# Logo Download Script

This script uses the Brandfetch API to download logos for all member organizations.

## Setup

1. **Set your Brandfetch API key as an environment variable:**

   ```bash
   export BRANDFETCH_API_KEY='your-api-key-here'
   ```

   Or add it to your shell profile (`~/.zshrc` or `~/.bashrc`):
   ```bash
   echo 'export BRANDFETCH_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Run the script:**

   ```bash
   python3 download_logos.py
   ```

## How it works

- The script maps each organization to its domain name
- It queries the Brandfetch API for brand data
- It downloads the best available logo format (preferring PNG, then SVG)
- Logos are saved to `src/assets/members/` with sanitized filenames

## Organizations without domains

Some organizations don't have a mapped domain and will need manual lookup:
- API PA
- Movement Alliance Project
- PA Debt Collective
- Philadelphia Coalition for Affordable Communities
- PhilaPOSH

For these, you can either:
1. Find their domain and add it to `ORGANIZATION_DOMAINS` in the script
2. Manually download their logos from their websites

## Output

Logos are saved with filenames like:
- `seiu-healthcare-pa.png`
- `sag-aftra-philadelphia.svg`
- `teamsters-local-623.png`

The script will skip logos that already exist, so you can run it multiple times safely.

