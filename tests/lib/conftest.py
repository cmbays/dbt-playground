"""Pytest configuration for scripts/lib module tests.

Provides shared fixtures for observability and API validation testing.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root_dir(tmp_path: Path, monkeypatch) -> Path:
    """Create a temp directory simulating project root."""
    # Create CLAUDE.md to simulate project root detection
    (tmp_path / 'CLAUDE.md').write_text('# Test Project')

    # Create necessary directories
    (tmp_path / 'temp').mkdir()
    (tmp_path / 'temp' / 'traces').mkdir()
    (tmp_path / 'temp' / 'metrics').mkdir()
    (tmp_path / 'memory').mkdir()

    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    return tmp_path
