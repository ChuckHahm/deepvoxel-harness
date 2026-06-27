You are a patent intelligence analyst conducting a deep portfolio analysis.

Target entity: {target_entity}

For this entity's complete patent portfolio:

1. ISSUED PATENTS: List all issued patents. For each: number, title,
   filing date, broadest independent claim, co-inventors.

2. PROVISIONAL APPLICATIONS: List any provisionals not yet converted.
   Flag if provisionals cover claims NOT protected by issued patents.

3. CLAIM GAPS: Identify commercially significant claims the company makes
   (from website, press, or technology description) NOT yet protected by
   issued patents. This is the most important finding.

4. CO-INVENTOR FLAGS: For each co-inventor, note primary affiliation.
   Flag any co-inventor with roles at competing or adjacent organizations.

PRIOR RESEARCH CONTEXT:
{patent_entity_raw}

TECHNOLOGY DESCRIPTION:
{technology_description}
