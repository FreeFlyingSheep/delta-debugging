"""Outcome for delta debugging."""

import logging
from enum import StrEnum


logger: logging.Logger = logging.getLogger(__name__)


class Outcome(StrEnum):
    """Outcome of a test."""

    PASS = "pass"
    """Test passed. The configuration does not induce the failure."""
    FAIL = "fail"
    """Test failed. The configuration induces the failure."""
    UNRESOLVED = "unresolved"
    """Test result is unresolved. The result is unexpected, which is considered as not inducing the failure."""
