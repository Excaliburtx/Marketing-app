# Architecture Overview

## Agent Flow (Sequential)

```
User Request
    │
    ▼
┌─────────────────────┐
│  Data Collector     │  → product context + KPI definitions
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Market Researcher  │  → trends, channels, competitive notes
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Analyst            │  → insights, opportunities, risks
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Report Writer      │  → structured Markdown report
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Compliance Reviewer│  → language check + final sign-off
└─────────────────────┘
    │
    ▼
  Saved Report (./reports/)
```

## Design Choices

- **CrewAI** chosen for rapid role-based prototyping. Easy to explain to non-engineers.
- **YAML configs** for agents and tasks so marketing/compliance people can adjust prompts without touching Python.
- **Local file tools** first – zero external dependencies beyond the LLM. Easy to replace with real CRM/rate APIs later.
- **Compliance agent** is deliberately last. It does not block the pipeline but forces a review step.

## Extending

1. Add new tools in `src/tools/` and attach them to the relevant agent in `crew.py`.
2. Add new agents by creating an `@agent` method and a corresponding entry in `agents.yaml` + a task.
3. For production branching, human approval, or long-running state → migrate the orchestration layer to LangGraph while keeping the same agent prompts and tools.
