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
        print(result)
    elif args.command == 'score':
        if args.ids:
            asyncio.run(process_specific_propositions(args.ids))
        else:
            asyncio.run(process_backlog(args.batch_size, args.rate_limit))
    elif args.command == 'orchestrate':
        asyncio.run(orchestrate_main())


if __name__ == "__main__":
    main()