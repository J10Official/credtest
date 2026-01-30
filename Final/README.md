# MWAHAHA Humor Generation Pipeline

A modular DSPy-based pipeline for the SemEval 2026 Task 1: MWAHAHA (Models Write Automatic Humor And Humans Annotate).

## Overview

This pipeline generates humorous content for multiple tasks:
- **Task A1**: Headline-based jokes (English, Spanish, Chinese)
- **Task A2**: Word-inclusion jokes (must contain two specific words)
- **Task B1**: GIF captions (image only)
- **Task B2**: GIF captions with prompt completion

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                    (CLI Entry Point)                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                       pipeline.py                                │
│    HeadlineJokePipeline | WordInclusionJokePipeline             │
│    GifCaptionPipeline   | GifPromptCaptionPipeline              │
└────┬──────────────┬─────────────┬──────────────┬────────────────┘
     │              │             │              │
     ▼              ▼             ▼              ▼
┌─────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│signatures│  │  api.py   │  │validators│  │ logger.py│
│_A1/A2/  │  │(Gemini/   │  │  .py     │  │          │
│B1/B2.py │  │OpenRouter)│  │          │  │          │
└─────────┘  └───────────┘  └──────────┘  └──────────┘
                  │
           ┌──────▼──────┐
           │  config.py  │
           │  (.env)     │
           └─────────────┘
```

## 5-Module Pipeline

Each task uses a consistent 5-module architecture based on GTVH (General Theory of Verbal Humor):

1. **ContextEnricher** (The Analyst) - Analyzes input to extract situation, associations, and targets
2. **HumorArchitect** (The Brain) - Designs the cognitive mechanism (script opposition, logical mechanism)
3. **DeliveryStrategist** (The Director) - Plans narrative strategy and language style
4. **ContentWriter** (The Artist) - Generates the actual joke with setup and punchline
5. **HumorJudge** (The Critic) - Evaluates and selects the best candidate

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install dspy-ai python-dotenv

# Setup environment variables
cp .env.example .env
# Edit .env and add your API key
```

## Configuration

### Environment Variables (`.env`)

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here  # Optional
API_PROVIDER=gemini  # or "openrouter"
```

### LLM Parameters (`config.py`)

```python
# Default parameters for all modules
DEFAULT_LLM_PARAMS = {
    "temperature": 0.9,
    "top_p": 0.95,
    "max_tokens": 2048,
}

# Module-specific overrides
MODULE_LLM_PARAMS = {
    "HumorArchitect": {"temperature": 1.0},
    "ContentWriter": {"temperature": 1.0},
    "HumorJudge": {"temperature": 0.3},
}
```

## Usage

### Basic Commands

```bash
# Test mode (default) - 10 samples per file
python main.py

# Full mode - all samples
python main.py --full

# Specific task
python main.py --task a-en       # Task A English only
python main.py --task b1 --full  # Task B1 full mode

# Resume from interruption (full mode only)
python main.py --full --resume

# Use different provider
python main.py --provider openrouter
```

### Available Tasks

| Task | Description | Languages |
|------|-------------|-----------|
| `a-en` | Headlines + Word inclusion | English |
| `a-es` | Headlines + Word inclusion | Spanish |
| `a-zh` | Headlines + Word inclusion | Chinese |
| `b1` | GIF captions | English |
| `b2` | GIF + prompt captions | English |
| `all` | All tasks (default) | All |

### Test vs Full Mode

| Mode | Task A | Task B |
|------|--------|--------|
| Test | 10 samples (5 headline, 5 words) | 5 samples |
| Full | All 300 samples | All 301 samples |

## Output

### Directory Structure

```
Final/
├── test_outputs/          # Test mode outputs
│   ├── task-a-en.tsv
│   ├── task-a-es.tsv
│   ├── task-a-zh.tsv
│   ├── task-b1.tsv
│   └── task-b2.tsv
├── outputs/               # Full mode outputs
│   └── ...
└── logs/                  # Detailed logs
    └── run_YYYYMMDD_HHMMSS.log
```

### Output Format

TSV files with two columns:
```tsv
id	text
en_2001	Why did the Panamanian lawmakers visit Taiwan? Because diplomatic immunity doesn't cover awkward silences.
en_2002	Liverpool's transfer strategy: Buy in summer, panic in January, cry in May.
```

## Logging

The pipeline provides detailed logging:

```
================================================================================
 🎭 HEADLINE JOKE PIPELINE [EN]
================================================================================
Headline: Experts warn of health threat posed by ultra-processed foods

------------------------------------------------------------
 📝 Generating Candidate 1/2
------------------------------------------------------------

------------------------------------------------------------
 🔧 ContextEnricher
------------------------------------------------------------
  📥 INPUT [ContextEnricher]
  original_input: Experts warn of health threat posed by ultra-processed foods
  target_language_and_culture: English

  📤 OUTPUT [ContextEnricher]
  situation: Health experts are raising alarms about...
  semantic_associations:
    - ultra-processed: chemicals, additives, convenience...
  potential_targets:
    - The vague term "experts"
    - The irony of warning about food...
  📊 Tokens: 245 in / 312 out = 557 total
```

## Retry Logic

Rate limits are handled with progressive backoff:
```
5s → 5s → 10s → 20s → 30s → 30s → 30s → 2min → 2min → 2min
```

## Constraint Validation

The pipeline validates generated content:

- **Task A1**: Character limit (900 EN/ES, 300 ZH), no placeholders
- **Task A2**: Word inclusion (both words must appear), character limit
- **Task B**: Word count (max 20 words), character limit

Validation is performed after generation and failures are logged.

## Token Tracking

Token usage is tracked for cost analysis:

```
📈 SUMMARY
  Duration: 0:05:23
  Total Input Tokens: 15,234
  Total Output Tokens: 8,456
  Total API Calls: 48
```

## File Structure

| File | Description |
|------|-------------|
| `main.py` | CLI entry point |
| `config.py` | Configuration (paths, LLM params, limits) |
| `api.py` | API provider management (Gemini/OpenRouter) |
| `pipeline.py` | DSPy pipeline implementations |
| `data_loader.py` | TSV loading and resume capability |
| `validators.py` | Constraint satisfaction checks |
| `logger.py` | Structured logging utilities |
| `signatures_*.py` | DSPy signature definitions |

## Extending

### Adding a New Provider

1. Create a new class in `api.py`:
```python
class NewProvider(APIProvider):
    def configure(self, **kwargs) -> dspy.LM:
        # Configure and return DSPy LM
        pass
```

2. Register in `PROVIDERS` dict:
```python
PROVIDERS = {
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
    "newprovider": NewProvider,
}
```

3. Add model name to `config.py`:
```python
MODELS = {
    "gemini": "gemini-2.0-flash",
    "newprovider": "model-name",
}
```

### Modifying LLM Parameters

Edit `config.py`:
```python
MODULE_LLM_PARAMS = {
    "ContentWriter": {
        "temperature": 1.2,
        "top_p": 0.9,
    },
}
```

## Notes

### GIF Description (Task B)

The current implementation uses placeholder GIF descriptions. In production:
1. Use a vision model (e.g., Gemini Vision) to describe GIFs
2. Or pre-process GIFs to create description files

### Resume Capability

Resume only works in full mode. The pipeline:
1. Reads existing output file
2. Identifies processed IDs
3. Skips already-processed items

### Error Handling

On error, the pipeline:
1. Logs the error with context
2. Saves a placeholder in output
3. Continues to next item

## License

MIT License - See LICENSE file for details.
