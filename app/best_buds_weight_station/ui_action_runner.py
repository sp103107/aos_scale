"""Background dispatch helpers for PySide6 and Tk operator UIs.

Runs blocking device / run-install work off the UI thread; callbacks fire on the main thread.
"""
from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any


class InFlightGuard:
    """Ignore duplicate action clicks while work is running."""

    def __init__(self, debounce_s: float = 0.5):
        self._debounce_s = debounce_s
        self._in_flight: set[str] = set()
        self._last_started: dict[str, float] = {}

    def try_begin(self, action_key: str) -> bool:
        now = time.monotonic()
        if action_key in self._in_flight:
            return False
        last = self._last_started.get(action_key, 0.0)
        if now - last < self._debounce_s:
            return False
        self._in_flight.add(action_key)
        self._last_started[action_key] = now
        return True

    def end(self, action_key: str) -> None:
        self._in_flight.discard(action_key)

    def is_running(self, action_key: str) -> bool:
        return action_key in self._in_flight


def run_tk_background(
    root: Any,
    fn: Callable[[], Any],
    *,
    on_success: Callable[[Any], None],
    on_error: Callable[[Exception], None],
) -> None:
    def worker() -> None:
        try:
            result = fn()
        except Exception as exc:
            root.after(0, lambda: on_error(exc))
            return
        root.after(0, lambda: on_success(result))

    threading.Thread(target=worker, name="bbws-ui-action", daemon=True).start()


try:
    from PySide6.QtCore import QObject, QThread, Signal

    class _ActionWorker(QThread):
        finished_ok = Signal(object)
        finished_err = Signal(object)

        def __init__(self, fn: Callable[[], Any]):
            super().__init__()
            self._fn = fn

        def run(self) -> None:
            try:
                self.finished_ok.emit(self._fn())
            except Exception as exc:
                self.finished_err.emit(exc)

    class QtActionRunner(QObject):
        """Run a callable on a worker thread; signals return to the Qt main thread."""

        def run(
            self,
            fn: Callable[[], Any],
            *,
            on_success: Callable[[Any], None],
            on_error: Callable[[Exception], None],
        ) -> None:
            worker = _ActionWorker(fn)
            worker.finished_ok.connect(on_success)
            worker.finished_err.connect(on_error)
            worker.finished.connect(worker.deleteLater)
            worker.start()

except ImportError:
    QtActionRunner = None  # type: ignore[misc, assignment]
