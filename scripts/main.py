"""End-to-end pipeline for generating tailored resumes."""

from __future__ import annotations

import time
from pathlib import Path

from scrape_jobs import scrape_jobs
from gemini_api import tailor_resume
from build_resume import prepare_job_directory, write_job_summary, compile_pdf

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "job_config.yaml"
OUTPUT_ROOT = Path(__file__).resolve().parents[1] / "outputs"


def generate_resumes(config_path: Path = CONFIG_PATH, output_root: Path = OUTPUT_ROOT) -> None:
    print("🚀 Starting resume generation pipeline...")
    print(f"📂 Config file: {config_path}")
    print(f"📂 Output directory: {output_root}")

    start_time = time.time()

    print("\n" + "="*60)
    print("📡 PHASE 1: JOB SCRAPING")
    print("="*60)

    jobs = scrape_jobs(config_path)
    print(f"\n✅ Job scraping completed! Found {len(jobs)} jobs to process")

    if not jobs:
        print("⚠️ No jobs found. Exiting...")
        return

    print(f"\n📂 Creating output directory: {output_root}")
    output_root.mkdir(exist_ok=True)

    print("\n" + "="*60)
    print("🎯 PHASE 2: RESUME GENERATION")
    print("="*60)

    for idx, job in enumerate(jobs, 1):
        print(f"\n🔄 Processing job {idx}/{len(jobs)}: {job.get('title', 'Unknown')}")
        print(f"🏢 Company: {job.get('company', 'Unknown')}")
        print(f"📍 Location: {job.get('location', 'Unknown')}")

        job_start_time = time.time()
        job_dir = output_root / f"job_{idx}"

        # Step 1: Prepare directory
        print(f"\n📁 Step 1/5: Preparing job directory...")
        prepare_job_directory(job_dir)

        # Step 2: Write job summary
        print(f"📝 Step 2/5: Writing job summary...")
        write_job_summary(job, job_dir)

        # Step 3: Tailor resume with AI
        print(f"🤖 Step 3/5: Tailoring resume with AI...")
        tailored = tailor_resume(job, job_dir / "resume.tex")

        # Step 4: Save tailored resume
        print(f"💾 Step 4/5: Saving tailored resume...")
        tailored_file = job_dir / "resume.tex"
        tailored_file.write_text(tailored, encoding="utf-8")
        print(f"💾 Tailored resume saved to: {tailored_file}")

        # Step 5: Compile PDF
        print(f"🔧 Step 5/5: Compiling PDF...")
        compile_pdf(job_dir)

        job_duration = time.time() - job_start_time
        print(f"✅ Job {idx} completed in {job_duration:.2f} seconds")

        # Add a small delay between jobs to respect API limits
        if idx < len(jobs):
            print("⏳ Waiting 5 seconds before next job...")
            time.sleep(5)

    total_duration = time.time() - start_time
    print("\n" + "="*60)
    print("🎉 PIPELINE COMPLETED!")
    print("="*60)
    print(f"📊 Total jobs processed: {len(jobs)}")
    print(f"⏱️ Total time: {total_duration:.2f} seconds")
    print(f"📂 Output location: {output_root}")
    print("="*60)


if __name__ == "__main__":
    generate_resumes()
