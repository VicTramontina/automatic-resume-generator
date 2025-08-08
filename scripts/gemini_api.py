"""Interface with the Google Gemini API.

The actual API key must be supplied in the environment variable
``GEMINI_API_KEY``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

import google.generativeai as genai


def tailor_resume(job: Dict[str, Any], base_resume: str | Path) -> str:
    """Return a resume tailored to *job*.

    Parameters
    ----------
    job:
        Dictionary with information about the job opening. The ``description``
        field is particularly important.
    base_resume:
        Path to the base LaTeX resume used as a starting point.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    base_resume = Path(base_resume).read_text(encoding="utf-8")
    job_desc = job.get("description", "")
    prompt = (
        "You are an assistant that customizes LaTeX resumes. Given the job "
        "description and the base resume, rewrite the resume so that it "
        "highlights the most relevant skills and experience for the job. "
        "Return only valid LaTeX code.\n\n"
        f"Job description:\n{job_desc}\n\n"
        f"Base resume:\n{base_resume}\n"
    )
    response = model.generate_content(prompt)
    return response.text
