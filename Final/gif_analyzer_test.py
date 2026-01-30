#!/usr/bin/env python3
"""
GIF Analyzer Test Module

Quick test script to verify the GIF analyzer works correctly.
Tests both B1 (GIF only) and B2 (GIF + prompt) analysis.

Usage:
    python gif_analyzer_test.py --task b1    # Test B1 only
    python gif_analyzer_test.py --task b2    # Test B2 only  
    python gif_analyzer_test.py              # Test both (default)
    
NOTE: We have limited RPD (20 requests per day) for Gemini 2.5 Flash Lite.
      Don't spam this test. Each run uses 1-2 API calls.
"""

import sys
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("gif_analyzer_test")

# Add parent to path for imports
sys.path.insert(0, '.')

from gif_analyzer import GIFAnalyzer, analyze_gif_for_b1, analyze_gif_for_b2
from data_loader import load_task_b1, load_task_b2


def test_b1_analysis():
    """Test GIF analysis for Task B1 (GIF only)."""
    print("\n" + "="*70)
    print("🧪 TEST: Task B1 - GIF Analysis (Open-ended)")
    print("="*70)
    
    # Load one item from B1
    items = load_task_b1(test_mode=True)
    
    if not items:
        print("❌ No B1 items found!")
        return False
    
    item = items[0]
    print(f"\n📎 Test GIF: {item.id}")
    print(f"🔗 URL: {item.url}")
    
    # Analyze
    print("\n⏳ Analyzing GIF with Gemini 2.5 Flash Lite...")
    start_time = datetime.now()
    
    try:
        description = analyze_gif_for_b1(item.url)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if description:
            print(f"\n✅ Analysis successful! ({elapsed:.1f}s)")
            print(f"📏 Description length: {len(description)} characters")
            print("\n" + "-"*50)
            print("📝 FULL DESCRIPTION:")
            print("-"*50)
            print(description)
            print("-"*50)
            return True
        else:
            print(f"\n❌ Analysis returned empty result ({elapsed:.1f}s)")
            return False
            
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n❌ Analysis failed ({elapsed:.1f}s): {e}")
        import traceback
        traceback.print_exc()
        return False


def test_b2_analysis():
    """Test GIF analysis for Task B2 (GIF + prompt)."""
    print("\n" + "="*70)
    print("🧪 TEST: Task B2 - GIF Analysis (With Prompt Context)")
    print("="*70)
    
    # Load one item from B2
    items = load_task_b2(test_mode=True)
    
    if not items:
        print("❌ No B2 items found!")
        return False
    
    item = items[0]
    print(f"\n📎 Test GIF: {item.id}")
    print(f"🔗 URL: {item.url}")
    print(f"📝 Prompt: {item.prompt}")
    
    # Analyze
    print("\n⏳ Analyzing GIF with Gemini 2.5 Flash Lite...")
    start_time = datetime.now()
    
    try:
        description = analyze_gif_for_b2(item.url, item.prompt)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if description:
            print(f"\n✅ Analysis successful! ({elapsed:.1f}s)")
            print(f"📏 Description length: {len(description)} characters")
            print("\n" + "-"*50)
            print("📝 FULL DESCRIPTION:")
            print("-"*50)
            print(description)
            print("-"*50)
            return True
        else:
            print(f"\n❌ Analysis returned empty result ({elapsed:.1f}s)")
            return False
            
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n❌ Analysis failed ({elapsed:.1f}s): {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyzer_class():
    """Test the GIFAnalyzer class directly."""
    print("\n" + "="*70)
    print("🧪 TEST: GIFAnalyzer Class Initialization")
    print("="*70)
    
    try:
        analyzer = GIFAnalyzer()
        print(f"✅ GIFAnalyzer initialized successfully")
        print(f"📊 Model: {analyzer.model.model_name}")
        print(f"📊 Calls made so far: {analyzer.calls_made}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize GIFAnalyzer: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test the GIF Analyzer module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--task",
        choices=["b1", "b2", "both", "init"],
        default="both",
        help="Which task to test (default: both). 'init' only tests initialization."
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🎬 GIF ANALYZER TEST SUITE")
    print("="*70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing: {args.task}")
    print("⚠️  Remember: Limited to 20 RPD for Gemini 2.5 Flash Lite!")
    
    results = {}
    
    # Always test initialization
    results["init"] = test_analyzer_class()
    
    if not results["init"]:
        print("\n❌ Initialization failed. Cannot proceed with API tests.")
        sys.exit(1)
    
    if args.task == "init":
        print("\n✅ Initialization test complete!")
        sys.exit(0)
    
    # Run task-specific tests
    if args.task in ("b1", "both"):
        results["b1"] = test_b1_analysis()
    
    if args.task in ("b2", "both"):
        results["b2"] = test_b2_analysis()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n  Total: {total_passed}/{total_tests} passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
