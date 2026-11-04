"""Exceptions raised by the PEC core. Every one derives from `PecError`."""


class PecError(Exception):
    """Base class for all PEC errors."""


class UnitError(PecError, ValueError):
    """Unknown or unsupported unit."""
