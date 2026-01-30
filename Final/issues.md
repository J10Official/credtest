# MWAHAHA Pipeline - Issues & Improvements

This document catalogs all identified issues, potential bugs, and improvement opportunities in the MWAHAHA humor generation pipeline.

---

## Critical Issues

### 1. ❌ Intermittent JSON Mode Errors from DSPy

**Severity**: Critical  
**Location**: [api.py#L266](api.py#L266), [pipeline.py](pipeline.py)  
**Status**: ✅ Fixed

**Problem**:  
Despite configuring `dspy.ChatAdapter()` to avoid JSON mode, intermittent `BadRequestError` errors still occur with messages like:
```
BadRequestError at json_repair.parse: Could not parse the given string
```

This is a race condition in DSPy's internal adapter selection that sometimes falls back to JSON mode when `gemma-3-27b-it` doesn't support it.

**Evidence**:  
- Item `en_2007` failed with this error
- Item `en_2006` succeeded because 3/4 parallel branches worked

**Impact**:  
- Random failures that are hard to reproduce
- Requires manual re-processing of failed items

**Fix Applied**:
1. Added JSON parse error detection in `with_retry` decorator (api.py)
2. Automatic ChatAdapter re-enforcement when JSON error is detected
3. JSON errors now trigger retry instead of immediate failure
4. Added `json_parse` as tracked error type in RetryTracker

---

### 2. ⚠️ ChatAdapter Configuration Only at Provider Init

**Severity**: High  
**Location**: [api.py#L265-266](api.py#L265-266), [pipeline.py#L320](pipeline.py#L320)  
**Status**: ✅ Fixed

**Problem**:  
`dspy.configure(adapter=dspy.ChatAdapter())` is only called once in `GeminiProvider.configure()`. In parallel execution contexts, there's no guarantee this persists across all threads.

**Evidence**:  
The intermittent JSON mode errors suggest the adapter configuration doesn't always hold.

**Fix Applied**:
Added ChatAdapter re-enforcement at the start of each parallel branch in `_generate_single_candidate()`:
```python
# Re-enforce ChatAdapter for this thread to prevent JSON mode issues
dspy.configure(adapter=dspy.ChatAdapter())
```

This ensures every parallel thread explicitly configures the adapter before making any API calls.

---

### 3. ⚠️ No Retry on JSON Parse Errors

**Severity**: High  
**Location**: [api.py#L170-210](api.py#L170-210)  
**Status**: ✅ Fixed

**Problem**:  
The `with_retry` decorator only handles rate limits and transient errors. JSON parsing failures (BadRequestError) are NOT retried because they're classified as non-retryable.

**Previous Logic**:
```python
if not (is_rate_limit or is_transient):
    logger.error(f"💀 Non-retryable error. Aborting.")
    raise
```

**Fix Applied**:
Added JSON error detection and retry logic:
```python
# Check if it's a JSON mode/parse error (DSPy race condition)
is_json_error = any(term in error_str for term in [
    "json_repair", "could not parse", "json mode",
    "badrequest", "bad request", "response_mime_type"
])

if is_json_error:
    # Re-enforce ChatAdapter to prevent JSON mode on retry
    logger.warning(f"🔧 JSON mode error detected. Re-enforcing ChatAdapter...")
    dspy.configure(adapter=dspy.ChatAdapter())

if not (is_rate_limit or is_transient or is_json_error):
    # Not a retryable error, raise immediately
    raise
```

Also updated RetryTracker to track `json_parse` as a third error category.

---

## Medium Issues

### 4. ⚠️ Token Tracking May Miss Usage Data

**Severity**: Medium  
**Location**: [api.py#L420-460](api.py#L420-460), [logger.py#L215-255](logger.py#L215-255)  
**Status**: ✅ Fixed

**Problem**:  
Token tracking has multiple fallback paths trying to find usage data, but often returns 0.

**Fix Applied**:
1. Created shared `utils.py` module with `extract_token_usage()` function
2. Updated `api.py:track_tokens()` to use shared utility
3. Updated `logger.py:log_dspy_trace()` to use shared utility
4. Debug logging now happens in one place when tokens are 0

---

### 5. ⚠️ Singleton Pattern for GIFAnalyzer May Cause Issues

**Severity**: Medium  
**Location**: [gif_analyzer.py#L495-510](gif_analyzer.py#L495-510)  
**Status**: ✅ Fixed

**Problem**:
The singleton pattern was not thread-safe. In parallel execution, multiple threads could create instances simultaneously.

**Fix Applied**:
Implemented double-checked locking pattern:
```python
_analyzer_lock = threading.Lock()

def get_gif_analyzer() -> GIFAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        with _analyzer_lock:
            if _analyzer_instance is None:
                _analyzer_instance = GIFAnalyzer()
    return _analyzer_instance
```

---

### 6. ⚠️ Duplicate Token Extraction Logic

**Severity**: Medium  
**Location**: [utils.py](utils.py) (new), [api.py](api.py), [logger.py](logger.py)  
**Status**: ✅ Fixed

**Problem**:  
The same token extraction logic was duplicated in `api.py` and `logger.py`.

**Fix Applied**:
Extracted to shared utility in new `utils.py` module:
```python
# utils.py
def extract_token_usage(last_call: dict) -> Tuple[int, int]:
    """Extract (input_tokens, output_tokens) from DSPy call history."""
    # Single implementation handling all formats
```

Both `api.py:track_tokens()` and `logger.py:log_dspy_trace()` now import and use this shared function.

---

### 7. ⚠️ Error Placeholders Break Resume Logic

**Severity**: Medium  
**Location**: [main.py#L135](main.py#L135), [data_loader.py#L253-285](data_loader.py#L253-285)  
**Status**: ✅ Fixed

**Problem**:  
When an error occurs, a placeholder is saved:
```python
save_output(task_name, item.id, f"[ERROR: {str(e)[:50]}]", test_mode=test_mode)
```

On resume, `load_existing_outputs()` includes these error entries, so failed items are NOT re-processed.

**Impact**:  
Cannot automatically retry failed items without manual cleanup.

**Fix Applied**:
Updated `get_remaining_items()` to detect and retry error entries:
```python
def get_remaining_items(items: list, existing_outputs: dict) -> list:
    remaining = []
    for item in items:
        if item.id not in existing_outputs:
            remaining.append(item)  # Not processed yet
        elif existing_outputs[item.id].startswith("[ERROR"):
            remaining.append(item)  # Previously failed - retry
    return remaining
```

Now on `--resume`, items with `[ERROR: ...]` placeholders will be automatically retried.


---

## Low Issues

### 9. 📝 Hardcoded Variation Hints - Why They Exist

**Severity**: Low  
**Location**: [pipeline.py#L420-440](pipeline.py#L420-440)

**Current Implementation**:
```python
ARCHITECT_HINTS = [
    "Focus on IRONY or INCONGRUITY...",
    "Focus on EXAGGERATION or ABSURDITY...",
    ...
]
```

**Why Variation Hints Were Added (Value Analysis)**:

The signatures (e.g., `HumorArchitect`) already contain detailed GTVH guidance in their docstrings and field descriptions. So why add variation hints?

**The Problem They Solve**: Without hints, the 2×2 parallel branches would often converge on similar outputs because:
1. Same input → same context analysis → similar humor concepts
2. LLMs have "default modes" - they gravitate toward certain humor types
3. Temperature alone doesn't guarantee diversity in *direction*, just randomness

**What Signatures Provide vs. What Hints Provide**:

| Signatures Provide | Hints Provide |
|-------------------|---------------|
| General GTVH framework | Specific direction per branch |
| List of possible mechanisms (Irony, Exaggeration, etc.) | "Use THIS mechanism for THIS branch" |
| Quality guidelines | Diversity enforcement |
| Evaluation criteria | Exploration strategy |

**Example**: The signature lists `[False Analogy, Literal Interpretation, Role Reversal, Exaggeration, ...]` as valid mechanisms. Without hints, all 4 branches might choose "Irony" because it's common. The hints force Branch 1 toward Irony, Branch 2 toward Exaggeration, ensuring coverage.

**Analogy**: Signatures are like a cookbook with many recipes. Hints are like assigning "you make the appetizer, you make the main course" - ensuring the full menu gets covered rather than everyone making the same dish.

**Why This Is Still Listed as an Issue**:

The hints ARE valuable, but the implementation concern is:
- Hardcoded in pipeline.py makes A/B testing different hint strategies difficult
- Can't easily experiment with more/fewer hint categories
- Configuration-driven hints would enable research iteration

**Recommended Fix** (if desired):
Move to `config.py` for easier experimentation:
```python
# config.py
ARCHITECT_VARIATION_HINTS = [...]
STRATEGY_VARIATION_HINTS = [...]
NUM_ARCHITECT_VARIATIONS = 2  # Already there
```

---

### 10. 📝 No Input Validation in Pipeline

**Severity**: Low  
**Location**: [pipeline.py#L572-595](pipeline.py#L572-595)  
**Status**: ✅ Fixed

**Problem**:  
`forward()` accepted empty strings without validation.

**Fix Applied**:
Added validation at the start of `forward()`:
```python
if not original_input or not original_input.strip():
    raise ValueError("original_input cannot be empty or whitespace only")
```

---

### 11. 📝 Inconsistent Logging Levels

**Severity**: Low  
**Location**: [logger.py](logger.py), various modules  
**Status**: ✅ Fixed

**Problem**:  
Some errors use `logger.error()`, others use `log_error()`. Some debug info uses `logger.debug()`, others `logger.info()`.

**Fix Applied**:
1. Established consistent logging patterns:
   - `ERROR`: Failures that affect output
   - `WARNING`: Recoverable issues
   - `INFO`: Progress updates and module outputs
   - `DEBUG`: Inputs and internal state
   
2. Added **Prompt Tuning Mode** (`PROMPT_TUNING_MODE` in config.py):
   - Custom log level `PROMPT_OUTPUT` (25) between INFO and WARNING
   - Clean, organized output showing only generated content
   - No timestamps or noise - just module outputs
   - Perfect for analyzing prompt effectiveness

3. New prompt tuning functions in logger.py:
   - `pt_item_start()`: Header for each input item
   - `pt_context()`: Context enrichment output
   - `pt_candidate_joke()`: Full candidate with architecture and strategy
   - `pt_judgment()`: Final selection display
   - `pt_section()`, `pt_subsection()`, `pt_field()`: Clean formatting

4. Improved standard logging consistency:
   - `log_input()` now takes module_name, uses DEBUG level
   - `log_output()` now supports branch_id, auto-triggers prompt tuning
   - Both functions have consistent formatting

---

### 12. 📝 Missing Type Hints in Some Functions

**Severity**: Low  
**Location**: Various

**Problem**:  
Some functions lack return type hints:
```python
def get_writing_tips(task: str, language: str = "en"):  # -> str?
def extract_outputs(prediction: Any):  # -> dict?
```

**Recommended Fix**:
Add complete type annotations for IDE support and documentation.

---


### 14. 📝 No Timeout on GIF Download

**Severity**: Low  
**Location**: [gif_analyzer.py#L210](gif_analyzer.py#L210), [config.py](config.py)  
**Status**: ✅ Fixed

**Problem**:
30 seconds was too long for batch processing.

**Fix Applied**:
Made timeout configurable in config.py:
```python
# config.py
GIF_DOWNLOAD_TIMEOUT = 15  # Reduced from 30s
GIF_CONVERSION_TIMEOUT = 60
```

Updated `gif_analyzer.py` to use `GIF_DOWNLOAD_TIMEOUT` from config.

---

## Improvement Opportunities

### 15. 🚀 Add Caching for GIF Descriptions

**Location**: [gif_analyzer.py](gif_analyzer.py)

Currently, GIF analysis is always performed. For development/testing, caching would speed up iterations.

```python
# Could use functools.lru_cache or disk-based cache
@lru_cache(maxsize=100)
def analyze_gif_cached(gif_url: str, cache_key: str) -> Optional[str]:
    ...
```

---

### 16. 🚀 Add Batch Processing Support

**Location**: [main.py](main.py)

Currently processes items one at a time. Could batch multiple items for better throughput:
```python
async def process_batch(items: list, batch_size: int = 5):
    ...
```

---


### 19. 🚀 Add Structured Error Reporting

**Location**: New module

Currently errors are just logged. Could add:
```python
class ErrorReport:
    item_id: str
    error_type: str
    error_message: str
    timestamp: datetime
    module: str
    recoverable: bool
```

---

## Summary Table

| ID | Issue | Severity | Status |
|----|-------|----------|--------|
| 1 | Intermittent JSON Mode Errors | Critical | ✅ Fixed |
| 2 | ChatAdapter Only at Init | High | ✅ Fixed |
| 3 | No Retry on JSON Parse | High | ✅ Fixed |
| 4 | Token Tracking Misses Data | Medium | ✅ Fixed |
| 5 | GIFAnalyzer Singleton Not Thread-Safe | Medium | ✅ Fixed |
| 6 | Duplicate Token Extraction | Medium | ✅ Fixed |
| 7 | Error Placeholders Break Resume | Medium | ✅ Fixed |
| 8 | Multiple HumorJudge Calls | Medium | By Design |
| 9 | Hardcoded Variation Hints | Low | By Design |
| 10 | No Input Validation | Low | ✅ Fixed |
| 11 | Inconsistent Logging | Low | Open |
| 12 | Missing Type Hints | Low | Open |
| 13 | Confusing Test Limits | Low | Open |
| 14 | No Configurable GIF Timeout | Low | ✅ Fixed |

---

## Recommended Priority

### Immediate (Before Production)
1. ~~Fix ChatAdapter thread safety (#2)~~ ✅ Fixed
2. ~~Add JSON error retry (#3)~~ ✅ Fixed
3. ~~Fix resume to retry errors (#7)~~ ✅ Fixed

### Short-Term
4. ~~Fix token tracking (#4)~~ ✅ Fixed
5. ~~Thread-safe GIFAnalyzer (#5)~~ ✅ Fixed
6. ~~DRY token extraction (#6)~~ ✅ Fixed

### Long-Term
7. Caching (#15)
8. Batch processing (#16)
