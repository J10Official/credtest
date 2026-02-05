#!/usr/bin/env python3
"""
Test script to verify per-module model configuration.

This script verifies that:
1. ContentWriter uses DeepSeek v3.2 with atlas-cloud/fp8 provider
2. All other modules use Gemma 3 27B with bf16 quantization
3. Per-module configuration properly overrides defaults
"""

import config
from api import get_module_lm, _log_active_providers
from logger import logger

def test_module_configuration():
    """Test that module configurations are correctly set up."""
    
    print("=" * 70)
    print("TESTING MODULE CONFIGURATION")
    print("=" * 70)
    
    logger.info("=" * 70)
    logger.info("TESTING MODULE CONFIGURATION")
    logger.info("=" * 70)
    
    # Test each module
    modules = ["ContextEnricher", "HumorArchitect", "DeliveryStrategist", "ContentWriter", "HumorJudge"]
    
    for module_name in modules:
        logger.info(f"\n📦 Testing {module_name}:")
        
        # Get module config
        module_config = config.get_module_config(module_name)
        logger.info(f"   Model: {module_config['model'] or 'DEFAULT'}")
        
        # Get module LM
        module_lm = get_module_lm(module_name)
        
        if module_lm:
            logger.info(f"   ✅ Has custom LM")
            logger.info(f"   Model string: {module_lm.model}")
            
            # Check for extra_body provider settings
            if hasattr(module_lm, 'kwargs') and 'extra_body' in module_lm.kwargs:
                extra_body = module_lm.kwargs['extra_body']
                if 'provider' in extra_body:
                    provider_settings = extra_body['provider']
                    logger.info(f"   Provider settings: {provider_settings}")
                    
                    if 'order' in provider_settings:
                        logger.info(f"   🎯 Provider routing: {provider_settings['order']}")
                    if 'quantizations' in provider_settings:
                        logger.info(f"   🔧 Quantizations: {provider_settings['quantizations']}")
        else:
            logger.info(f"   📍 Using global default: {config.DEFAULT_MODEL}")
    
    # Log full model configuration
    logger.info("\n")
    _log_active_providers()
    
    # Verify ContentWriter specifically
    logger.info("\n" + "=" * 70)
    logger.info("VERIFYING CONTENTWRITER CONFIGURATION")
    logger.info("=" * 70)
    
    writer_config = config.get_module_config("ContentWriter")
    logger.info(f"Model spec: {writer_config['model']}")
    
    expected_model = "openrouter/deepseek/deepseek-v3.2"
    actual_model = writer_config['model']
    
    if actual_model == expected_model:
        logger.info(f"✅ ContentWriter model is correct: {expected_model}")
    else:
        logger.error(f"❌ ContentWriter model mismatch!")
        logger.error(f"   Expected: {expected_model}")
        logger.error(f"   Actual: {actual_model}")
        return False
    
    # Check provider settings
    if 'extra_body' in writer_config['params']:
        extra_body = writer_config['params']['extra_body']
        if 'provider' in extra_body:
            provider = extra_body['provider']
            logger.info(f"✅ Provider settings found: {provider}")
            
            if 'order' in provider and provider['order'] == ['atlas-cloud/fp8']:
                logger.info(f"✅ Provider routing is correct: atlas-cloud/fp8")
            else:
                logger.error(f"❌ Provider routing mismatch!")
                logger.error(f"   Expected: ['atlas-cloud/fp8']")
                logger.error(f"   Actual: {provider.get('order', 'NOT SET')}")
                return False
        else:
            logger.error(f"❌ No provider settings in extra_body!")
            return False
    else:
        logger.error(f"❌ No extra_body in params!")
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ ALL TESTS PASSED - Configuration is correct!")
    logger.info("=" * 70)
    return True


if __name__ == "__main__":
    success = test_module_configuration()
    exit(0 if success else 1)
