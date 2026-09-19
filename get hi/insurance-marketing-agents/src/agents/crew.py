"""
Multi-agent crew for Life Insurance (Pre-need / At-need) and Annuities
marketing data collection and report generation.
"""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.tools.data_tools import (
    get_product_context_tool,
    list_data_files_tool,
    load_data_tool,
    save_data_tool,
)
from src.tools.report_tools import list_reports_tool, save_report_tool


@CrewBase
class InsuranceMarketingCrew:
    """Crew that collects market data and produces marketing reports
    for Pre-need, At-need, and Annuity products.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ------------------------------------------------------------------
    # Agents
    # ------------------------------------------------------------------

    @agent
    def data_collector(self) -> Agent:
        return Agent(
            config=self.agents_config["data_collector"],  # type: ignore
            tools=[
                get_product_context_tool,
                save_data_tool,
                load_data_tool,
                list_data_files_tool,
            ],
            verbose=True,
        )

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["market_researcher"],  # type: ignore
            tools=[
                get_product_context_tool,
                save_data_tool,
                load_data_tool,
                list_data_files_tool,
            ],
            verbose=True,
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst"],  # type: ignore
            tools=[
                get_product_context_tool,
                load_data_tool,
                list_data_files_tool,
            ],
            verbose=True,
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["report_writer"],  # type: ignore
            tools=[
                save_report_tool,
                list_reports_tool,
                load_data_tool,
            ],
            verbose=True,
        )

    @agent
    def compliance_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["compliance_reviewer"],  # type: ignore
            tools=[load_data_tool],
            verbose=True,
        )

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    @task
    def collect_context_task(self) -> Task:
        return Task(
            config=self.tasks_config["collect_context_task"],  # type: ignore
            agent=self.data_collector(),
        )

    @task
    def research_market_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_market_task"],  # type: ignore
            agent=self.market_researcher(),
        )

    @task
    def analyze_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_data_task"],  # type: ignore
            agent=self.analyst(),
        )

    @task
    def write_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["write_report_task"],  # type: ignore
            agent=self.report_writer(),
        )

    @task
    def compliance_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["compliance_review_task"],  # type: ignore
            agent=self.compliance_reviewer(),
        )

    # ------------------------------------------------------------------
    # Crew
    # ------------------------------------------------------------------

    @crew
    def crew(self) -> Crew:
        """Creates the Insurance Marketing crew."""
        return Crew(
            agents=self.agents,  # automatically created by @agent decorator
            tasks=self.tasks,    # automatically created by @task decorator
            process=Process.sequential,
            verbose=True,
        )
