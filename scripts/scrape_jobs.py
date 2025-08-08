"""Basic web scraping utilities for job listings.

Reads configuration from a YAML file describing the web sites to scrape and
returns a list of job dictionaries with the desired fields extracted using
CSS selectors.
"""

from __future__ import annotations

import yaml
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Any


def scrape_jobs(config_path: str | Path) -> List[Dict[str, Any]]:
    """Scrape job listings defined in *config_path*.

    The configuration must contain a ``sites`` list where each entry defines:

    ``url``
        Page to fetch.
    ``job_selector``
        CSS selector locating each job element on the page.
    ``fields``
        Mapping of field name to CSS selector relative to the job element.
    """
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

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
            jobs.append(job)
    return jobs


if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="Scrape job listings")
    parser.add_argument("--config", default="../config/job_config.yaml")
    args = parser.parse_args()
    results = scrape_jobs(args.config)
    print(json.dumps(results, indent=2, ensure_ascii=False))
