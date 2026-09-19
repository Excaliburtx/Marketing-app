"""Tools for generating and saving marketing reports."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from crewai.tools import tool

from src.config.settings import settings


@tool("Save marketing report")
def save_report_tool(title: str, content: str, product_line: str = "general") -> str:
    """
    Save a finished marketing report as a Markdown file.
    product_line should be one of: pre-need, at-need, annuities, or general.
    """
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)
    safe_title = safe_title.strip().replace(" ", "_")[:60]
    filename = f"{product_line}_{safe_title}_{stamp}.md"
    path = settings.reports_dir / filename

    header = f"""# {title}

**Product Line:** {product_line}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**System:** Insurance Marketing Agents  

---

"""
    path.write_text(header + content, encoding="utf-8")
    return f"Report saved to {path}"


@tool("List existing reports")
def list_reports_tool() -> str:
    """List previously generated marketing reports."""
    if not settings.reports_dir.exists():
        return "No reports directory yet."
    files = sorted(settings.reports_dir.glob("*.md"), reverse=True)
    if not files:
        return "No reports found."
    return "\n".join(f"- {f.name}" for f in files[:20])
