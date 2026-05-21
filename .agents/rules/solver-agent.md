# Solver Agent Rule

- Solver, rates, spectra, and fitting modules must be pure computation.
- Do not read configs, write outputs, or generate plots in model-layer functions.
- Populations and intensities must be non-negative.
- Missing source terms or transition probabilities must fail closed or return explicit missing-data diagnostics.
- Fitting must expose candidate/error information, not only a single best point.
