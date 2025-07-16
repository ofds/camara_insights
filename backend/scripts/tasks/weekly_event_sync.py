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
    include_past_days: int = 7,
    event_types: list = None
) -> Dict[str, Any]:
    """
    Sync events for current and upcoming weeks.
    
    Args:
        weeks_ahead: Number of weeks ahead to sync (default: 2)
        include_past_days: Number of past days to include (default: 7)
        event_types: List of event types to sync (default: all types)
    
    Returns:
        Dictionary with sync results
    """
    print("--- Starting Weekly Event Sync ---")
    
    # Create database session
    db = SessionLocal()
    
    # Initialize sync service
    sync_service = DataSyncService(db)
    
    # Calculate date range
    start_date = datetime.now() - timedelta(days=include_past_days)
    end_date = datetime.now() + timedelta(weeks=weeks_ahead)
    
    results = {
        "events": 0,
        "event_types": {},
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        "errors": []
    }
    
    try:
        # Event types to sync
        if event_types is None:
            event_types = [
                "sessao",
                "audiencia_publica",
                "reuniao",
                "sessao_solene",
                "sessao_especial",
                "outros"
            ]
        
        # Sync events for each type
        for event_type in event_types:
            print(f"Syncing events of type: {event_type}")
            
            event_params = {
                "dataInicio": start_date.strftime("%Y-%m-%d"),
                "dataFim": end_date.strftime("%Y-%m-%d"),
                "tipo": event_type,
                "ordenarPor": "dataHoraInicio"
            }
            
            events_synced = await sync_service.sync_events(
                params=event_params,
                batch_size=50
            )
            
            results["events"] += events_synced
            results["event_types"][event_type] = events_synced
            
            print(f"  {events_synced} events synced for type '{event_type}'")
        
        print(f"--- Weekly Event Sync Completed ---")
        print(f"Total events synced: {results['events']}")
        print(f"Date range: {results['date_range']['start']} to {results['date_range']['end']}")
        
    except Exception as e:
        error_msg = f"Error during weekly event sync: {str(e)}"
        print(error_msg)
        results["errors"].append(error_msg)
    
    return results


def main():
    """Main entry point for weekly event sync."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Weekly event sync for calendar updates")
    parser.add_argument("--weeks-ahead", type=int, default=2, help="Weeks ahead to sync")
    parser.add_argument("--include-past-days", type=int, default=7, help="Past days to include")
    parser.add_argument("--event-types", nargs="+", help="Specific event types to sync")
    
    args = parser.parse_args()
    
    asyncio.run(weekly_event_sync(
        weeks_ahead=args.weeks_ahead,
        include_past_days=args.include_past_days,
        event_types=args.event_types
    ))


if __name__ == "__main__":
    main()