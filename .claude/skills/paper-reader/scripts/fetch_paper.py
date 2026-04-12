#!/usr/bin/env python3
"""
Download a research paper PDF from a URL.
Supports arxiv abstract URLs (converts to PDF) and direct PDF URLs.
Usage: python fetch_paper.py <url>
Output: Path to downloaded PDF (printed to stdout)
"""

import argparse
import os
import re
import sys
import tempfile
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests required. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

ARXIV_ABS_PATTERN = re.compile(
    r"https?://(?:www\.)?arxiv\.org/abs/(\d+\.\d+)",
    re.IGNORECASE
)
ARXIV_PDF_PATTERN = re.compile(
    r"https?://(?:www\.)?arxiv\.org/pdf/(\d+\.\d+)",
    re.IGNORECASE
)


def get_pdf_url(url: str) -> str:
    """Convert arxiv abstract URL to PDF URL if needed."""
    match = ARXIV_ABS_PATTERN.search(url)
    if match:
        paper_id = match.group(1)
        return f"https://arxiv.org/pdf/{paper_id}.pdf"
    return url


def download_pdf(url: str, dest_dir: Optional[str] = None) -> str:
    """Download PDF from URL and return path to saved file."""
    pdf_url = get_pdf_url(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PaperReader/1.0)"
    }
    resp = requests.get(pdf_url, headers=headers, timeout=60)
    resp.raise_for_status()

    if "application/pdf" not in resp.headers.get("Content-Type", ""):
        # Arxiv may redirect; check content
        if resp.content[:4] != b"%PDF":
            raise ValueError(f"URL did not return a valid PDF. Content-Type: {resp.headers.get('Content-Type')}")

    dir_path = dest_dir or tempfile.gettempdir()
    os.makedirs(dir_path, exist_ok=True)

    # Derive filename from URL
    if "arxiv.org" in pdf_url:
        paper_id = ARXIV_PDF_PATTERN.search(pdf_url)
        if paper_id:
            filename = f"arxiv_{paper_id.group(1).replace('.', '_')}.pdf"
        else:
            filename = "arxiv_paper.pdf"
    else:
        filename = url.split("/")[-1].split("?")[0] or "paper.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

    filepath = os.path.join(dir_path, filename)
    with open(filepath, "wb") as f:
        f.write(resp.content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Download a research paper PDF from URL")
    parser.add_argument("url", help="Arxiv abstract URL, arxiv PDF URL, or direct PDF URL")
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Directory to save PDF (default: temp dir)"
    )
    args = parser.parse_args()

    try:
        path = download_pdf(args.url, args.output_dir)
        print(path)
    except requests.RequestException as e:
        print(f"Error: Failed to download: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
