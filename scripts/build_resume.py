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
    print(f"📁 Preparing job directory: {job_dir}")
    if job_dir.exists():
        print(f"🗑️ Removing existing directory: {job_dir}")
        shutil.rmtree(job_dir)
    print(f"📋 Copying LaTeX source from {LATEX_SRC} to {job_dir}")
    shutil.copytree(LATEX_SRC, job_dir)
    print(f"✅ Job directory prepared successfully")


def write_job_summary(job: Dict[str, Any], job_dir: Path) -> None:
    """Create a markdown file summarising the job posting."""
    print(f"📝 Writing job summary to {job_dir / 'job.md'}")
    lines = [f"# {job.get('title', 'Job')}\n"]
    for key, value in job.items():
        if key == "title":
            continue
        lines.append(f"**{key.capitalize()}:** {value}\n")
    (job_dir / "job.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Job summary written ({len(lines)} lines)")


def compile_pdf(job_dir: Path) -> None:
    """Compile ``resume.tex`` inside *job_dir* using ``xelatex`` and ``biber``."""
    print(f"🔧 Starting PDF compilation in {job_dir}")

    try:
        # First XeLaTeX run
        print("📄 Running first XeLaTeX compilation...")
        result1 = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "resume.tex"],
            cwd=job_dir,
            check=False,  # Don't fail on warnings
            capture_output=True,
            text=True,
        )
        print(f"📄 First XeLaTeX run completed (exit code: {result1.returncode})")

        # Run Biber for bibliography processing
        print("📚 Running Biber for bibliography processing...")
        biber_result = subprocess.run(
            ["biber", "resume"],
            cwd=job_dir,
            check=False,  # Don't fail if no bibliography
            capture_output=True,
            text=True,
        )
        print(f"📚 Biber run completed (exit code: {biber_result.returncode})")

        # Second XeLaTeX run to resolve references
        print("📄 Running second XeLaTeX compilation...")
        result2 = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "resume.tex"],
            cwd=job_dir,
            check=False,  # Don't fail on warnings
            capture_output=True,
            text=True,
        )
        print(f"📄 Second XeLaTeX run completed (exit code: {result2.returncode})")

        # Check if PDF was actually created
        pdf_file = job_dir / "resume.pdf"
        if pdf_file.exists():
            pdf_size = pdf_file.stat().st_size
            print(f"✅ PDF compilation successful! Generated file: {pdf_file} ({pdf_size} bytes)")
        else:
            print("❌ PDF compilation failed - no PDF file generated")
            print("📋 XeLaTeX output from final run:")
            print(result2.stdout)
            if result2.stderr:
                print("📋 XeLaTeX stderr:")
                print(result2.stderr)
            raise subprocess.CalledProcessError(result2.returncode, result2.args)

    except subprocess.CalledProcessError as e:
        print(f"❌ LaTeX compilation failed with return code {e.returncode}")
        print("📋 LaTeX output:")
        print(e.stdout)
        if e.stderr:
            print("📋 LaTeX stderr:")
            print(e.stderr)
        raise
