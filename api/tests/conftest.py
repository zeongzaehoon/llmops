"""Shared test setup for the infra-free api/ suite.

Sets a deterministic JWT secret BEFORE any `auth` import (auth/__init__.py reads
JWT_SECRET_KEY at module load), so token round-trip tests are reproducible
without touching real secrets or live infrastructure.
"""
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
