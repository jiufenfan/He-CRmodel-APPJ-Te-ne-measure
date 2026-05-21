# Harness Agent Rule

- Harness code owns config loading, data loading, report generation, and output paths.
- Harnesses must not silently enable unverified data.
- Every run must record enabled data and validation issues.
- v0.1.0 harnesses may fail closed with clear missing-data reports instead of forcing a numeric result.
