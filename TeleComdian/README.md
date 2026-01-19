# Tele-Comedian: Neuro-Symbolic Humor Generation System

## Architecture Overview

The system follows a **Decomposed Reasoning Pipeline** to generate humor. Unlike "black box" generation, this system breaks down the creative process into distinct cognitive steps.

```mermaid
graph TD
    A[Input: Headline/Words/Image] --> B{Input Type?}
    B -- Image --> C[Module 1a: VLM Context Enrichment]
    B -- Text --> D[Module 1b: Semantic/Cultural Retrieval]
    C --> E[Context Object]
    D --> E
    E --> F[Module 2: Humor Theoretic Reasoning (CoT)]
    F --> G[Humor Strategy / Script]
    G --> H[Module 3: Dynamic Parameter Drafter]
    H --> I[Raw Drafts]
    I --> J[Module 4: Post-Hoc Formatter]
    J --> K[Structured Candidate]
    K --> L[Module 5: RLAIF Judges]
    L --> M{Pass?}
    M -- Yes --> N[Final Output]
    M -- No --> H[Retry with Feedback]
```

## Modules

1.  **Context Enrichment:** Uses Retrieval or VLMs to ground the joke in facts.
2.  **Humor Theory:** Uses Chain-of-Thought to identify "Benign Violations" or "Script Switches".
3.  **Dynamic Drafter:** Generates the joke text using phase-specific hyperparameters (High Temp for brainstorming, Low Temp for refining).
4.  **Formatter:** Enforces constraints (length, word inclusion) strictly.
5.  **Judges:** Evaluates the joke for constraints, theory alignment, and "vibe".

## Tech Stack

*   **Framework:** `dspy` (Declarative Self-Improving Language Programs)
*   **Models:** Google Gemini (via `google-generativeai` or `litellm`)
*   **Validation:** `pydantic`
*   **Data:** `pandas`

## File Structure

```
TeleComdian/
├── data/                   # Input TSV files
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration & Model Setup
│   ├── pipeline.py         # Core TeleComedianPipeline Class
│   ├── modules/            # DSPy Modules
│   │   ├── __init__.py
│   │   ├── context.py      # Context Enrichment
│   │   ├── theory.py       # Humor Theory CoT
│   │   ├── draft.py        # Dynamic Drafter
│   │   └── formatter.py    # Post-Hoc Structuring
│   └── judges/             # RLAIF Judges
│       ├── __init__.py
│       └── evaluators.py
├── requirements.txt
└── README.md
```

## Implementation Plan

1.  **Setup:** Initialize DSPy with Gemini.
2.  **Core Modules:** Implement Context, Theory, and Draft modules using `dspy.Signature`.
3.  **Pipeline:** Connect modules in `TeleComedianPipeline`.
4.  **Dynamic Params:** Implement the logic to switch temperatures between modules.
5.  **Evaluation:** Implement the Judge module.
