#!/usr/bin/env python3
"""
Script to download logos for member organizations using Brandfetch API.
Set BRANDFETCH_API_KEY environment variable before running.
"""

import json
import os
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError

# Brandfetch API configuration
BRANDFETCH_API_KEY = os.environ.get('BRANDFETCH_API_KEY')
BRANDFETCH_BASE_URL = 'https://api.brandfetch.io/v2/brands/'

# Map organization names to their domains for Brandfetch API
# Some organizations may need manual domain lookup
ORGANIZATION_DOMAINS = {
    "AAUP Penn": "aaup.org",
    "AFSCME District Council 47": "afscme.org",
    "APALA Philly": "apalanet.org",
    "APFA PHL": "apfa.org",
    "API PA": None,  # May need manual lookup
    "Faculty and Staff Federation of the Community College of Philadelphia": "ccp.edu",
    "IUPAT District Council 21": "iupat.org",
    "Juntos": "juntos.org",
    "Movement Alliance Project": None,  # May need manual lookup
    "National Domestic Workers Alliance – PA Chapter": "domesticworkers.org",
    "OnePA": "onepa.org",
    "PA Debt Collective": None,  # May need manual lookup
    "PA Stands Up": "pastandsup.org",
    "Penn for PILOTs": "upenn.edu",  # University of Pennsylvania
    "Penn GET-UP": "upenn.edu",  # University of Pennsylvania
    "Philadelphia Coalition for Affordable Communities": None,  # May need manual lookup
    "Philadelphia Council AFL-CIO": "aflcio.org",
    "Philadelphia Joint Board Workers United": "workersunited.org",
    "PhilaPOSH": None,  # May need manual lookup
    "POWER": "powerinterfaith.org",
    "Restaurant Opportunities Center PA": "rocunited.org",
    "SAG-AFTRA Philadelphia": "sagaftra.org",
    "SEIU Healthcare PA": "seiu.org",
    "SEIU Local 668": "seiu.org",
    "TAUP AFT Local 4531": "aft.org",  # Temple Association of University Professionals
    "Teamsters Local 623": "teamster.org",
    "Teamsters Local 773": "teamster.org",
    "TUGSA AFT Local 6290": "aft.org",  # Temple University Graduate Students Association
    "UAP AFT Local 9608": "aft.org",  # University of Pennsylvania
    "WGA Philly": "wga.org",
}

# Define all member organizations
ORGANIZATIONS = list(ORGANIZATION_DOMAINS.keys())

def sanitize_filename(name):
    """Convert organization name to a safe filename."""
    return name.lower().replace(" ", "-").replace("/", "-").replace("–", "-").replace("'", "").replace(",", "")

def fetch_brand_data(domain):
    """Fetch brand data from Brandfetch API."""
    if not BRANDFETCH_API_KEY:
        raise ValueError("BRANDFETCH_API_KEY environment variable not set")
    
    url = f"{BRANDFETCH_BASE_URL}{domain}"
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {BRANDFETCH_API_KEY}',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
    except HTTPError as e:
        if e.code == 404:
            print(f"  Brand not found in Brandfetch: {domain}")
        elif e.code == 401:
            raise ValueError("Invalid Brandfetch API key")
        else:
            print(f"  HTTP Error {e.code} for {domain}: {e.reason}")
    except URLError as e:
        print(f"  URL Error for {domain}: {e.reason}")
    except Exception as e:
        print(f"  Error fetching {domain}: {e}")
    
    return None

def get_best_logo_url(brand_data):
    """Extract the best logo URL from brand data."""
    if not brand_data or 'logos' not in brand_data:
        return None
    
    logos = brand_data['logos']
    if not logos:
        return None
    
    # Prefer PNG format, then SVG, then any format
    preferred_formats = ['png', 'svg', 'jpg', 'jpeg']
    
    for logo in logos:
        if 'formats' in logo:
            for fmt in preferred_formats:
                for format_item in logo['formats']:
                    if format_item.get('format', '').lower() == fmt and 'src' in format_item:
                        return format_item['src']
            # If preferred format not found, use first available
            if logo['formats'] and 'src' in logo['formats'][0]:
                return logo['formats'][0]['src']
    
    return None

def download_logo(url, filepath):
    """Download a logo from a URL."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
                return True
    except Exception as e:
        print(f"  Error downloading logo: {e}")
    return False

def main():
    if not BRANDFETCH_API_KEY:
        print("ERROR: BRANDFETCH_API_KEY environment variable not set")
        print("Please set it with: export BRANDFETCH_API_KEY='your-api-key'")
        return
    
    output_dir = Path("../../src/assets/members")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading logos using Brandfetch API")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    downloaded = []
    failed = []
    skipped = []
    
    for org in ORGANIZATIONS:
        domain = ORGANIZATION_DOMAINS.get(org)
        
        # Determine file extension and filename
        filename_base = sanitize_filename(org)
        filepath_png = output_dir / f"{filename_base}.png"
        filepath_svg = output_dir / f"{filename_base}.svg"
        
        # Skip if already exists
        if filepath_png.exists() or filepath_svg.exists():
            print(f"✓ {org} - already exists")
            skipped.append(org)
            continue
        
        if not domain:
            print(f"✗ {org} - no domain mapped (needs manual lookup)")
            failed.append(org)
            continue
        
        print(f"Fetching {org} ({domain})...")
        
        # Fetch brand data from Brandfetch
        brand_data = fetch_brand_data(domain)
        
        if not brand_data:
            failed.append(org)
            continue
        
        # Get best logo URL
        logo_url = get_best_logo_url(brand_data)
        
        if not logo_url:
            print(f"  No logo found in brand data")
            failed.append(org)
            continue
        
        # Determine file extension from URL or format
        if logo_url.lower().endswith('.svg'):
            filepath = filepath_svg
        elif logo_url.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = filepath_png
        else:
            # Default to PNG
            filepath = filepath_png
        
        # Download the logo
        if download_logo(logo_url, filepath):
            print(f"✓ {org} - downloaded successfully")
            downloaded.append(org)
        else:
            failed.append(org)
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Downloaded: {len(downloaded)}")
    print(f"  Already existed: {len(skipped)}")
    print(f"  Failed/No domain: {len(failed)}")
    
    if downloaded:
        print(f"\nSuccessfully downloaded logos:")
        for org in downloaded:
            print(f"  ✓ {org}")
    
    if failed:
        print(f"\nOrganizations that need attention:")
        for org in failed:
            domain = ORGANIZATION_DOMAINS.get(org, "No domain mapped")
            print(f"  ✗ {org} ({domain})")

if __name__ == "__main__":
    main()

