"""
Daily sync task for prioritized information.
This task syncs only the most critical and frequently updated information:
- Propositions and their child entities (authors, related propositions, status updates)
- Focuses on recent and active propositions
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


async def daily_priority_sync(
    days_back: int = 30,
    max_propositions: int = 100,
    include_authors: bool = True,
    include_status: bool = True
) -> Dict[str, Any]:
    """
    Sync prioritized information for daily updates.
    
    Args:
        days_back: Number of days back to sync propositions (default: 30)
        max_propositions: Maximum number of propositions to sync (default: 100)
        include_authors: Whether to sync proposition authors (default: True)
        include_status: Whether to sync status updates (default: True)
    
    Returns:
        Dictionary with sync results
    """
    print("--- Starting Daily Priority Sync ---")
    
    # Create database session
    db = SessionLocal()
    
    # Initialize sync service
    sync_service = DataSyncService(db)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    results = {
        "propositions": 0,
        "authors": 0,
        "status_updates": 0,
        "related_propositions": 0,
        "errors": []
    }
    
    try:
        # Sync recent propositions with filters
        proposition_params = {
            "dataInicio": start_date.strftime("%Y-%m-%d"),
            "dataFim": end_date.strftime("%Y-%m-%d"),
            "ordenarPor": "id",
            "itens": min(max_propositions, 100)  # API limit
        }
        
        # Sync propositions
        propositions_synced = await sync_service.sync_propositions(
            params=proposition_params,
            batch_size=20
        )
        results["propositions"] = propositions_synced
        
        # Sync authors if requested
        if include_authors and propositions_synced > 0:
            authors_synced = await sync_service.sync_proposition_authors()
            results["authors"] = authors_synced
        
        # Sync status updates (tramitações) if requested
        if include_status and propositions_synced > 0:
            status_synced = await sync_service.sync_tramitacoes()
            results["status_updates"] = status_synced
        
        # Sync related propositions
        if propositions_synced > 0:
            related_synced = await sync_service.sync_related_propositions()
            results["related_propositions"] = related_synced
        
        print(f"--- Daily Priority Sync Completed ---")
        print(f"Propositions synced: {results['propositions']}")
        print(f"Authors synced: {results['authors']}")
        print(f"Status updates synced: {results['status_updates']}")
        print(f"Related propositions synced: {results['related_propositions']}")
        
    except Exception as e:
        error_msg = f"Error during daily sync: {str(e)}"
        print(error_msg)
        results["errors"].append(error_msg)
    
    return results


def main():
    """Main entry point for daily priority sync."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily priority sync for critical information")
    parser.add_argument("--days-back", type=int, default=30, help="Days back to sync")
    parser.add_argument("--max-propositions", type=int, default=100, help="Max propositions to sync")
    parser.add_argument("--no-authors", action="store_true", help="Skip author sync")
    parser.add_argument("--no-status", action="store_true", help="Skip status updates")
    
    args = parser.parse_args()
    
    asyncio.run(daily_priority_sync(
        days_back=args.days_back,
        max_propositions=args.max_propositions,
        include_authors=not args.no_authors,
        include_status=not args.no_status
    ))


if __name__ == "__main__":
    main()