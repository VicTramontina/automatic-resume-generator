"""Enhanced web scraping utilities for job listings.

Reads configuration from a YAML file describing the web sites to scrape and
returns a list of job dictionaries with the desired fields extracted using
CSS selectors. Supports individual job page extraction, pagination, and infinite scroll.
"""

from __future__ import annotations

import re
import time
from urllib.parse import urljoin, urlparse

import yaml
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Any, Optional

# Selenium imports for infinite scroll
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


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


def _get_page_content(url: str, headers: Optional[Dict[str, str]] = None) -> BeautifulSoup:
    """Get and parse page content with error handling."""
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if headers:
        default_headers.update(headers)

    response = requests.get(url, headers=default_headers, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def _extract_job_data(soup: BeautifulSoup, fields: Dict[str, str], base_url: str = "") -> Dict[str, Any]:
    """Extract job data from a soup object using field selectors."""
    job: Dict[str, Any] = {}
    for field, selector in fields.items():
        target = soup.select_one(selector)
        if target:
            if field == "link" and target.get("href"):
                # Handle relative URLs
                job[field] = urljoin(base_url, target.get("href"))
            else:
                job[field] = target.get_text(strip=True)
        else:
            job[field] = None
    return job


def _scrape_individual_job(job_url: str, detail_fields: Dict[str, str]) -> Dict[str, Any]:
    """Scrape detailed information from an individual job page."""
    try:
        soup = _get_page_content(job_url)
        return _extract_job_data(soup, detail_fields, job_url)
    except Exception as e:
        print(f"Error scraping job details from {job_url}: {e}")
        return {}


def _check_skills_match(job_text: str, skills_config: List[Any]) -> bool:
    """Check if job matches skill requirements based on configuration."""
    job_text_lower = job_text.lower()

    for skill_entry in skills_config:
        if isinstance(skill_entry, str):
            # Old format: just a string (optional skill)
            if skill_entry.lower() in job_text_lower:
                return True
        elif isinstance(skill_entry, dict):
            # New format: dict with skill and required flag
            skill_name = skill_entry.get("name", "").lower()
            is_required = skill_entry.get("required", False)

            skill_found = skill_name in job_text_lower

            if is_required and not skill_found:
                # Required skill not found, job doesn't match
                return False
            elif not is_required and skill_found:
                # Optional skill found, job matches
                return True

    # If we have any required skills, at least one must be found
    has_required_skills = any(
        isinstance(skill, dict) and skill.get("required", False)
        for skill in skills_config
    )

    if has_required_skills:
        # Check if at least one required skill was found
        for skill_entry in skills_config:
            if isinstance(skill_entry, dict) and skill_entry.get("required", False):
                if skill_entry.get("name", "").lower() in job_text_lower:
                    return True
        return False

    # If no required skills and no optional skills found, check old format
    return any(
        isinstance(skill, str) and skill.lower() in job_text_lower
        for skill in skills_config
    )


def _get_next_page_url(soup: BeautifulSoup, base_url: str, pagination_config: Dict[str, Any]) -> Optional[str]:
    """Get the next page URL based on pagination configuration."""
    if pagination_config.get("type") == "next_button":
        next_selector = pagination_config.get("next_selector", "")
        next_link = soup.select_one(next_selector)
        if next_link and next_link.get("href"):
            return urljoin(base_url, next_link.get("href"))

    elif pagination_config.get("type") == "numbered_links":
        # For numbered links, we need to track current page and get next
        links_selector = pagination_config.get("links_selector", "")
        page_links = soup.select(links_selector)

        # Find current active page and get next one
        for i, link in enumerate(page_links):
            if link.get("aria-current") == "page" or "current" in link.get("class", []):
                # Found current page, return next if exists
                if i + 1 < len(page_links):
                    next_link = page_links[i + 1]
                    if next_link.get("href"):
                        return urljoin(base_url, next_link.get("href"))
                break

    return None


def _setup_selenium_driver() -> Optional[webdriver.Chrome]:
    """Setup Chrome driver for infinite scroll support."""
    if not SELENIUM_AVAILABLE:
        print("Selenium not available. Install with: pip install selenium webdriver-manager")
        return None

    try:
        print("Setting up Chrome driver for Docker environment...")

        # Check if Chrome and ChromeDriver are available
        import subprocess
        try:
            chrome_version = subprocess.run(["/usr/bin/google-chrome", "--version"],
                                          capture_output=True, text=True, check=True)
            print(f"Chrome version: {chrome_version.stdout.strip()}")
        except Exception as e:
            print(f"Chrome binary not found: {e}")
            return None

        try:
            driver_version = subprocess.run(["/usr/local/bin/chromedriver", "--version"],
                                          capture_output=True, text=True, check=True)
            print(f"ChromeDriver version: {driver_version.stdout.strip()}")
        except Exception as e:
            print(f"ChromeDriver binary not found: {e}")
            return None

        options = Options()
        options.add_argument("--headless=new")  # Use new headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI,VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--mute-audio")
        options.add_argument("--no-first-run")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--disable-crash-reporter")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-permissions-api")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Simplified Docker-specific options
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--force-color-profile=srgb")
        options.add_argument("--memory-pressure-off")
        options.add_argument("--no-zygote")  # Important for Docker

        # Use system Google Chrome binary
        options.binary_location = "/usr/bin/google-chrome"

        # Use system chromedriver
        service = Service("/usr/local/bin/chromedriver")

        print("Attempting to create Chrome driver instance...")
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome driver successfully created!")
        return driver
    except Exception as e:
        print(f"Failed to setup Chrome driver: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None


def _scrape_with_infinite_scroll(site: Dict[str, Any], max_jobs: int) -> List[Dict[str, Any]]:
    """Scrape jobs from a site that uses infinite scroll (like LinkedIn)."""
    if not SELENIUM_AVAILABLE:
        print("Selenium not available for infinite scroll. Falling back to regular scraping.")
        return []

    driver = _setup_selenium_driver()
    if not driver:
        return []

    try:
        url = site["url"]
        print(f"Loading {url} with Selenium for infinite scroll...")
        driver.get(url)

        # Wait for initial content to load
        time.sleep(3)

        jobs = []
        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = site.get("max_scrolls", 10)

        while len(jobs) < max_jobs and scroll_attempts < max_scroll_attempts:
            # Get current page content
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_elements = soup.select(site.get("job_selector", ""))

            print(f"Scroll {scroll_attempts + 1}: Found {len(job_elements)} total job listings")

            # Process new jobs (skip already processed ones)
            for i, elem in enumerate(job_elements[len(jobs):]):
                if len(jobs) >= max_jobs:
                    break

                job_soup = BeautifulSoup(str(elem), "html.parser")
                job = _extract_job_data(job_soup, site.get("fields", {}), url)

                # Skip if no link found
                if not job.get("link"):
                    continue

                # Extract individual job details if configured
                if job.get("link") and site.get("detail_fields"):
                    print(f"Scraping details for: {job.get('title', 'Unknown title')}")
                    detailed_job = _scrape_individual_job(job["link"], site["detail_fields"])
                    job.update(detailed_job)
                    time.sleep(0.5)

                jobs.append(job)
                print(f"✓ Job {len(jobs)}/{max_jobs} collected: {job.get('title', 'Unknown title')}")

            # Scroll down to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Check if we've reached the bottom or no new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("No more content to load")
                break

            last_height = new_height
            scroll_attempts += 1

        print(f"Collected {len(jobs)} jobs with infinite scroll")
        return jobs

    except Exception as e:
        print(f"Error during infinite scroll scraping: {e}")
        return []
    finally:
        driver.quit()


def scrape_jobs(config_path: str | Path) -> List[Dict[str, Any]]:
    """Scrape job listings defined in *config_path*.

    The configuration must contain a ``sites`` list and may include ``skills``
    keywords as well as ``salary`` thresholds in USD or BRL.

    Enhanced to support individual job page extraction, pagination, and infinite scroll.
    """
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    skills_config = config.get("skills", [])
    salary_cfg = config.get("salary", {})
    min_usd = salary_cfg.get("usd")
    min_brl = salary_cfg.get("brl")

    jobs: List[Dict[str, Any]] = []

    for site in config.get("sites", []):
        print(f"Scraping {site.get('name', 'Unknown site')}...")

        max_jobs = site.get("max_jobs", 50)  # Default to 50 jobs per site

        # Check if this site uses infinite scroll
        if site.get("pagination", {}).get("type") == "infinite_scroll":
            print(f"Using infinite scroll for {site.get('name')}")
            site_jobs = _scrape_with_infinite_scroll(site, max_jobs)

            # Apply filters to scraped jobs
            filtered_jobs = []
            for job in site_jobs:
                # Apply skill filters
                haystack = " ".join(
                    filter(None, [job.get("skills"), job.get("description"), job.get("title")])
                )

                if skills_config and not _check_skills_match(haystack, skills_config):
                    continue

                # Apply salary filters
                cur, amount = _parse_salary(job.get("salary", ""))
                if (
                    (cur == "USD" and min_usd and amount < min_usd)
                    or (cur == "BRL" and min_brl and amount < min_brl)
                ):
                    continue

                filtered_jobs.append(job)
                if len(filtered_jobs) >= max_jobs:
                    break

            jobs.extend(filtered_jobs)
            print(f"Total filtered jobs from {site.get('name')}: {len(filtered_jobs)}")
            continue

        # Regular pagination scraping (existing logic)
        site_jobs = []
        current_url = site["url"]
        page_count = 0
        max_pages = site.get("max_pages", 20)  # Safety limit to prevent infinite loops

        while len(site_jobs) < max_jobs and page_count < max_pages:
            page_count += 1

            try:
                print(f"Scraping page {page_count}: {current_url}")
                soup = _get_page_content(current_url)

                # Extract job listings from current page
                job_elements = soup.select(site.get("job_selector", ""))
                print(f"Found {len(job_elements)} job listings on this page")

                page_jobs_added = 0
                for elem in job_elements:
                    if len(site_jobs) >= max_jobs:
                        print(f"Reached maximum jobs limit ({max_jobs}) for {site.get('name')}")
                        break

                    # Extract basic job info and link
                    job_soup = BeautifulSoup(str(elem), "html.parser")
                    job = _extract_job_data(job_soup, site.get("fields", {}), current_url)

                    # If we have a job link and detail fields, scrape the individual page
                    if job.get("link") and site.get("detail_fields"):
                        print(f"Scraping details for: {job.get('title', 'Unknown title')}")
                        detailed_job = _scrape_individual_job(job["link"], site["detail_fields"])
                        job.update(detailed_job)  # Merge detailed info
                        time.sleep(0.5)  # Be respectful to the server

                    # Apply skill filters
                    haystack = " ".join(
                        filter(None, [job.get("skills"), job.get("description"), job.get("title")])
                    )

                    if skills_config and not _check_skills_match(haystack, skills_config):
                        continue

                    # Apply salary filters
                    cur, amount = _parse_salary(job.get("salary", ""))
                    if (
                        (cur == "USD" and min_usd and amount < min_usd)
                        or (cur == "BRL" and min_brl and amount < min_brl)
                    ):
                        continue

                    site_jobs.append(job)
                    page_jobs_added += 1
                    print(f"✓ Job {len(site_jobs)}/{max_jobs} added: {job.get('title', 'Unknown title')}")

                print(f"Added {page_jobs_added} jobs from this page")

                # Check if we should continue to next page
                if len(site_jobs) >= max_jobs:
                    print(f"Reached target of {max_jobs} jobs for {site.get('name')}")
                    break

                # Get next page URL if pagination is configured
                if "pagination" in site:
                    next_url = _get_next_page_url(soup, current_url, site["pagination"])
                    if next_url and next_url != current_url:
                        current_url = next_url
                        time.sleep(1)  # Be respectful between pages
                    else:
                        print("No more pages available")
                        break
                else:
                    # No pagination configured, stop after first page
                    break

            except Exception as e:
                print(f"Error scraping page {current_url}: {e}")
                break

        jobs.extend(site_jobs)
        print(f"Total jobs collected from {site.get('name')}: {len(site_jobs)}")

    print(f"Total jobs found across all sites: {len(jobs)}")
    return jobs


if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="Scrape job listings")
    parser.add_argument("--config", default="../config/job_config.yaml")
    args = parser.parse_args()
    results = scrape_jobs(args.config)
    print(json.dumps(results, indent=2, ensure_ascii=False))
