"""CLI entry point (used by GitHub Actions and cron):  python run_agents.py --job collect"""
import argparse

from agents.orchestrator import JOBS, run_job

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--job", choices=JOBS.keys(), default="all")
    for r in run_job(p.parse_args().job):
        print(r)
