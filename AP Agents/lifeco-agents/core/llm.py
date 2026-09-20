"""Thin Claude wrapper. If no API key is set, agents fall back to rule-based output so the app still runs."""
import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")


def llm_available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def ask_claude(system: str, prompt: str, max_tokens: int = 1500, web_search: bool = False) -> str | None:
    """Returns text, or None if no key / error (callers must handle the fallback)."""
    if not llm_available():
        return None
    try:
        import anthropic
        client = anthropic.Anthropic()
        kwargs = {}
        if web_search:
            kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]
        resp = client.messages.create(
            model=MODEL, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}], **kwargs,
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip() or None
    except Exception as e:  # never let an LLM failure kill the pipeline
        print(f"[llm] error: {e}")
        return None
