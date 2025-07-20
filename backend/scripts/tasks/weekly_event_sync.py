"""
Weekly event sync task.
This task syncs events for the current and upcoming week,
ensuring the calendar is always up-to-date.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.data_sync_service import DataSyncService
from app.infra.db.session import SessionLocal


async def weekly_event_sync(
    weeks_ahead: int = 2,
    include_past_days: int = 7
) -> Dict[str, Any]:
    """
    Sync events for current and upcoming weeks.

    Args:
        weeks_ahead: Number of weeks ahead to sync (default: 2)
        include_past_days: Number of past days to include (default: 7)

    Returns:
        Dictionary with sync results
    """
    print("--- Starting Weekly Event Sync ---")

    # Create database session
    db = SessionLocal()

    try:
        # Initialize sync service
        sync_service = DataSyncService(db)

        # Calculate date range
        start_date = datetime.now() - timedelta(days=include_past_days)
        end_date = datetime.now() + timedelta(weeks=weeks_ahead)

        results = {
            "events": 0,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "errors": []
        }

        print(f"Syncing all events from {results['date_range']['start']} to {results['date_range']['end']}")
        
        # Define parameters for all events in the date range
        event_params = {
            "dataInicio": start_date.strftime("%Y-%m-%d"),
            "dataFim": end_date.strftime("%Y-%m-%d"),
            "ordenarPor": "dataHoraInicio",
            "itens": 100 # Request a larger number of items per page
        }

        # Perform a single sync operation for all event types
        events_synced = await sync_service.sync_events(
            params=event_params,
            batch_size=100 # Match batch size to items per page
        )

        results["events"] = events_synced

        print(f"--- Weekly Event Sync Completed ---")
        print(f"Total events synced: {results['events']}")
        print(f"Date range: {results['date_range']['start']} to {results['date_range']['end']}")

    except Exception as e:
        error_msg = f"Error during weekly event sync: {str(e)}"
        print(error_msg)
        results["errors"].append(error_msg)
    finally:
        # Ensure the database session is always closed
        print("Closing database session.")
        db.close()

    return results


def main():
    """Main entry point for weekly event sync."""
    import argparse

    parser = argparse.ArgumentParser(description="Weekly event sync for calendar updates")
    parser.add_argument("--weeks-ahead", type=int, default=2, help="Weeks ahead to sync")
    parser.add_argument("--include-past-days", type=int, default=7, help="Past days to include")
    
    args = parser.parse_args()

    asyncio.run(weekly_event_sync(
        weeks_ahead=args.weeks_ahead,
        include_past_days=args.include_past_days
    ))


if __name__ == "__main__":
    main()