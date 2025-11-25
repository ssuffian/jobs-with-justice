# Member Logos

This directory contains logos for coalition member organizations.

## Adding Logos

1. Download or obtain the logo for each organization
2. Save the logo file with a descriptive filename (e.g., `aaup-penn.png`, `afscme-dc47.png`)
3. Update `src/pages/our-work/our-coalition.astro` to import and use the logo:

```astro
---
import aaupLogo from '../../assets/members/aaup-penn.png';
// ... other imports
---

<div class="member-card">
  <Image src={aaupLogo} alt="AAUP Penn" class="member-logo" />
  <p class="member-name">{member}</p>
</div>
```

## Logo Guidelines

- Preferred formats: PNG (with transparency) or SVG
- Recommended size: 200-300px width
- Maintain aspect ratio
- Use transparent backgrounds when possible
- Ensure logos are readable at small sizes

## Member Organizations

- AAUP Penn
- AFSCME District Council 47
- APALA Philly
- APFA PHL
- API PA
- Faculty and Staff Federation of the Community College of Philadelphia
- IUPAT District Council 21
- Juntos
- Movement Alliance Project
- National Domestic Workers Alliance – PA Chapter
- OnePA
- PA Debt Collective
- PA Stands Up
- Penn for PILOTs
- Penn GET-UP
- Philadelphia Coalition for Affordable Communities
- Philadelphia Council AFL-CIO
- Philadelphia Joint Board Workers United
- PhilaPOSH
- POWER
- Restaurant Opportunities Center PA
- SAG-AFTRA Philadelphia
- SEIU Healthcare PA
- SEIU Local 668
- TAUP AFT Local 4531
- Teamsters Local 623
- Teamsters Local 773
- TUGSA AFT Local 6290
- UAP AFT Local 9608
- WGA Philly

