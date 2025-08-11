"""Basic web scraping utilities for job listings.

Reads configuration from a YAML file describing the web sites to scrape and
returns a list of job dictionaries with the desired fields extracted using
CSS selectors.
"""

from __future__ import annotations

import re

import yaml
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Any


def _parse_salary(text: str) -> tuple[str, float]:
    """Return currency code and amount extracted from *text*."""
    if not text:
        return "", 0.0
    currency = ""
    if "R$" in text or "BRL" in text:
        currency = "BRL"
    elif "$" in text or "USD" in text:
        currency = "USD"
    match = re.search(r"(\d+[\.,]?\d*)", text)
    if not match:
        return currency, 0.0
    amount = float(match.group(1).replace(".", "").replace(",", "."))
    return currency, amount


def scrape_jobs(config_path: str | Path) -> List[Dict[str, Any]]:
    """Scrape job listings defined in *config_path*.

    The configuration must contain a ``sites`` list and may include ``skills``
    keywords as well as ``salary`` thresholds in USD or BRL.
    """
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    desired = [s.lower() for s in config.get("skills", [])]
    salary_cfg = config.get("salary", {})
    min_usd = salary_cfg.get("usd")
    min_brl = salary_cfg.get("brl")

    jobs: List[Dict[str, Any]] = []
    for site in config.get("sites", []):
        response = requests.get(site["url"], timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for elem in soup.select(site.get("job_selector", "")):
            job: Dict[str, Any] = {}
            for field, selector in site.get("fields", {}).items():
                target = elem.select_one(selector)
                job[field] = target.get_text(strip=True) if target else None

            haystack = " ".join(
                filter(None, [job.get("skills"), job.get("description"), job.get("title")])
            ).lower()
            if desired and not any(skill in haystack for skill in desired):
                continue

            cur, amount = _parse_salary(job.get("salary", ""))
            if (
                (cur == "USD" and min_usd and amount < min_usd)
                or (cur == "BRL" and min_brl and amount < min_brl)
            ):
                continue

            jobs.append(job)
    return jobs


if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="Scrape job listings")
    parser.add_argument("--config", default="../config/job_config.yaml")
    args = parser.parse_args()
    results = scrape_jobs(args.config)
    print(json.dumps(results, indent=2, ensure_ascii=False))

