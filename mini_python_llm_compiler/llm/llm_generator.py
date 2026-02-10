"""LLM wrapper for generating Python code from natural language prompts."""
from __future__ import annotations
import os
from typing import Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled gracefully when dependency missing
    OpenAI = None


SYSTEM_PROMPT = (
    "You are a helpful assistant that writes short Python 3 code using only "
    "variables, arithmetic, print, and simple if/else. Do not include imports."
)


class LLMGenerator:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key or os.getenv("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")
        self.model = model
        self.client = None
        if OpenAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def generate_code(self, prompt: str) -> str:
        if self.client:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        # Fallback deterministic generator for offline use
        return self._fallback(prompt)

    def _fallback(self, prompt: str) -> str:
        # Very small heuristic to make the project runnable without an API key
        if "hello" in prompt.lower():
            return "print(\"Hello from the offline generator!\")"
        if "sum" in prompt.lower():
            return "x = 2\ny = 3\nprint(x + y)"
        return (
            "x = 5\n"
            "y = x + 2\n"
            "if y > 5:\n"
            "    print(\"Value is big\")\n"
            "else:\n"
            "    print(\"Value is small\")\n"
        )


def generate_code(prompt: str) -> str:
    generator = LLMGenerator()
    return generator.generate_code(prompt)
