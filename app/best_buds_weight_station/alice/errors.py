from __future__ import annotations


class AliceError(Exception):
    """Base class for operator-facing Alice errors."""


class AuthorityViolation(AliceError):
    """Raised when a requested action exceeds Alice's authority."""


class IncompleteContext(AliceError):
    """Raised when required command context is absent."""


class InvalidCommitReceipt(AliceError):
    """Raised when a backend result cannot prove authoritative local commit."""
