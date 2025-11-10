# Coding Challenge: Forged Image Detection

## Introduction

This coding challenge is designed to assess your ability to develop a Python script that can distinguish between authentic and forged images. The goal is to maximize the detection of forged images while minimizing false positives.

## Challenge Description

You are tasked with creating a Python script that takes two input folders: one containing forged images (retouched with tools like Photoshop) and another containing authentic images (not retouched). Your script should analyze these images and classify them as either forged or authentic. The primary objective is to achieve a high true positive rate (capturing as many forged images as possible) and a low false positive rate (identifying as few authentic images as forged).

### Input
 
- forged_images/: A folder containing images that have been digitally altered.
- authentic_images/: A folder containing original, unaltered images.

### Output

Your script should output a summary of its performance, including:

 - Total number of images processed.
 - Number of forged images detected.
 - Number of authentic images incorrectly classified as forged (false positives).
 - Number of forged images missed (false negatives).
 - Accuracy, precision, and recall metrics (if applicable).


### Delivery
Please deliver your solution as either a GitHub repository or a ZIP file. The submission must include:

1. Your Python script(s).
2. Clear instructions on how to run your script and any necessary dependencies (e.g., a requirements.txt file).
3. A brief explanation of your approach and any assumptions made.


### Evaluation Criteria

Your solution will be evaluated based on the following:

 - Trade-offs Made: Justification of design choices, acknowledging limitations and alternative approaches.
 - Handover Quality: The ease with which another developer could understand, maintain, and extend your code.
 - Codebase Awareness: Demonstrating understanding of common coding patterns, best practices, and avoiding "vibe coding."
 - Use of AI Tools: Documenting any AI tools used (e.g., code generators, analysis tools) and their impact on the solution.

### Example Usage (Conceptual)

```python detect_forgeries.py --forged_dir forged_images/ --authentic_dir authentic_images/```


## Follow-up Q&A w Stakeholders


1. Biz requirements: what kind of images will be assessed? I assume it is related to the insurance domain. Will they have car accidents, or general pics photoshopped, or idk, burned/broken/damaged things?
    - Stakeholder reply: The assumption is correct. You can simplify by looking at damages (there is a really hard scenario of a number nicely replaced in the car plate, but it's quite hard to catch without also not triggering a lot of false positives)
2. Are all the images carrying the same weight/risk/cost/tolerable error rate? A low-risk case may be worth a low-cost solution, or even a fallback chain. 
    - Stakeholder reply: at this point, we just process each single image we identify in 
        1. pdf documents (extracted with PyMuPDF) and 
        2. provided by the user (usually tiff or bmp that we convert - yes, that's the kind of users). 
    - Each one has the same weight for now. Later we may weight them differently depending on the type of image.
3. What is considered a "high true positive rate"? 60, 70, 90, 95, 99? Would it be connected with question 2? Is 5-10% accuracy gain worth higher complexity?
    - Stakeholder reply: Great questions and the drivers we are using now are:
        - at least 80% true positives
        - no more than 20% false positives
    - We may refine them later.
4. Are COTS considered options for the solution? Any constraints on tech, procedure, cost, perf, quality certif, or legal?
    - Stakeholder reply: Why not :) (hint hint, ours is a pseudo one). Great question. Drivers are:
        - Accuracy
        - ISO27001b and GDPR compliant
    - Anything else is about what drives the best outcome on the above goals / constraints.
5. Delivery: is a script the target output? I sense it would be more like a small system/workflow/pipeline rather than a script. Would it be acceptable to use another delivery format, like a miro board or an RFC-like document?
    - Stakeholder reply: This, if properly implemented, could take many hours / days. We're happy with a very simple runnable "something" you can show us, and a nice discussion on tradeoffs.

