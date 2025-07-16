"""
Backlog processor for handling AI scoring of propositions.
This class encapsulates the backlog processing logic following SOLID principles.
"""

import asyncio
from typing import List, Optional, Callable
from sqlalchemy.orm import Session

from src.data.repository import ProposicaoRepository
from app.services.scoring_service import analyze_and_score_propositions
from app.core.rate_limiter import RateLimiter
from typing import Dict, List, Tuple, Any


class BacklogProcessor:
    """Processor for handling AI scoring backlog with rate limiting."""
    
    def __init__(self, 
                 session_factory: Callable[[], Session],
                 rate_limiter: Optional[RateLimiter] = None,
                 batch_size: int = 10,
                 requests_per_minute: int = 18):
        """
        Initialize the backlog processor.
        
        Args:
            session_factory: Factory function to create database sessions
            rate_limiter: Optional custom rate limiter
            batch_size: Number of propositions to process in each batch
            requests_per_minute: Rate limit for API calls
        """
        self.session_factory = session_factory
        self.batch_size = batch_size
        self.rate_limiter = rate_limiter or RateLimiter(requests_per_minute=requests_per_minute)
    
    async def process_batch(self, propositions: List[Any]) -> int:
        """Process a single batch of propositions."""
        if not propositions:
            return 0
        
        # Create a worker function for each proposition
        async def task_worker(prop):
            await self.rate_limiter.acquire()
            print(f"Analyzing proposition ID: {prop.id}...")
            
            # Create a new session for each worker to avoid session conflicts
            session = self.session_factory()
            try:
                await analyze_and_score_propositions(session, [prop])
            finally:
                session.close()
        
        # Process all propositions in the batch concurrently
        tasks = [task_worker(prop) for prop in propositions]
        await asyncio.gather(*tasks)
        
        return len(propositions)
    
    async def process_backlog(self) -> int:
        """
        Process the entire backlog of unscored propositions.
        
        Returns:
            Total number of propositions processed
        """
        total_processed = 0
        batch_number = 1
        
        print("--- Starting backlog processing ---")
        print("This will run continuously until all propositions are analyzed.")
        print("Press CTRL+C to stop at any time.")
        
        try:
            while True:
                # Create a new session for each batch
                session = self.session_factory()
                try:
                    print(f"\n--- Batch #{batch_number}: Fetching up to {self.batch_size} propositions... ---")
                    
                    # Get unscored propositions
                    from app.infra.db.models.entidades import Proposicao
                    repository = ProposicaoRepository(session, Proposicao)
                    propositions_to_score = repository.get_unscored(self.batch_size)
                    
                    if not propositions_to_score:
                        print("\nCongratulations! All propositions in the backlog have been analyzed.")
                        break
                    
                    print(f"Found {len(propositions_to_score)} propositions. Starting concurrent processing...")
                    
                    # Process this batch
                    processed = await self.process_batch(propositions_to_score)
                    total_processed += processed
                    
                    print(f"--- Batch #{batch_number} completed. {processed} propositions processed. ---")
                    batch_number += 1
                    
                except Exception as e:
                    print(f"Unexpected error occurred: {e}. Waiting 1 minute before continuing.")
                    await asyncio.sleep(60)
                finally:
                    session.close()
        
        except KeyboardInterrupt:
            print("\nProcessing interrupted by user.")
        
        print(f"--- Processing completed. Total propositions processed: {total_processed} ---")
        return total_processed
    
    async def process_specific_propositions(self, proposition_ids: List[int]) -> int:
        """
        Process specific propositions by ID.
        
        Args:
            proposition_ids: List of proposition IDs to process
            
        Returns:
            Number of propositions successfully processed
        """
        session = self.session_factory()
        try:
            repository = ProposicaoRepository(session, None)
            propositions = [repository.get_by_id(pid) for pid in proposition_ids]
            propositions = [p for p in propositions if p is not None]
            
            if not propositions:
                print("No valid propositions found for the given IDs.")
                return 0
            
            print(f"Processing {len(propositions)} specific propositions...")
            processed = await self.process_batch(propositions)
            print(f"Successfully processed {processed} propositions.")
            return processed
            
        finally:
            session.close()