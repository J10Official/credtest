# MWAHAHA Humor Generation Pipeline - Technical Documentation

## Overview

The MWAHAHA (Memes with Automated Humor and Hilarious AI) Pipeline is a DSPy-based humor generation system designed for the SemEval 2026 MWAHAHA shared task. It generates jokes and captions for:

- **Task A1**: Headline-based jokes (EN, ES, ZH)
- **Task A2**: Word-inclusion jokes (EN, ES, ZH)  
- **Task B1**: GIF caption generation
- **Task B2**: GIF + prompt caption generation

---

## Architecture

### High-Level Flow

```
Input (Headline/Words/GIF) 
    → ContextEnricher (analyze)
    → HumorArchitect × 2 (parallel, different humor concepts)
        → DeliveryStrategist × 2 (parallel, different delivery styles)
            → ContentWriter (generate jokes)
    → HumorJudge (tournament selection)
    → Best Joke Output
```

### 2×2 Variation Strategy

The pipeline generates **4 candidate jokes** using a 2×2 strategy:
- 2 different **humor concepts** from HumorArchitect (irony/incongruity vs. exaggeration/absurdity)
- 2 different **delivery styles** per concept (deadpan vs. energetic)

All 4 branches run **in parallel** using `ThreadPoolExecutor` for ~4x speedup.

### 5-Module Architecture (GTVH-Based)

Based on the General Theory of Verbal Humor:

| Module | Role | Purpose |
|--------|------|---------|
| **ContextEnricher** | Analyst | Extract situation, semantic associations, potential targets |
| **HumorArchitect** | Brain | Design GTVH structure (script opposition, logical mechanism) |
| **DeliveryStrategist** | Director | Choose narrative format and language style |
| **ContentWriter** | Artist | Write final joke with setup and punchline |
| **HumorJudge** | Critic | Tournament-style selection of best joke |

---

## File Structure

```
Final/
├── main.py              # CLI entry point
├── config.py            # Configuration constants
├── api.py               # API providers, retry logic, token tracking
├── pipeline.py          # UnifiedHumorPipeline class
├── signatures_A1.py     # DSPy signatures for Task A1 (headline jokes)
├── signatures_A2.py     # DSPy signatures for Task A2 (word inclusion)
├── signatures_B1.py     # DSPy signatures for Task B1 (GIF captions)
├── signatures_B2.py     # DSPy signatures for Task B2 (GIF + prompt)
├── data_loader.py       # TSV loading/saving, resume capability
├── gif_analyzer.py      # GIF → MP4 → Gemini analysis
├── validators.py        # Constraint checking (word inclusion, limits)
├── logger.py            # Colored logging, DSPy tracing
├── requirements.txt     # Python dependencies
├── Input/               # Input TSV files
├── outputs/             # Full mode outputs
├── test_outputs/        # Test mode outputs
└── logs/                # Run logs
```

---

## Module Documentation

### 1. `api.py` - API Module

**Purpose**: Unified interface for LLM providers with retry logic and token tracking.

#### Key Components

| Class/Function | Description |
|----------------|-------------|
| `TokenTracker` | Thread-safe token usage tracking across API calls |
| `RetryTracker` | Thread-safe retry attempt tracking per module |
| `GeminiProvider` | Google Gemini API provider via LiteLLM |
| `OpenRouterProvider` | OpenRouter API provider (future-ready) |
| `with_retry` | Decorator for automatic retry with exponential backoff |
| `configure_dspy()` | Main entry point for DSPy configuration |
| `call_with_retry()` | Wrapper for DSPy predictor calls with retry |
| `track_tokens()` | Extract and record token usage from LLM history |

#### Retry Configuration

```python
RETRY_INTERVALS = [5, 5, 10, 20, 30, 30, 30, 120, 120, 120]  # seconds
```

Handles: rate limits (429), quota errors, transient errors (500, 502, 503, timeouts)

#### ChatAdapter Configuration (Line 266)

```python
dspy.configure(adapter=dspy.ChatAdapter())
```

**Critical**: Prevents JSON mode issues with gemma-3-27b-it which doesn't support JSON mode.

---

### 2. `config.py` - Configuration

**Purpose**: Centralize all configurable parameters.

#### Key Settings

| Setting | Value | Description |
|---------|-------|-------------|
| `MODELS["gemini"]` | `gemma-3-27b-it` | Primary LLM model |
| `NUM_ARCHITECT_VARIATIONS` | 2 | Humor concept variations |
| `NUM_STRATEGY_VARIATIONS` | 2 | Delivery style variations |
| `MAX_CHARS` | 900 (EN/ES), 300 (ZH) | Character limits |
| `MAX_WORDS_TASK_B` | 20 | Word limit for Task B |
| `DEFAULT_LLM_PARAMS` | temp=0.9, top_p=0.95 | Default generation params |

#### Module-Specific Temperatures

- HumorArchitect, ContentWriter: `1.0` (more creative)
- HumorJudge: `0.3` (more deterministic)

---

### 3. `pipeline.py` - Unified Pipeline

**Purpose**: Single pipeline handling all task types with parallel execution.

#### Class: `UnifiedHumorPipeline`

**Constructor Parameters**:
- `task_type`: One of `"a1"`, `"a2"`, `"b1"`, `"b2"`

**Key Methods**:

| Method | Description |
|--------|-------------|
| `forward()` | Main entry point - generates and selects best joke |
| `generate_with_variation()` | 2×2 parallel generation strategy |
| `_generate_single_candidate()` | Runs one branch (Architect → Strategist → Writer) |
| `judge_candidates()` | Tournament-style pairwise comparison |
| `_create_branch_predictors()` | Creates fresh predictors for parallel isolation |

#### Signature Registry

```python
SIGNATURE_REGISTRY = {
    "a1": (ContextEnricherA1, HumorArchitectA1, ...),
    "a2": (ContextEnricherA2, HumorArchitectA2, ...),
    "b1": (ContextEnricherB1, HumorArchitectB1, ...),
    "b2": (ContextEnricherB2, HumorArchitectB2, ...),
}
```

All signatures have **identical field names** - only docstrings/descriptions differ.

#### Variation Hints

**Architect Hints** (encourage diversity):
- IRONY or INCONGRUITY
- EXAGGERATION or ABSURDITY
- WORDPLAY or DOUBLE MEANINGS
- SUBVERTED EXPECTATIONS

**Strategy Hints**:
- DEADPAN or DRY
- ENERGETIC or PUNCHY
- SARDONIC or CYNICAL
- PLAYFUL or WHIMSICAL

---

### 4. `signatures_*.py` - DSPy Signatures

**Purpose**: Task-specific DSPy signatures with detailed prompts.

#### Structure (per task type)

Each file contains:
1. `WRITING_TIPS_*` - Guidelines for ContentWriter
2. `EVALUATION_CRITERIA_*` - Criteria for HumorJudge
3. Five DSPy Signature classes:
   - `ContextEnricher`
   - `HumorArchitect`
   - `DeliveryStrategist`
   - `ContentWriter`
   - `HumorJudge`

#### Language Support

| File | Languages |
|------|-----------|
| `signatures_A1.py` | EN, ES, ZH |
| `signatures_A2.py` | EN, ES, ZH |
| `signatures_B1.py` | EN only |
| `signatures_B2.py` | EN only |

#### GTVH Fields in HumorArchitect

- `focal_targets` - Hinge concepts for the joke
- `cognitive_manipulation` - Semantic/logical shift
- `logical_mechanism` - GTVH label (e.g., False Analogy, Irony)
- `expected_script` - Normal expectation (setup)
- `opposing_script` - Hidden reality (punchline)
- `script_opposition` - Abstract clash axis

---

### 5. `main.py` - CLI Entry Point

**Purpose**: Command-line interface for running the pipeline.

#### Usage

```bash
python main.py                     # Test mode, all tasks
python main.py --full              # Full mode, all tasks
python main.py --task a-en         # Task A English only
python main.py --task b1 --full    # Full mode, Task B1
python main.py --full --resume     # Resume from existing outputs
```

#### Arguments

| Flag | Description |
|------|-------------|
| `--task` | `a-en`, `a-es`, `a-zh`, `b1`, `b2`, `all` |
| `--full` | Process all samples (vs test mode) |
| `--resume` | Skip already processed items |
| `--provider` | `gemini` or `openrouter` |

#### Processing Functions

- `process_task_a(language, test_mode, resume)` - Task A processing
- `process_task_b1(test_mode, resume)` - Task B1 with GIF analysis
- `process_task_b2(test_mode, resume)` - Task B2 with GIF + prompt

---

### 6. `data_loader.py` - Data Handling

**Purpose**: TSV file loading, saving, and resume capability.

#### Data Classes

```python
@dataclass
class TaskAItem:
    id: str
    word1: Optional[str]
    word2: Optional[str]
    headline: Optional[str]

@dataclass
class TaskB1Item:
    id: str
    url: str

@dataclass
class TaskB2Item:
    id: str
    url: str
    prompt: str
```

#### Key Functions

| Function | Description |
|----------|-------------|
| `load_task_a(language, test_mode)` | Load Task A items |
| `load_task_b1(test_mode)` | Load Task B1 items |
| `load_task_b2(test_mode)` | Load Task B2 items |
| `save_output(task_name, item_id, text, ...)` | Save single output |
| `load_existing_outputs(task_name, test_mode)` | Load for resume |
| `get_remaining_items(items, existing)` | Filter unprocessed |
| `sanitize_text_for_tsv(text)` | Remove newlines for TSV |

#### TSV Sanitization

```python
def sanitize_text_for_tsv(text: str) -> str:
    """Replace newlines with spaces for valid TSV format."""
    sanitized = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    while '  ' in sanitized:
        sanitized = sanitized.replace('  ', ' ')
    return sanitized.strip()
```

---

### 7. `gif_analyzer.py` - GIF Analysis

**Purpose**: Convert GIFs to text descriptions using Gemini 2.5 Flash Lite.

#### Class: `GIFAnalyzer`

**Process Flow**:
1. Download GIF from URL
2. Save to temp file
3. Convert GIF → MP4 via ffmpeg
4. Upload MP4 to Gemini File API
5. Analyze with task-specific prompt
6. Return description

#### Prompts

- `PROMPT_B1_GIF_ANALYSIS` - Open-ended GIF description
- `PROMPT_B2_GIF_ANALYSIS` - Prompt-contextualized description

#### Key Methods

| Method | Description |
|--------|-------------|
| `_download_gif(url)` | Download GIF bytes |
| `_convert_gif_to_mp4(gif_path)` | ffmpeg conversion |
| `_upload_gif_to_gemini(gif_bytes)` | Upload to File API |
| `_call_with_retry(file, prompt)` | API call with retry |
| `analyze_gif_b1(gif_url)` | Task B1 analysis |
| `analyze_gif_b2(gif_url, prompt)` | Task B2 analysis |

#### Convenience Functions

```python
analyze_gif_for_b1(gif_url)  # Singleton wrapper
analyze_gif_for_b2(gif_url, prompt)
```

---

### 8. `validators.py` - Constraint Checking

**Purpose**: Verify generated jokes meet task requirements.

#### Validation Functions

| Function | Description |
|----------|-------------|
| `check_word_inclusion(joke, word1, word2)` | Both words present |
| `check_char_length(text, language)` | Within char limit |
| `check_word_count(text, max_words)` | Within word limit |
| `check_not_empty(text)` | Has content |

#### Class: `ConstraintValidator`

Combines multiple checks and tracks results:

```python
validator = ConstraintValidator(item_id)
validator.validate_task_a_word_inclusion(joke, word1, word2, language)
passed = validator.all_passed()
failures = validator.get_failures()
```

#### Main Entry Point

```python
validate_joke(joke, task_type, language, word1, word2, item_id)
# Returns: (all_passed: bool, failures: list)
```

---

### 9. `logger.py` - Logging Utilities

**Purpose**: Structured logging with colors and DSPy tracing.

#### Features

- Colored terminal output (DEBUG=cyan, INFO=green, ERROR=red)
- File logging (DEBUG level, stored in `logs/`)
- DSPy trace logging (prompts, completions)
- Token usage logging
- Progress bars

#### Key Functions

| Function | Description |
|----------|-------------|
| `log_section(title)` | Major section header (=====) |
| `log_subsection(title)` | Minor section header (-----) |
| `log_input(data, task_type)` | Log input fields |
| `log_output(data, module_name)` | Log output fields |
| `log_dspy_trace(lm, module_name)` | Log LLM prompt/completion |
| `log_progress(current, total, task)` | Progress bar |
| `log_error(error, context)` | Error with context |
| `log_summary(stats)` | Final statistics |

---

## Configuration Files

### `.env` (Required)

```env
GEMINI_API_KEY=your_api_key_here
API_PROVIDER=gemini
```

### `config.py` Key Settings

```python
# Logging
LOG_LEVEL = "INFO"              # DEBUG, INFO, WARNING, ERROR
LOG_TOKEN_USAGE = True          # Track API token consumption
PROMPT_TUNING_MODE = False      # Enable clean output mode for prompt analysis

# Variation Strategy  
NUM_ARCHITECT_VARIATIONS = 2    # Different humor concepts
NUM_STRATEGY_VARIATIONS = 2     # Different delivery styles per concept
NUM_CANDIDATES = 4              # Total jokes = arch × strat

# GIF Processing
GIF_DOWNLOAD_TIMEOUT = 15       # Seconds to wait for GIF download
GIF_CONVERSION_TIMEOUT = 60     # Seconds for GIF-to-video conversion
```

### Prompt Tuning Mode

Set `PROMPT_TUNING_MODE = True` in `config.py` to get clean, organized output for analyzing prompt effectiveness:

**What it shows:**
- Input item header
- Context enrichment results
- Each candidate's humor architecture and delivery strategy
- Final joke for each branch
- Winning joke selection

**What it hides:**
- Timestamps
- Log level tags
- Token counts
- DSPy traces
- Rate limit messages

**Example output:**
```
═══════════════════════════════════════════════════════════════════════════════
  🎭 HEADLINE JOKE - current
═══════════════════════════════════════════════════════════════════════════════

  INPUT: Scientists Discover New Species of Deep-Sea Fish...

──────────────────────────────────────────────────────────────────────────
  📋 CONTEXT ANALYSIS
──────────────────────────────────────────────────────────────────────────
  situation: Scientific discovery announcement about unusual marine life...
  potential_targets:
    • scientists
    • deep-sea creatures
    • discovery process

──────────────────────────────────────────────────────────────────────────
  🎯 CANDIDATE [1,1]
──────────────────────────────────────────────────────────────────────────

  HUMOR ARCHITECTURE:
    focal_targets: Scientists' obsession with naming things
    cognitive_manipulation: Ironic juxtaposition
    ...

  GENERATED JOKE:
    ┌────────────────────────────────────────────────────────────────┐
    │ Scientists discover new deep-sea fish, immediately argue about │
    │ who gets to name it after themselves                           │
    └────────────────────────────────────────────────────────────────┘
```

### `requirements.txt`

Key dependencies:
- `dspy==3.0.4` - DSPy framework
- `litellm` - LLM abstraction layer
- `google-generativeai` - Gemini SDK for GIF analysis
- `python-dotenv` - Environment variable loading

---

## Usage Examples

### Basic Test Run

```bash
cd Final
python main.py --task a-en
```

### Full Production Run

```bash
python main.py --full --resume
```

### Process Single Task Type

```bash
python main.py --task b1 --full
```

---

## Output Format

### TSV Structure

```tsv
id	text
en_0001	The generated joke text here
en_0002	Another generated joke
```

### Output Directories

- Test mode: `test_outputs/`
- Full mode: `outputs/`
- Logs: `logs/run_YYYYMMDD_HHMMSS.log`

---

## Token Tracking

The pipeline tracks all token usage for cost analysis:

```python
from api import get_token_summary

summary = get_token_summary()
# {
#     "total_input_tokens": 12345,
#     "total_output_tokens": 6789,
#     "total_tokens": 19134,
#     "num_calls": 42
# }
```

---

## Error Handling

### Retry Strategy

Rate limits and transient errors trigger automatic retry with exponential backoff:
- 5s, 5s, 10s, 20s, 30s, 30s, 30s, 2min, 2min, 2min

### Graceful Degradation

- Parallel branches are independent - one failure doesn't affect others
- Failed items save `[ERROR: message]` placeholder
- Resume capability skips already-processed items

### Error Markers in Output

```tsv
id	text
en_2007	[ERROR: BadRequestError at json_repair.parse: ...]
```

---

## Development Notes

### Thread Safety

- `TokenTracker` and `RetryTracker` use locks for parallel access
- Each parallel branch creates its own predictor instances
- No shared mutable state between branches

### DSPy Configuration

```python
# Avoid JSON mode issues with gemma-3-27b-it
dspy.configure(adapter=dspy.ChatAdapter())
```

### GIF Processing Requirements

- Requires `ffmpeg` installed on system
- GIFs are converted to MP4 for Gemini video API
- Temp files are cleaned up after processing

---

## Version Information

- DSPy: 3.0.4
- Model: gemma-3-27b-it (via Gemini API)
- GIF Analyzer: gemini-2.5-flash-lite
- Python: 3.10+
