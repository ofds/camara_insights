"""
Refactored score_propositions.py using SOLID principles.
This script now uses the BacklogProcessor class for handling AI scoring.
"""

import asyncio
import sys
import os
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.infra.db.session import SessionLocal
from src.services.backlog_processor import BacklogProcessor


async def process_backlog(batch_size: int = 10, requests_per_minute: int = 18) -> int:
    """
    Process the backlog of unscored propositions.
    
    Args:
        batch_size: Number of propositions to process in each batch
        requests_per_minute: Rate limit for API calls
        
    Returns:
        Total number of propositions processed
    """
    # Create session factory
    def session_factory():
        return SessionLocal()
    
    # Create and run processor
    processor = BacklogProcessor(
        session_factory=session_factory,
        batch_size=batch_size,
        requests_per_minute=requests_per_minute
    )
    
    return await processor.process_backlog()


async def process_specific_propositions(proposition_ids: List[int]) -> int:
    """
    Process specific propositions by ID.
    
    Args:
        proposition_ids: List of proposition IDs to process
        
    Returns:
        Number of propositions successfully processed
    """
    def session_factory():
        return SessionLocal()
    
    processor = BacklogProcessor(session_factory=session_factory)
    return await processor.process_specific_propositions(proposition_ids)


def main():
    """Main entry point for score_propositions."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process AI scoring for propositions")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--rate-limit", type=int, default=18, help="Requests per minute limit")
    parser.add_argument("--ids", nargs="*", type=int, help="Specific proposition IDs to process")
    
    args = parser.parse_args()
    
    if args.ids:
        # Process specific propositions
        print(f"Processing specific propositions: {args.ids}")
        asyncio.run(process_specific_propositions(args.ids))
    else:
        # Process backlog
        print("Processing entire backlog...")
        asyncio.run(process_backlog(args.batch_size, args.rate_limit))


if __name__ == "__main__":
    main()