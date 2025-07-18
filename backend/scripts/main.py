import logging

"""
Main CLI interface for the refactored Câmara Insights project.
This provides a unified command-line interface for all tasks.
"""

import asyncio
import argparse
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.tasks.sync_all import sync_all_data
from scripts.tasks.sync_authors_only import sync_proposition_authors
from scripts.tasks.sync_referencias import sync_references
from scripts.tasks.check_ai_data import check_ai_data
from scripts.tasks.score_propositions import process_backlog, process_specific_propositions
from scripts.tasks.orchestrate import main as orchestrate_main
from scripts.tasks.daily_priority_sync import daily_priority_sync
from scripts.tasks.weekly_event_sync import weekly_event_sync


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Câmara Insights CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync all data
    sync_all_parser = subparsers.add_parser('sync-all', help='Sync all data from Câmara API')
    sync_all_parser.add_argument('--year', type=int, default=2023, help='Year to sync from')
    
    # Sync authors only
    sync_authors_parser = subparsers.add_parser('sync-authors', help='Sync only proposition authors')
    
    # Sync references
    sync_refs_parser = subparsers.add_parser('sync-refs', help='Sync reference tables')
    
    # Check AI data
    check_ai_parser = subparsers.add_parser('check-ai', help='Check AI analysis results')
    check_ai_parser.add_argument('--limit', type=int, default=10, help='Number of results to display')
    check_ai_parser.add_argument('--format', choices=['console', 'json', 'csv'], default='console', help='Output format')
    
    # Score propositions
    score_parser = subparsers.add_parser('score', help='Process AI scoring for propositions')
    score_parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    score_parser.add_argument('--rate-limit', type=int, default=18, help='Requests per minute limit')
    score_parser.add_argument('--ids', nargs='*', type=int, help='Specific proposition IDs to process')
    
    # Daily priority sync
    daily_sync_parser = subparsers.add_parser('daily-sync', help='Daily sync of prioritized information')
    daily_sync_parser.add_argument('--days-back', type=int, default=30, help='Days back to sync')
    daily_sync_parser.add_argument('--max-propositions', type=int, default=100, help='Max propositions to sync')
    daily_sync_parser.add_argument('--no-authors', action='store_true', help='Skip author sync')
    daily_sync_parser.add_argument('--no-status', action='store_true', help='Skip status updates')
    
    # Weekly event sync
    weekly_sync_parser = subparsers.add_parser('weekly-sync', help='Weekly sync of events for calendar')
    weekly_sync_parser.add_argument('--weeks-ahead', type=int, default=2, help='Weeks ahead to sync')
    weekly_sync_parser.add_argument('--include-past-days', type=int, default=7, help='Past days to include')
    weekly_sync_parser.add_argument('--event-types', nargs='+', help='Specific event types to sync')
    
    # Orchestrate
    orchestrate_parser = subparsers.add_parser('orchestrate', help='Run complete ETL orchestration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run the appropriate command
    if args.command == 'sync-all':
        asyncio.run(sync_all_data(args.year))
    elif args.command == 'sync-authors':
        asyncio.run(sync_proposition_authors())
    elif args.command == 'sync-refs':
        asyncio.run(sync_references())
    elif args.command == 'check-ai':
        result = check_ai_data(args.limit, args.format)
        logging.info(result)
    elif args.command == 'score':
        if args.ids:
            asyncio.run(process_specific_propositions(args.ids))
        else:
            asyncio.run(process_backlog(args.batch_size, args.rate_limit))
    elif args.command == 'daily-sync':
        asyncio.run(daily_priority_sync(
            days_back=args.days_back,
            max_propositions=args.max_propositions,
            include_authors=not args.no_authors,
            include_status=not args.no_status
        ))
    elif args.command == 'weekly-sync':
        asyncio.run(weekly_event_sync(
            weeks_ahead=args.weeks_ahead,
            include_past_days=args.include_past_days,
            event_types=args.event_types
        ))
    elif args.command == 'orchestrate':
        asyncio.run(orchestrate_main())


if __name__ == "__main__":
    main()