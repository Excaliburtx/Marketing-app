"""Tools for data collection and market research."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from crewai.tools import tool
from rich.console import Console

from src.config.settings import settings

console = Console()


@tool("Save structured data to local storage")
def save_data_tool(filename: str, content: str, subfolder: str = "raw") -> str:
    """
    Save text or JSON content to the data directory.
    Use this to persist collected market data, competitor info, or intermediate results.
    """
    target_dir = settings.data_dir / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)

    # Auto-append timestamp if not present
    if not any(c.isdigit() for c in filename[:8]):
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        name, ext = Path(filename).stem, Path(filename).suffix or ".txt"
        filename = f"{name}_{stamp}{ext}"

    path = target_dir / filename
    path.write_text(content, encoding="utf-8")
    return f"Saved to {path}"


@tool("Load previously saved data file")
def load_data_tool(filename: str, subfolder: str = "raw") -> str:
    """Load a file from the data directory by name."""
    path = settings.data_dir / subfolder / filename
    if not path.exists():
        # Try searching
        matches = list((settings.data_dir / subfolder).glob(f"*{filename}*"))
        if matches:
            path = matches[0]
        else:
            return f"File not found: {filename}"
    return path.read_text(encoding="utf-8")


@tool("List available data files")
def list_data_files_tool(subfolder: str = "raw") -> str:
    """List files currently stored in the data directory."""
    target = settings.data_dir / subfolder
    if not target.exists():
        return "No data directory found yet."
    files = sorted(target.glob("*"))
    if not files:
        return "No files found."
    return "\n".join(f"- {f.name} ({f.stat().st_size} bytes)" for f in files)


@tool("Get current product line focus")
def get_product_context_tool() -> str:
    """Return the supported product lines and basic definitions for context."""
    context = {
        "product_lines": settings.product_lines,
        "definitions": {
            "pre-need": (
                "Life insurance or annuity products purchased in advance to fund "
                "funeral and burial expenses. Often sold through funeral homes."
            ),
            "at-need": (
                "Insurance or final-expense products and services arranged after a death "
                "has occurred. High urgency, short sales cycle."
            ),
            "annuities": (
                "Insurance contracts that provide guaranteed income streams, typically "
                "for retirement. Includes fixed, fixed-indexed, variable, and immediate annuities."
            ),
        },
        "key_marketing_metrics": [
            "New annualized premium (NAP)",
            "Face amount / case count",
            "Average issue age",
            "Distribution channel mix (career agents, independent, banks, funeral homes)",
            "Lapse / surrender rates",
            "Competitor rate competitiveness (MYGA, FIAs)",
            "Lead source ROI and conversion rates",
        ],
    }
    return json.dumps(context, indent=2)
