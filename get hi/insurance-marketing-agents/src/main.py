#!/usr/bin/env python3
"""
Insurance Marketing Agents
CLI entry point for running Pre-need / At-need / Annuity marketing crews.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import typer
from rich.console import Console
from rich.panel import Panel

from src.agents.crew import InsuranceMarketingCrew
from src.config.settings import settings

app = typer.Typer(help="AI agents for Life Insurance (Pre-need/At-need) & Annuities marketing reports")
console = Console()


@app.command()
def run(
    product_line: str = typer.Option(
        "annuities",
        "--product",
        "-p",
        help="Product line: pre-need | at-need | annuities | all",
    ),
    request: str = typer.Option(
        "Produce a current market overview and marketing opportunity report.",
        "--request",
        "-r",
        help="What you want the agents to focus on",
    ),
):
    """Run the full multi-agent marketing crew."""
    console.print(
        Panel.fit(
            f"[bold]Insurance Marketing Agents[/bold]\n"
            f"Product line: [cyan]{product_line}[/cyan]\n"
            f"Request: {request}",
            title="Starting Crew",
        )
    )

    # Ensure dirs exist
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)

    inputs = {
        "product_line": product_line,
        "user_request": request,
    }

    crew = InsuranceMarketingCrew().crew()
    result = crew.kickoff(inputs=inputs)

    console.print("\n[bold green]Crew finished.[/bold green]")
    console.print(Panel(str(result), title="Final Output", expand=False))


@app.command()
def list_reports():
    """List previously generated reports."""
    reports = sorted(settings.reports_dir.glob("*.md"), reverse=True)
    if not reports:
        console.print("[yellow]No reports found yet.[/yellow]")
        return
    console.print("[bold]Existing reports:[/bold]")
    for r in reports[:20]:
        console.print(f"  • {r.name}")


@app.command()
def info():
    """Show system info and supported product lines."""
    console.print(
        Panel.fit(
            f"Supported product lines: {', '.join(settings.product_lines)}\n"
            f"Data dir: {settings.data_dir.resolve()}\n"
            f"Reports dir: {settings.reports_dir.resolve()}\n"
            f"Default model: {settings.default_model}",
            title="System Info",
        )
    )


if __name__ == "__main__":
    app()
