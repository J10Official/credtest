#!/usr/bin/env python3
"""
MWAHAHA Humor Generation Pipeline - Main Entry Point

Usage:
    python main.py                           # Test mode, all tasks
    python main.py --full                    # Full mode, all tasks
    python main.py --task a-en               # Test mode, Task A English only
    python main.py --task b1 --full          # Full mode, Task B1 only
    python main.py --full --resume           # Full mode with resume capability

Tasks:
    a-en    Task A English (headlines + word inclusion)
    a-es    Task A Spanish
    a-zh    Task A Chinese
    b1      Task B1 (GIF captions)
    b2      Task B2 (GIF + prompt captions)
    all     All tasks (default)
"""

import argparse
import sys
from datetime import datetime
from typing import Optional

from config import (
    OUTPUT_DIR,
    TEST_OUTPUT_DIR,
    LOG_DIR,
    SAVE_COMPLETE_OUTPUT,
)
import config  # For modifying SAVE_COMPLETE_OUTPUT at runtime
from api import configure_dspy, get_token_summary, reset_token_tracker, get_retry_summary, get_retry_formatted_summary, reset_all_trackers, is_openrouter_model_free, get_openrouter_model_name
from gif_analyzer import analyze_gif_for_b1, analyze_gif_for_b2
from data_loader import (
    load_task_a,
    load_task_b1,
    load_task_b2,
    load_existing_outputs,
    get_remaining_items,
    save_output,
    save_complete_output,
    get_task_file_name,
)
from pipeline import UnifiedHumorPipeline
from validators import validate_joke
from logger import (
    logger,
    log_section,
    log_progress,
    log_summary,
    log_error,
    create_run_logger,
    add_file_handler_to_logger,
)


def process_task_a(
    language: str,
    test_mode: bool = True,
    resume: bool = False,
) -> dict:
    """
    Process Task A for a specific language.
    
    Args:
        language: Language code ("en", "es", "zh")
        test_mode: If True, process limited samples
        resume: If True, skip already processed items
    
    Returns:
        Statistics dictionary
    """
    log_section(f"📰 TASK A - {language.upper()}")
    
    # Sensitive topics that may trigger LLM censorship (headline task only)
    # These are geopolitically sensitive topics that DeepSeek/other Chinese models may refuse
    # Includes translations for ES and ZH matching
    SENSITIVE_TOPICS = {
        "en": [
            "china", "chinese", "beijing", "xi jinping", "ccp", "prc",
            "taiwan", "hong kong", "tibet", "uyghur", "xinjiang",
            "tiananmen", "dalai lama", "falun gong",
        ],
        "es": [
            "china", "chino", "chinos", "pekín", "beijing", "xi jinping", "pcc",
            "taiwán", "taiwan", "hong kong", "tíbet", "tibet", "uigur", "xinjiang",
            "tiananmen", "dalái lama", "falun gong",
        ],
        "zh": [
            "中国", "中國", "北京", "习近平", "習近平", "共产党", "共產黨",
            "台湾", "台灣", "香港", "西藏", "维吾尔", "維吾爾", "新疆",
            "天安门", "天安門", "达赖喇嘛", "達賴喇嘛", "法轮功", "法輪功",
        ],
    }
    
    def contains_sensitive_topic(text: str, lang: str) -> bool:
        """Check if text contains any sensitive topics for the given language."""
        text_lower = text.lower()
        topics = SENSITIVE_TOPICS.get(lang, SENSITIVE_TOPICS["en"])
        return any(topic.lower() in text_lower for topic in topics)
    
    # Load data
    items = load_task_a(language, test_mode=test_mode)
    
    if not items:
        logger.warning(f"No items found for Task A {language}")
        return {"processed": 0, "errors": 0}
    
    # Check for existing outputs if resuming
    task_name = get_task_file_name("a", language)
    existing = {}
    if resume:
        # Support resume in both test and full mode, and for complete mode
        existing = load_existing_outputs(
            task_name, 
            test_mode=test_mode,
            complete_mode=config.SAVE_COMPLETE_OUTPUT
        )
        items = get_remaining_items(items, existing)
    
    if not items:
        logger.info("All items already processed!")
        return {"processed": 0, "skipped": len(existing), "errors": 0}
    
    # Initialize pipelines (unified pipeline with task-specific signatures)
    headline_pipeline = UnifiedHumorPipeline("a1")
    word_pipeline = UnifiedHumorPipeline("a2")
    
    stats = {"processed": 0, "headlines": 0, "word_inclusion": 0, "errors": 0}
    
    for i, item in enumerate(items):
        try:
            log_progress(i + 1, len(items), f"Task A {language.upper()}")
            
            if item.is_headline_task:
                # Headline-based joke - with censorship detection
                try:
                    joke, all_candidates = headline_pipeline.forward(
                        original_input=item.headline,
                        language=language,
                        skip_judge=config.SAVE_COMPLETE_OUTPUT,  # Skip judge in --complete mode
                    )
                except Exception as first_error:
                    # First attempt failed - check if it's a sensitive topic
                    if contains_sensitive_topic(item.headline, language):
                        # One retry already happened in call_with_retry, skip with censorship message
                        logger.warning(f"⚠️ {item.id}: Sensitive topic detected, likely censorship")
                        save_output(task_name, item.id, "[CENSORED: Sensitive geopolitical topic]", test_mode=test_mode)
                        stats["errors"] += 1
                        continue
                    else:
                        # Not a sensitive topic, re-raise to trigger normal error handling
                        raise first_error
                
                # Save complete output if enabled
                save_complete_output(
                    task_name, item.id, joke, all_candidates, test_mode=test_mode,
                    original_input=item.headline, language=language, task_type="a1"
                )
                stats["headlines"] += 1
            elif item.is_word_inclusion_task:
                # Word inclusion joke
                joke, all_candidates = word_pipeline.forward(
                    original_input=f"{item.word1}, {item.word2}",
                    language=language,
                    word1=item.word1,
                    word2=item.word2,
                    skip_judge=config.SAVE_COMPLETE_OUTPUT,  # Skip judge in --complete mode
                )
                
                # Save complete output if enabled
                save_complete_output(
                    task_name, item.id, joke, all_candidates, test_mode=test_mode,
                    original_input=f"{item.word1}, {item.word2}",
                    language=language, word1=item.word1, word2=item.word2, task_type="a2"
                )
                stats["word_inclusion"] += 1
            else:
                logger.warning(f"Item {item.id} has neither headline nor words")
                continue
            
            # Save output (skip if --complete mode since there's no winner)
            if joke is not None:
                save_output(task_name, item.id, joke, test_mode=test_mode)
                logger.info(f"✅ {item.id}: {joke[:80]}...")
            else:
                logger.info(f"✅ {item.id}: Generated {len(all_candidates)} candidates (no judging)")
            stats["processed"] += 1
            
        except KeyboardInterrupt:
            logger.warning("Interrupted by user. Progress has been saved.")
            break
        except Exception as e:
            log_error(e, f"processing {item.id}")
            stats["errors"] += 1
            # Save a placeholder to mark as attempted
            save_output(task_name, item.id, f"[ERROR: {str(e)[:50]}]", test_mode=test_mode)
    
    return stats


def process_task_b1(
    test_mode: bool = True,
    resume: bool = False,
) -> dict:
    """
    Process Task B1 (GIF captions).
    
    Uses Gemini 2.5 Flash Lite to analyze GIFs and convert them to
    detailed textual descriptions for the humor generation pipeline.
    """
    log_section("🖼️ TASK B1 - GIF CAPTIONS")
    
    # Load data
    items = load_task_b1(test_mode=test_mode)
    
    if not items:
        logger.warning("No items found for Task B1")
        return {"processed": 0, "errors": 0}
    
    # Check for existing outputs if resuming
    task_name = "task-b1"
    existing = {}
    if resume:
        existing = load_existing_outputs(
            task_name, 
            test_mode=test_mode,
            complete_mode=config.SAVE_COMPLETE_OUTPUT
        )
        items = get_remaining_items(items, existing)
    
    if not items:
        logger.info("All items already processed!")
        return {"processed": 0, "skipped": len(existing), "errors": 0}
    
    # Initialize pipeline
    pipeline = UnifiedHumorPipeline("b1")
    
    stats = {"processed": 0, "errors": 0, "gif_analysis_failed": 0}
    
    for i, item in enumerate(items):
        try:
            log_progress(i + 1, len(items), "Task B1")
            
            # Analyze the GIF using Gemini 2.5 Flash Lite
            logger.info(f"🎬 Analyzing GIF: {item.url[:60]}...")
            gif_description = analyze_gif_for_b1(item.url)
            
            if not gif_description:
                logger.error(f"❌ Failed to analyze GIF for {item.id}")
                stats["gif_analysis_failed"] += 1
                stats["errors"] += 1
                save_output(task_name, item.id, "[ERROR: GIF analysis failed]", test_mode=test_mode)
                continue
            
            logger.info(f"📝 GIF description: {gif_description[:150]}...")
            
            # Generate caption using the humor pipeline
            caption, all_candidates = pipeline.forward(
                original_input=gif_description,
                skip_judge=config.SAVE_COMPLETE_OUTPUT,  # Skip judge in --complete mode
            )
            
            # Save complete output if enabled
            save_complete_output(
                task_name, item.id, caption, all_candidates, test_mode=test_mode,
                original_input=gif_description, task_type="b1"
            )
            
            # Save output (skip if --complete mode since there's no winner)
            if caption is not None:
                save_output(task_name, item.id, caption, test_mode=test_mode)
                logger.info(f"✅ {item.id}: {caption}")
            else:
                logger.info(f"✅ {item.id}: Generated {len(all_candidates)} candidates (no judging)")
            stats["processed"] += 1
            
        except KeyboardInterrupt:
            logger.warning("Interrupted by user. Progress has been saved.")
            break
        except Exception as e:
            log_error(e, f"processing {item.id}")
            stats["errors"] += 1
            save_output(task_name, item.id, f"[ERROR: {str(e)[:50]}]", test_mode=test_mode)
    
    return stats


def process_task_b2(
    test_mode: bool = True,
    resume: bool = False,
) -> dict:
    """
    Process Task B2 (GIF + prompt captions).
    
    Uses Gemini 2.5 Flash Lite to analyze GIFs in the context of
    their fill-in-the-blank prompts for the humor generation pipeline.
    """
    log_section("🖼️ TASK B2 - GIF + PROMPT CAPTIONS")
    
    # Load data
    items = load_task_b2(test_mode=test_mode)
    
    if not items:
        logger.warning("No items found for Task B2")
        return {"processed": 0, "errors": 0}
    
    # Check for existing outputs if resuming
    task_name = "task-b2"
    existing = {}
    if resume:
        existing = load_existing_outputs(
            task_name, 
            test_mode=test_mode,
            complete_mode=config.SAVE_COMPLETE_OUTPUT
        )
        items = get_remaining_items(items, existing)
    
    if not items:
        logger.info("All items already processed!")
        return {"processed": 0, "skipped": len(existing), "errors": 0}
    
    # Initialize pipeline
    pipeline = UnifiedHumorPipeline("b2")
    
    stats = {"processed": 0, "errors": 0, "gif_analysis_failed": 0}
    
    for i, item in enumerate(items):
        try:
            log_progress(i + 1, len(items), "Task B2")
            
            # Analyze the GIF with context of the prompt using Gemini 2.5 Flash Lite
            logger.info(f"🎬 Analyzing GIF: {item.url[:60]}...")
            logger.info(f"📝 Prompt: {item.prompt}")
            gif_description = analyze_gif_for_b2(item.url, item.prompt)
            
            if not gif_description:
                logger.error(f"❌ Failed to analyze GIF for {item.id}")
                stats["gif_analysis_failed"] += 1
                stats["errors"] += 1
                save_output(task_name, item.id, "[ERROR: GIF analysis failed]", test_mode=test_mode)
                continue
            
            logger.info(f"📝 GIF description: {gif_description[:150]}...")
            
            # Generate caption using the humor pipeline
            # For B2, we pass both the GIF description and the prompt
            pipeline_input = f"GIF Description: {gif_description}\n\nPrompt to Complete: {item.prompt}"
            caption, all_candidates = pipeline.forward(
                original_input=pipeline_input,
                skip_judge=config.SAVE_COMPLETE_OUTPUT,  # Skip judge in --complete mode
            )
            
            # Save complete output if enabled
            save_complete_output(
                task_name, item.id, caption, all_candidates, test_mode=test_mode,
                original_input=pipeline_input, task_type="b2"
            )
            
            # Save output (skip if --complete mode since there's no winner)
            if caption is not None:
                save_output(task_name, item.id, caption, test_mode=test_mode)
                logger.info(f"✅ {item.id}: {caption}")
            else:
                logger.info(f"✅ {item.id}: Generated {len(all_candidates)} candidates (no judging)")
            stats["processed"] += 1
            
        except KeyboardInterrupt:
            logger.warning("Interrupted by user. Progress has been saved.")
            break
        except Exception as e:
            log_error(e, f"processing {item.id}")
            stats["errors"] += 1
            save_output(task_name, item.id, f"[ERROR: {str(e)[:50]}]", test_mode=test_mode)
    
    return stats


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description="MWAHAHA Humor Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--task",
        choices=["a-en", "a-es", "a-zh", "b1", "b2", "all"],
        default="all",
        help="Task to run (default: all)"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run in full mode (process all samples)"
    )
    
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing outputs (only in full mode)"
    )
    
    parser.add_argument(
        "--complete",
        action="store_true",
        help="Save complete output (all candidates + LLM outputs as JSON)"
    )
    
    parser.add_argument(
        "--provider",
        choices=["gemini", "openrouter"],
        default=None,
        help="API provider to use (default: from DEFAULT_MODEL in config.py)"
    )
    
    args = parser.parse_args()
    
    # Setup
    test_mode = not args.full
    mode_str = "FULL" if args.full else "TEST"
    
    # Enable complete output if requested
    if args.complete:
        config.SAVE_COMPLETE_OUTPUT = True
        logger.info("📋 Complete output mode enabled (all candidates + LLM outputs)")
    
    # Create output directories
    output_dir = OUTPUT_DIR if args.full else TEST_OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    
    # Create complete output directory if needed
    if config.SAVE_COMPLETE_OUTPUT:
        from config import COMPLETE_OUTPUT_DIR
        complete_dir = COMPLETE_OUTPUT_DIR / ("full" if args.full else "test")
        complete_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Complete output directory: {complete_dir}")
    
    # Create run-specific logger that writes to file
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = add_file_handler_to_logger(f"run_{run_id}.log")
    
    log_section(f"🎭 MWAHAHA PIPELINE - {mode_str} MODE")
    logger.info(f"Task: {args.task}")
    logger.info(f"Provider: {args.provider}")
    logger.info(f"Resume: {args.resume}")
    logger.info(f"📁 Log file: {log_file_path}")
    
    # Check for paid OpenRouter model and warn user
    # Note: Provider is determined from DEFAULT_MODEL in config, --provider is a fallback
    model_name = get_openrouter_model_name()
    if "openrouter" in model_name or args.provider == "openrouter":
        if not is_openrouter_model_free(model_name):
            logger.warning(f"⚠️  WARNING: OpenRouter model '{model_name}' is NOT a free model!")
            logger.warning(f"⚠️  This will incur API costs. Free models must end with ':free'")
            logger.warning(f"⚠️  Example free model: meta-llama/llama-3.3-70b-instruct:free")
            print()
            confirm = input("Do you want to proceed with this PAID model? (yes/no): ").strip().lower()
            if confirm != "yes":
                logger.info("Aborted by user. Please update DEFAULT_MODEL in config.py to use a free model.")
                sys.exit(0)
            logger.info("User confirmed paid model usage. Proceeding...")
        else:
            logger.info(f"✅ Using free OpenRouter model: {model_name}")
    
    # Configure API
    try:
        print(f"\n🔍 DEBUG: args.provider = {args.provider}")
        print(f"🔍 DEBUG: config.DEFAULT_MODEL = {config.DEFAULT_MODEL}")
        print(f"🔍 DEBUG: config.API_PROVIDER = {config.API_PROVIDER}\n")
        
        lm = configure_dspy(provider_name=args.provider)
        # Determine actual provider used
        if args.provider:
            provider_used = args.provider
        else:
            from config import parse_model_spec
            provider_used, _ = parse_model_spec(config.DEFAULT_MODEL)
            provider_used = provider_used or config.API_PROVIDER
        print(f"✅ API configured: {provider_used}\n")
        logger.info(f"✅ API configured: {provider_used}")
    except Exception as e:
        logger.error(f"❌ Failed to configure API: {e}")
        logger.error("Make sure API keys are set in .env file")
        sys.exit(1)
    
    # Reset all trackers (tokens and retries)
    reset_all_trackers()
    
    # Track overall stats
    all_stats = {}
    start_time = datetime.now()
    
    try:
        # Run selected tasks
        if args.task in ("a-en", "all"):
            all_stats["a-en"] = process_task_a("en", test_mode, args.resume)
        
        if args.task in ("a-es", "all"):
            all_stats["a-es"] = process_task_a("es", test_mode, args.resume)
        
        if args.task in ("a-zh", "all"):
            all_stats["a-zh"] = process_task_a("zh", test_mode, args.resume)
        
        if args.task in ("b1", "all"):
            all_stats["b1"] = process_task_b1(test_mode, args.resume)
        
        if args.task in ("b2", "all"):
            all_stats["b2"] = process_task_b2(test_mode, args.resume)
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Pipeline interrupted. Partial results have been saved.")
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    token_summary = get_token_summary()
    retry_summary = get_retry_summary()
    
    log_summary({
        "Duration": str(duration),
        "Mode": mode_str,
        "Output Directory": str(output_dir),
        "Total Input Tokens": token_summary["total_input_tokens"],
        "Total Output Tokens": token_summary["total_output_tokens"],
        "Total API Calls": token_summary["total_api_calls"],
        "Total Retries": retry_summary["total_retries"],
        **{f"{task} processed": stats.get("processed", 0) for task, stats in all_stats.items()},
        **{f"{task} errors": stats.get("errors", 0) for task, stats in all_stats.items()},
    })
    
    # Log retry breakdown if there were any retries
    if retry_summary["total_retries"] > 0:
        logger.info("\n📊 Retry Breakdown by Module:")
        for module, counts in sorted(retry_summary["by_module"].items()):
            total = counts["rate_limit"] + counts["transient"]
            details = []
            if counts["rate_limit"] > 0:
                details.append(f"{counts['rate_limit']} rate limit")
            if counts["transient"] > 0:
                details.append(f"{counts['transient']} transient")
            logger.info(f"   {module}: {total} ({', '.join(details)})")
    
    logger.info(f"\n✨ Pipeline complete! Outputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
