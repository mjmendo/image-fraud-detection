# Solution

Implementation details and notes

## Approach

- Given R2.6, Claude code used to speed up proof-of-concept.
    - bot provided with challenge, requirements and solution as spec-driven development.
    - bot provided with instructions to generate code/tests, refactor, structure and lint the code.
- Script implements a pipeline architecture (load, process, output)
    - format detection triggers format-tailored "recipe" of detection methods.
- Use case
    - eval: run detector in test mode (metrics) over an input dataset (forged/original folders)
- Evaluation modes (all run in parallel)
    - strict: more precision, minimize false positives. Threshold == .7 (high confidence required)
    - balanced: 80% recall / 20% fp per requirements. Threshold == .5 (default)
    - aggresive: recall focused, catch more fakes. Threshold == .3 
- Input image format supported
    - JPEG: Metadata → Reverse Search → ELA → Statistical → Copy-Move → (Optional: Shadow)
    - TIFF/BMP: Metadata → Reverse Search → Statistical → Copy-Move (prioritize) → Noise Variance
    - PNG: Metadata → Reverse Search → Statistical → Copy-Move → Noise Variance
- Not implemented
    - reverse search
    - pdf image extraction
    - resilience, error handling (try-catches)
    - optimizations (parallel detection)
    - validation set
- Detection tiers
    1. primary/essential detectors
        - exif metadata
        - reverse image search
        - ela analysis
    2. secondary/advanced detectors
        - statistical analysis
        - duplicate region detection
    3. specialized
        - noise consistency analysis
- Configuration files for parametrization


## Outcome

- Both executions over provided images (jpg) and over a sample of CASIA2.0 (200 images, jpg/tiff) result in forged images detected on balance mode.
- Both executions over-rely on metadata *only* ("photoshop" in 95% of image metadata).

## Conclusion

- Even though the solution reaches the 80/20 requirements, it only works when metadata carry signals.  
    - Tiers implemented are a naive approach to real-world cases.
    - Parameter calilbration need a larger domain-specific dataset (statistical, noise).
- Implementing reverse search would have increased the accuracy, although potential contribution is unknown, probaly low.
- Validation set for param tuning would be the next possible step (on CASIA2.0?), although a more domain-specific dataset is required.

Real-world cases require outstandingly more scalable, complex, and sofisticated approaches (CNN, Visual Transformers) with their own challenges and tradeoffs.