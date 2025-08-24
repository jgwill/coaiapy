#!/usr/bin/env python3
"""
Example usage of the CoaiaPy Smart Caching System for Score Configs.

This demonstrates how to use the new project-aware caching system
introduced in Phase 2 of the score-config management enhancement.
"""

# Add the coaiapy directory to Python path if needed
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'coaiapy'))

from cofuse import get_config_with_auto_refresh

def example_usage():
    """Demonstrate smart caching usage scenarios"""
    
    print("=== CoaiaPy Smart Caching System Example ===\n")
    
    # Example 1: Get config by name (most common usage)
    print("1. Fetching config by name 'Helpfulness':")
    config = get_config_with_auto_refresh('Helpfulness')
    if config:
        print(f"   ✓ Found: {config['name']} (ID: {config['id']})")
        print(f"   ✓ Type: {config['dataType']}")
        if 'categories' in config:
            print(f"   ✓ Categories: {len(config['categories'])} options")
    else:
        print("   ❌ Config not found")
    
    print()
    
    # Example 2: Get config by ID  
    print("2. Fetching config by ID (if known):")
    # This would use a real config ID in practice
    config_id = "cm6m5rrk6001vvkbq7zovttji"  # Example ID
    config = get_config_with_auto_refresh(config_id)
    if config:
        print(f"   ✓ Found: {config['name']}")
    else:
        print("   ❌ Config with that ID not found")
    
    print()
    
    # Example 3: Demonstrate cache behavior
    print("3. Cache behavior demonstration:")
    print("   - First call: May hit API and cache result")
    config1 = get_config_with_auto_refresh('Quality')
    
    print("   - Second call: Should hit cache (faster)")
    config2 = get_config_with_auto_refresh('Quality')
    
    if config1 and config2:
        print(f"   ✓ Both calls returned same config: {config1['name']}")
    
    print()
    
    # Example 4: Show cache location
    from pathlib import Path
    cache_dir = Path.home() / '.coaia' / 'score-configs'
    print(f"4. Cache location: {cache_dir}")
    if cache_dir.exists():
        cache_files = list(cache_dir.glob('*.json'))
        print(f"   ✓ Found {len(cache_files)} project cache files")
        for cache_file in cache_files:
            print(f"   - {cache_file.name}")
    else:
        print("   ℹ️  Cache directory not yet created")
    
    print("\n=== Example Complete ===")
    print("💡 Tips:")
    print("   - Cache automatically refreshes after 24 hours")
    print("   - Each Langfuse project gets its own cache file")
    print("   - No manual cache management needed - it's all automatic!")

if __name__ == '__main__':
    try:
        example_usage()
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("Note: This example requires valid Langfuse credentials in config")