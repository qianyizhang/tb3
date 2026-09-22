"""User-facing workbench errors, shared across service boundaries."""


class MedicalError(ValueError):
    """An invalid operation, record or workspace input."""
