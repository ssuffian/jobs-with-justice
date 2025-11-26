#!/bin/bash
# Script to download logos for all member organizations

cd "$(dirname "$0")/../../src/assets/members"

# Function to download with error handling
download_logo() {
    local url=$1
    local filename=$2
    if [ ! -f "$filename" ]; then
        echo "Downloading $filename..."
        curl -L -f -s -o "$filename" "$url" && echo "✓ $filename" || echo "✗ Failed: $filename"
    else
        echo "✓ $filename (already exists)"
    fi
}

# Major unions - Wikipedia Commons
download_logo "https://upload.wikimedia.org/wikipedia/commons/4/4a/SEIU_logo.svg" "seiu-healthcare-pa.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/4/4a/SEIU_logo.svg" "seiu-local-668.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/4/4e/SAG-AFTRA_logo.svg" "sag-aftra-philadelphia.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/8/8a/Teamsters_logo.svg" "teamsters-local-623.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/8/8a/Teamsters_logo.svg" "teamsters-local-773.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/0/0a/AFSCME_logo.svg" "afscme-district-council-47.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/4/4c/AFL-CIO_logo.svg" "philadelphia-council-afl-cio.svg"

# AFT (American Federation of Teachers) - for TAUP, TUGSA, UAP
download_logo "https://upload.wikimedia.org/wikipedia/commons/7/7a/AFT_logo.svg" "taup-aft-local-4531.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/7/7a/AFT_logo.svg" "tugsa-aft-local-6290.svg"
download_logo "https://upload.wikimedia.org/wikipedia/commons/7/7a/AFT_logo.svg" "uap-aft-local-9608.svg"

# AAUP (American Association of University Professors)
download_logo "https://upload.wikimedia.org/wikipedia/commons/8/8a/AAUP_logo.svg" "aaup-penn.svg" || \
download_logo "https://www.aaup.org/sites/default/files/AAUP-logo.png" "aaup-penn.png"

# IUPAT (International Union of Painters and Allied Trades)
download_logo "https://upload.wikimedia.org/wikipedia/commons/9/9a/IUPAT_logo.svg" "iupat-district-council-21.svg"

# WGA (Writers Guild of America)
download_logo "https://upload.wikimedia.org/wikipedia/commons/1/1a/WGA_logo.svg" "wga-philly.svg"

# APALA (Asian Pacific American Labor Alliance)
download_logo "https://www.apalanet.org/wp-content/uploads/2021/01/apala-logo.png" "apala-philly.png" || \
download_logo "https://upload.wikimedia.org/wikipedia/commons/6/6a/APALA_logo.svg" "apala-philly.svg"

# APFA (Association of Professional Flight Attendants)
download_logo "https://www.apfa.org/wp-content/uploads/2021/01/apfa-logo.png" "apfa-phl.png"

# Workers United
download_logo "https://www.workersunited.org/wp-content/uploads/2021/01/workers-united-logo.png" "philadelphia-joint-board-workers-united.png"

# Community organizations - these may need manual downloads
echo ""
echo "The following organizations may need manual logo downloads from their websites:"
echo "  - Juntos (juntos.org)"
echo "  - POWER (powerinterfaith.org)"
echo "  - PA Stands Up (pastandsup.org)"
echo "  - OnePA (onepa.org)"
echo "  - Movement Alliance Project"
echo "  - National Domestic Workers Alliance PA Chapter"
echo "  - PA Debt Collective"
echo "  - Penn for PILOTs"
echo "  - Penn GET-UP"
echo "  - Philadelphia Coalition for Affordable Communities"
echo "  - PhilaPOSH"
echo "  - Restaurant Opportunities Center PA"
echo "  - Faculty and Staff Federation of the Community College of Philadelphia"
echo "  - API PA"

