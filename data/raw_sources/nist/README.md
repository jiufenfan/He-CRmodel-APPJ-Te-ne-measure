# NIST Raw Sources

Reserved for future NIST ASD exports or query snapshots.

No NIST data is imported in v0.1.0.

Planned raw-source products:

- He I level table export for canonical `levels.py` backing data.
- He I line/transition-probability export containing wavelengths and Einstein `Aki` coefficients for spontaneous radiation `He(p) -> He(q) + hv`.
- Query manifests: `hei_levels_query_manifest.json`, `hei_lines_query_manifest.json`.
- Raw exports present in this repo: `He-levels.txt`, `He-lines.txt` (NIST ASD CSV exports).

Every future export must record query parameters, download date, ASD citation/version information if available, and whether the table came from the Lines or Levels query.
