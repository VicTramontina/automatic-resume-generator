"""Utilities for building LaTeX resumes into PDF files."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any


LATEX_SRC = Path(__file__).resolve().parents[1] / "latex"


def prepare_job_directory(job_dir: Path) -> None:
    """Copy the LaTeX source tree into *job_dir*.

    The directory will contain a full copy of the ``latex`` folder so the
    generated resume can be compiled in isolation.
    """
    if job_dir.exists():
        shutil.rmtree(job_dir)
    shutil.copytree(LATEX_SRC, job_dir)


def write_job_summary(job: Dict[str, Any], job_dir: Path) -> None:
    """Create a markdown file summarising the job posting."""
    lines = [f"# {job.get('title', 'Job')}\n"]
    for key, value in job.items():
        if key == "title":
            continue
        lines.append(f"**{key.capitalize()}:** {value}\n")
    (job_dir / "job.md").write_text("\n".join(lines), encoding="utf-8")


def compile_pdf(job_dir: Path) -> None:
    """Compile ``resume.tex`` inside *job_dir* using ``pdflatex``."""
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "resume.tex"],
        cwd=job_dir,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
