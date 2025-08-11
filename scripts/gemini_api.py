"""Interface with the Google Gemini API.

The actual API key must be supplied in the environment variable
``GEMINI_API_KEY``.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, Any

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted


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
    print(f"🤖 Starting resume tailoring for job: {job.get('title', 'Unknown')}")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    print("🔑 Configuring Gemini API...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    print("📄 Reading base resume template...")
    base_resume = Path(base_resume).read_text(encoding="utf-8")
    job_desc = job.get("description", "")

    print(f"📝 Job description length: {len(job_desc)} characters")
    print(f"📝 Base resume length: {len(base_resume)} characters")

    prompt = (
        "You are an assistant that customizes LaTeX resumes. Given the job "
        "description and the base resume, rewrite the resume so that it "
        "highlights the most relevant skills and experience for the job. "
        "IMPORTANT FORMATTING RULES:\n"
        "- Keep the EXACT structure and formatting of the original resume\n"
        "- Do NOT add extra blank lines or indentation\n"
        "- Do NOT reformat the LaTeX spacing\n"
        "- Only modify the CONTENT within sections, not the structure\n"
        "- Preserve the exact line breaks and spacing from the original\n"
        "- Focus ONLY on tailoring the content to match the job requirements\n"
        "Return only valid LaTeX code with the original formatting preserved.\n\n"
        f"Job description:\n{job_desc}\n\n"
        f"Base resume:\n{base_resume}\n"
    )

    print(f"📤 Sending prompt to Gemini API (length: {len(prompt)} characters)...")

    # Retry logic for rate limiting
    max_retries = 3
    base_delay = 60  # Start with 60 seconds delay

    for attempt in range(max_retries):
        try:
            print(f"🔄 API call attempt {attempt + 1}/{max_retries}...")
            response = model.generate_content(prompt)
            print(f"✅ Successfully received response from Gemini API (length: {len(response.text)} characters)")
            return response.text
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                # Extract retry delay from error if available, otherwise use exponential backoff
                retry_delay = base_delay * (2 ** attempt)
                print(f"⚠️ Rate limit exceeded. Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print("❌ Max retries exceeded. Please wait before running again or consider upgrading your API plan.")
                raise
