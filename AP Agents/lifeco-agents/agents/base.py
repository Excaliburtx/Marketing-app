"""Every agent inherits from this. Handles timing, error capture and logging to the dashboard."""
import traceback
from datetime import datetime

from core.db import log_run


class BaseAgent:
    name = "base"
    role = ""

    def run(self) -> str:
        """Do the work; return a one-line summary."""
        raise NotImplementedError

    def execute(self) -> dict:
        started = datetime.now()
        try:
            summary = self.run()
            status = "success"
        except Exception as e:
            summary = f"{type(e).__name__}: {e}"
            status = "failed"
            print(traceback.format_exc())
        log_run(self.name, status, summary, started, datetime.now())
        print(f"[{self.name}] {status}: {summary}")
        return {"agent": self.name, "status": status, "summary": summary}
