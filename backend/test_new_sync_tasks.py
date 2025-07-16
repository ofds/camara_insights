"""
Test script for new sync tasks.
This script tests the daily priority sync and weekly event sync functionality.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.tasks.daily_priority_sync import daily_priority_sync
from scripts.tasks.weekly_event_sync import weekly_event_sync


async def test_daily_sync():
    """Test daily priority sync with minimal parameters."""
    print("=== Testing Daily Priority Sync ===")
    try:
        result = await daily_priority_sync(
            days_back=7,  # Test with just 7 days
            max_propositions=10,  # Test with just 10 propositions
            include_authors=True,
            include_status=True
        )
        print("Daily sync test completed successfully!")
        print(f"Results: {result}")
        return True
    except Exception as e:
        print(f"Daily sync test failed: {e}")
        return False


async def test_weekly_sync():
    """Test weekly event sync with minimal parameters."""
    print("\n=== Testing Weekly Event Sync ===")
    try:
        result = await weekly_event_sync(
            weeks_ahead=1,  # Test with just 1 week ahead
            include_past_days=3,  # Test with just 3 past days
            event_types=["sessao"]  # Test with just one event type
        )
        print("Weekly sync test completed successfully!")
        print(f"Results: {result}")
        return True
    except Exception as e:
        print(f"Weekly sync test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("Starting new sync tasks tests...")
    
    daily_success = await test_daily_sync()
    weekly_success = await test_weekly_sync()
    
    if daily_success and weekly_success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())