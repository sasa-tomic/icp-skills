#!/usr/bin/env python3
"""Fetch learn.internetcomputer.org and convert to AI-readable Markdown.

Usage:
    uv run fetch_learn.py [--force]

Options:
    --force  Re-download and re-convert all pages (ignore cache)
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE_URL = "https://learn.internetcomputer.org"
SITEMAP_URL = f"{BASE_URL}/hc/sitemap.xml"
CACHE_DIR = Path(".cache/html")
OUTPUT_DIR = Path("learn-md")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def get_sitemap_urls() -> list[str]:
    """Fetch and parse sitemap to get all article URLs."""
    result = subprocess.run(
        ["wget", "-q", "-O", "-", "--user-agent", USER_AGENT, SITEMAP_URL],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch sitemap: {result.stderr}")

    root = ElementTree.fromstring(result.stdout)
    namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    urls = []
    for url_elem in root.findall(".//ns:loc", namespace):
        if url_elem.text:
            urls.append(url_elem.text)

    return urls


def url_to_cache_path(url: str) -> Path:
    """Convert URL to cache file path."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    if not Path(path).suffix:
        path = f"{path}.html"
    return CACHE_DIR / path


def url_to_output_path(url: str) -> Path:
    """Convert URL to output markdown path."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    if not Path(path).suffix:
        path = f"{path}.md"
    else:
        path = str(Path(path).with_suffix(".md"))
    return OUTPUT_DIR / path


def download_page(url: str, force: bool = False, retries: int = 3) -> Path | None:
    """Download a page to cache with retries. Returns cache path or None on failure."""
    cache_path = url_to_cache_path(url)

    if not force and cache_path.exists():
        return cache_path

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(retries):
        result = subprocess.run(
            [
                "wget", "-q",
                "--user-agent", USER_AGENT,
                "--header", "Accept: text/html,application/xhtml+xml",
                "--header", "Accept-Language: en-US,en;q=0.9",
                "-O", str(cache_path),
                url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0 and cache_path.exists() and cache_path.stat().st_size > 0:
            return cache_path

        # Clean up failed download before retry
        if cache_path.exists():
            cache_path.unlink()

    return None


def extract_article(html_path: Path) -> tuple[str, str] | None:
    """Extract title and content from HTML. Returns (title, html_content) or None."""
    soup = BeautifulSoup(html_path.read_text(errors="ignore"), "html.parser")

    # Get title
    title_elem = soup.find("h1", itemprop="name")
    if not title_elem:
        title_elem = soup.find("title")
    if not title_elem:
        return None

    title = title_elem.get_text(strip=True)
    title = re.sub(r"\s*[–-]\s*Internet Computer\s*$", "", title)

    # Get article content
    content_elem = soup.find("section", class_="article-content")
    if not content_elem:
        return None

    # Remove scripts/styles
    for tag in content_elem.find_all(["script", "style"]):
        tag.decompose()

    return title, str(content_elem)


def html_to_md(html: str) -> str:
    """Convert HTML to clean markdown."""
    text = md(html, heading_style="ATX", bullets="-", strip=["script", "style"])
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = text.replace("\xa0", " ")
    return text.strip()


def process_url(url: str, force: bool = False) -> tuple[str, str]:
    """Download and convert a URL. Returns (status, short_url)."""
    short_url = url.replace(BASE_URL, "")
    output_path = url_to_output_path(url)

    # Skip if already converted (unless forcing)
    if not force and output_path.exists():
        return "skip", short_url

    # Download
    cache_path = download_page(url, force)
    if not cache_path:
        return "fail", short_url

    # Extract article content
    result = extract_article(cache_path)
    if not result:
        return "no-content", short_url

    title, content_html = result
    md_content = html_to_md(content_html)

    # Write markdown
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"# {title}\n\n{md_content}\n")

    return "ok", short_url


def main() -> None:
    force = "--force" in sys.argv

    print("Fetching sitemap...")
    urls = get_sitemap_urls()
    print(f"Found {len(urls)} URLs\n")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stats = {"ok": 0, "skip": 0, "fail": 0, "no-content": 0}

    for url in urls:
        status, short_url = process_url(url, force)
        stats[status] += 1

        icon = {"ok": "[OK]  ", "skip": "[SKIP]", "fail": "[FAIL]", "no-content": "[----]"}[status]
        print(f"  {icon} {short_url}")

    print(f"\nDone!")
    print(f"Converted: {stats['ok']}, Cached: {stats['skip']}, "
          f"No content: {stats['no-content']}, Failed: {stats['fail']}")
    print(f"Output: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
