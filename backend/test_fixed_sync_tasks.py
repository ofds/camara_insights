#!/usr/bin/env python3
import logging

"""
Test script to verify the fixed sync tasks work correctly.
This script tests the daily and weekly sync tasks after fixing the session issue.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.tasks.daily_priority_sync import daily_priority_sync
from scripts.tasks.weekly_event_sync import weekly_event_sync


async def test_daily_sync():
    """Test the daily priority sync with minimal parameters."""
    logging.info("Testing daily priority sync...")
    try:
        results = await daily_priority_sync(
            days_back=1,
            max_propositions=5,
            include_authors=True,
            include_status=True
        )
        logging.info("✅ Daily sync test passed!")
        logging.info(f"Results: {results}")
        return True
    except Exception as e:
        logging.error(f"❌ Daily sync test failed: {e}")
        return False


async def test_weekly_sync():
    """Test the weekly event sync with minimal parameters."""
    logging.info("\nTesting weekly event sync...")
    try:
        results = await weekly_event_sync(
            weeks_ahead=1,
            include_past_days=1,
            event_types=["sessao"]
        )
        logging.info("✅ Weekly sync test passed!")
        logging.info(f"Results: {results}")
        return True
    except Exception as e:
        logging.error(f"❌ Weekly sync test failed: {e}")
        return False

async def main():
    """Run all sync task tests."""
    logging.info("=== Testing Fixed Sync Tasks ===\n")
    
    
    daily_success = await test_daily_sync()
    weekly_success = await test_weekly_sync()
    
    print("\n=== Test Summary ===")
    if daily_success and weekly_success:
        logging.info("✅ All tests passed! The sync tasks are working correctly.")
        return 0
    else:
        logging.error("❌ Some tests failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)