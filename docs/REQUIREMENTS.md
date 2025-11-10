# Requirements

The main objective (goal) is *to achieve a high true positive rate (capturing as many forged images as possible) and a low false positive rate (identifying as few authentic images as forged).*

Here are listed the identified requirements from the [CHALLENGE.md](CHALLENGE.md) document.

## Requirement Interpretation

1. **Functional**
    1. solution must load images from 2 local folders, one with forged images (altered) and another with authentic images (not retouched, unaltered). Only images should be supported.
    2. solution must analyze and classify images as either `forged` or `authentic`.
    3. solution must focus on insurance domain, specifically images containing car damages, excluding car plates tampering.
    4. solution should support `.tiff`/`.bmp` raw formats besides compressed stardard formats (jpg).
    5. solution should not process any contextual data other than the contained in the images.

2. **Non-functional**
   1. solution must be formulated in python code (script, not a system).
   2. solution should be a simple executable sample representative enough to initiate discussion. 
   3. solution must be compliant with ISO27001b and GDPR compliant
   4. solution must be optimized for *accuracy* (see R4.1)
   5. solution should not observe any cost constraints.
   6. time-to-market and effort low.

3. **Principles**
   1. tradeoff awareness
   2. handover quality
   3. coding best practices in python
   4. transfparent AI tool documentation and impact.

4. **Constraints**
    1. at least 80% true positives.
    2. no more than 20% false positives.
    3. no training dataset provided.

5. **Identified tradeoffs**
    1. R4.1 vs R4.2: higher true positives (recall) incurr in higher false prositives.
    2. R2.3 vs R2.4: higher compliance incurr in lower accuracy.


### Assumptions

1. Images provided do not specify which one is original/forged. We assume damaged car image is forged (also bigger file size).
2. Candidate Car damages being considered in the solution (not all relevant since they require context beyond the image itself):
    - Staged accidents: Older damage photos used for new claims
    - Severity inflation: Photoshopping minor damage to look worse
    - Vehicle cloning: Same damage photo used for multiple claims
    - VIN manipulation: Altering vehicle identification in photos
    - Pre-existing damage: Old damage photos claimed as new
    - Damage exaggeration: Digitally worsening damages, like collitions or scratches
    - Stock photos: Internet images passed off as actual damage
    - Duplicate claims: Same damage photo across multiple properties
3. No specialized training dataset provided, assumed no training models part of the solution.
4. No processing volume provided. Assuming local compute (laptop), so single thread tolerable.


## Appendix

### Compliance

Extension for R2.2

- ISO 27001 Requirements
    - Secure training environments with access controls
    - Encryption of training data (at rest and in transit)
    - Comprehensive audit trails
    - Regular security testing
    - COTS vendors handle most of this (included in certification)

- GDPR Requirements
    - Legitimate interest as lawful basis (document LIA)
    - Transparency: Inform policyholders about ML training
    - Data minimization: Use differential privacy, federated learning
    - Article 22: No purely automated adverse decisions without human review
    - Right to explanation: Must explain individual decisions

- Explainable AI
    - Legal requirement: Not just "nice to have" - legally required under GDPR Article 22 
    - No black-box ML
    - Minimum requirements:
        - Feature attribution
        - Visual explanations
        - Plain language explanations
    - Best practices:
        - Interactive interfaces
        - Contrastive cases
        - Uncertainty quantification
    - Available tools: SHAP, LIME, Grad-CAM, attention maps
    - Trade-off: 5-10% accuracy reduction for full explainability (Germany standard)