from __future__ import annotations
from enum import Enum
from typing import Any

from .models import CaptureCommand, StabilityProfile
from .stability import StabilityDetector
from .storage import CommitStepError, DuplicateCommitError, SessionStore


class State(str, Enum):
    NO_RUN = 'NO_RUN'
    RUN_SETUP = 'RUN_SETUP'
    RUN_READY = 'RUN_READY'
    DEVICE_CONNECTING = 'DEVICE_CONNECTING'
    DISCONNECTED = 'DISCONNECTED'
    DEVICE_READY = 'DEVICE_READY'
    SESSION_SETUP = 'SESSION_SETUP'
    SESSION_READY = 'SESSION_READY'
    WAITING_FOR_BARCODE = 'WAITING_FOR_BARCODE'
    BARCODE_CAPTURED = 'BARCODE_CAPTURED'
    WAITING_FOR_LOAD = 'WAITING_FOR_LOAD'
    WEIGHING = 'WEIGHING'
    WAITING_FOR_STABLE_WEIGHT = 'WAITING_FOR_STABLE_WEIGHT'
    WEIGHT_STABLE = 'WEIGHT_STABLE'
    AUTO_RECORD = 'AUTO_RECORD'
    MANUAL_CONFIRM = 'MANUAL_CONFIRM'
    LOCAL_COMMIT_PENDING = 'LOCAL_COMMIT_PENDING'
    ALICE_RECEIPT_VALIDATION = 'ALICE_RECEIPT_VALIDATION'
    RECORD_SAVED = 'RECORD_SAVED'
    RECOVERY_REQUIRED = 'RECOVERY_REQUIRED'
    BLOCKED = 'BLOCKED'
    ERROR = 'ERROR'
    RUN_FINISHED = 'RUN_FINISHED'


_REQUIRED_RECEIPT_FIELDS = (
    'receipt_id', 'record_id', 'jsonl_event_id', 'individual_record_path',
    'checkpoint_version', 'record_hash',
)


class CaptureMachine:
    """Backend capture state machine.

    Persistence is authoritative here, but operator success feedback is not. A
    successful commit leaves the machine in ``RECORD_SAVED`` until the caller
    passes the terminal result through Alice and explicitly completes the
    terminal-feedback gate with :meth:`complete_terminal_result`.
    """

    def __init__(self, store: SessionStore, profile: StabilityProfile | None = None, beep=None):
        self.store = store
        self.profile = profile or StabilityProfile()
        self.detector = StabilityDetector(self.profile)
        self.beep = beep or (lambda kind: None)
        self.state = State.DISCONNECTED
        self.barcode = None
        self.mode = 'automatic'
        self.stable = None
        self.last_receipt = None
        self.last_error = None
        self.last_duplicate = None
        self.capture_idempotency_key = None

    def connect(self):
        self.state = State.RECOVERY_REQUIRED if self.store.recovery_required else State.DEVICE_READY

    def disconnect(self):
        self.state = State.DISCONNECTED
        self._clear_capture()
        self.detector.reset()
        self.beep('disconnect')

    def start_session(self, mode='automatic'):
        if self.state == State.RECOVERY_REQUIRED:
            raise RuntimeError('recovery required')
        if self.state != State.DEVICE_READY:
            raise RuntimeError('device not ready')
        if mode not in ('automatic', 'manual'):
            raise ValueError('invalid mode')
        self.mode = mode
        self.state = State.SESSION_READY
        self.state = State.WAITING_FOR_BARCODE

    def scan(self, barcode):
        if self.state != State.WAITING_FOR_BARCODE:
            raise RuntimeError('not waiting for barcode')
        if not barcode.strip():
            raise ValueError('barcode required')
        self.barcode = barcode
        self.capture_idempotency_key = f'{self.store.context.session_id}:{self.store.sequence + 1}:{barcode}'
        self.detector.reset()
        self.state = State.BARCODE_CAPTURED
        self.state = State.WAITING_FOR_STABLE_WEIGHT

    def reading(self, weight_g, raw=None, ready=True):
        if self.state != State.WAITING_FOR_STABLE_WEIGHT:
            return None
        result = self.detector.add(weight_g, ready)
        if not result.stable:
            return result
        self.stable = result
        self.state = State.WEIGHT_STABLE
        if self.mode == 'automatic':
            self.state = State.AUTO_RECORD
            return self._commit(raw)
        self.state = State.MANUAL_CONFIRM
        return result

    def confirm(self, raw=None, *, operator_note=None, void_status='none'):
        if self.state != State.MANUAL_CONFIRM:
            raise RuntimeError('not awaiting confirmation')
        return self._commit(raw, operator_note=operator_note, void_status=void_status)

    def _commit(self, raw, *, operator_note=None, void_status='none'):
        self.state = State.LOCAL_COMMIT_PENDING
        try:
            record, receipt = self.store.commit(
                CaptureCommand(
                    self.barcode,
                    self.stable.weight_g,
                    self.stable.sample_count,
                    {'spread_g': self.stable.spread_g, 'stddev_g': self.stable.stddev_g},
                    self.mode,
                    raw_adc_value=raw,
                    operator_note=operator_note,
                    void_status=void_status or 'none',
                    idempotency_key=self.capture_idempotency_key,
                )
            )
        except DuplicateCommitError as exc:
            self.last_duplicate = exc.to_result()
            self.last_error = None
            if self._valid_duplicate_result(self.last_duplicate):
                self.state = State.RECORD_SAVED
            else:
                self.state = State.LOCAL_COMMIT_PENDING
            return self.last_duplicate
        except CommitStepError as exc:
            self.last_error = exc.to_result()
            self.state = State.RECOVERY_REQUIRED if exc.jsonl_event_id else State.ERROR
            self.beep('error')
            raise
        except Exception:
            self.state = State.ERROR
            self.beep('error')
            raise

        receipt_dict = receipt.to_dict()
        if not self._valid_local_commit_receipt(receipt_dict):
            self.state = State.ERROR
            self.beep('error')
            raise RuntimeError('invalid local commit receipt')

        self.last_receipt = receipt
        self.last_error = None
        self.state = State.RECORD_SAVED
        # No success feedback or progression here. Alice must validate the
        # terminal result first and the controller must call
        # complete_terminal_result().
        return record, receipt

    def complete_terminal_result(self, feedback_kind: str = 'success') -> None:
        """Complete operator feedback only after Alice validates the result."""
        if self.state != State.RECORD_SAVED:
            raise RuntimeError('terminal result is not ready for completion')
        if feedback_kind not in {'success', 'warning'}:
            raise ValueError('invalid terminal feedback kind')
        self.beep(feedback_kind)
        self._clear_capture()
        self.state = State.WAITING_FOR_BARCODE

    def cancel_capture(self) -> None:
        if self.state not in {
            State.BARCODE_CAPTURED,
            State.WAITING_FOR_STABLE_WEIGHT,
            State.WEIGHT_STABLE,
            State.MANUAL_CONFIRM,
            State.AUTO_RECORD,
        }:
            raise RuntimeError('no cancellable capture is active')
        self._clear_capture()
        self.detector.reset()
        self.state = State.WAITING_FOR_BARCODE

    def recover(self):
        if self.state != State.RECOVERY_REQUIRED:
            raise RuntimeError('recovery not required')
        receipt = self.store.recover_from_ledger()
        self.state = State.SESSION_READY
        return receipt

    def _clear_capture(self) -> None:
        self.barcode = None
        self.stable = None
        self.capture_idempotency_key = None

    @staticmethod
    def _valid_local_commit_receipt(receipt: dict[str, Any]) -> bool:
        return (
            receipt.get('status') == 'committed'
            and receipt.get('local_commit') is True
            and all(receipt.get(field) not in (None, '') for field in _REQUIRED_RECEIPT_FIELDS)
        )

    @staticmethod
    def _valid_duplicate_result(result: dict[str, Any]) -> bool:
        return (
            result.get('status') == 'duplicate'
            and result.get('record_id') not in (None, '')
            and result.get('original_receipt_id') not in (None, '')
        )
