"""End-to-end pipeline for generating tailored resumes."""

from __future__ import annotations

from pathlib import Path

from scrape_jobs import scrape_jobs
from gemini_api import tailor_resume
from build_resume import prepare_job_directory, write_job_summary, compile_pdf

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "job_config.yaml"
OUTPUT_ROOT = Path(__file__).resolve().parents[1] / "outputs"


def generate_resumes(config_path: Path = CONFIG_PATH, output_root: Path = OUTPUT_ROOT) -> None:
    jobs = scrape_jobs(config_path)
    output_root.mkdir(exist_ok=True)

    for idx, job in enumerate(jobs, 1):
        job_dir = output_root / f"job_{idx}"
        prepare_job_directory(job_dir)
        write_job_summary(job, job_dir)
        tailored = tailor_resume(job, job_dir / "resume.tex")
        (job_dir / "resume.tex").write_text(tailored, encoding="utf-8")
        compile_pdf(job_dir)


if __name__ == "__main__":
    generate_resumes()
