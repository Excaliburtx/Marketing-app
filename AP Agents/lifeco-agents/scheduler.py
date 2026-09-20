"""Always-on scheduler for a server / VM / container:  python scheduler.py
(If you only use GitHub Actions for scheduling, you don't need this file.)"""
from apscheduler.schedulers.blocking import BlockingScheduler

from agents.orchestrator import run_job

s = BlockingScheduler(timezone="America/Los_Angeles")
s.add_job(lambda: run_job("collect"), "interval", hours=1, id="collect")
s.add_job(lambda: run_job("review"), "interval", minutes=15, id="review")
s.add_job(lambda: run_job("report"), "cron", hour=7, minute=0, id="report")
s.add_job(lambda: run_job("intel"), "cron", hour=6, minute=30, id="intel")

if __name__ == "__main__":
    print("Agent team running. Ctrl+C to stop.")
    run_job("all")  # warm start
    s.start()
