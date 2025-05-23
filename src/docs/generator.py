"""Utilities for generating project documentation."""
from __future__ import annotations

from typing import List

try:  # pragma: no cover - optional dependency
    from sphinx.cmd.build import main as sphinx_build
except Exception:  # pragma: no cover - handle missing dependency
    sphinx_build = None


class DocumentationGenerator:
    """Generate API and hardware documentation."""

    def generate_api_docs(self) -> None:
        if sphinx_build is None:
            raise RuntimeError("Sphinx is required to generate documentation")
        sphinx_build([
            "-b",
            "html",
            "-d",
            "docs/_build/doctrees",
            "docs",
            "docs/_build/html",
        ])

    def generate_hardware_guide(self, sensors: List[str]) -> None:
        """Placeholder for interactive hardware guide generation."""
        for sensor in sensors:
            # Implementation would build docs per sensor
            pass
