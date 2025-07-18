import logging

"""
Refactored orchestrate.py using SOLID principles.
This script now uses the data-driven orchestrator service.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.orchestrator_service import orchestrator
from scripts.tasks.sync_referencias import sync_references
from scripts.tasks.sync_all import sync_all_data
from scripts.tasks.sync_authors_only import sync_proposition_authors
from scripts.tasks.score_propositions import process_backlog


async def sync_references_task():
    """Task to sync reference tables."""
    await sync_references()


async def sync_all_data_task(year: int = 2023):
    """Task to sync all data."""
    await sync_all_data(year)


async def sync_authors_task():
    """Task to sync proposition authors."""
    await sync_proposition_authors()


async def score_propositions_task():
    """Task to score propositions."""
    await process_backlog()


def setup_orchestrator():
    """Set up the orchestrator with all tasks."""
    
    # Register tasks with the orchestrator
    orchestrator.register_task(
        name="sync_references",
        function=sync_references_task,
        dependencies=[],
        parameters={}
    )
    
    orchestrator.register_task(
        name="sync_all_data",
        function=sync_all_data_task,
        dependencies=["sync_references"],
        parameters={"year": 2023}
    )
    
    orchestrator.register_task(
        name="sync_authors",
        function=sync_authors_task,
        dependencies=["sync_all_data"],
        parameters={}
    )
    
    orchestrator.register_task(
        name="score_propositions",
        function=score_propositions_task,
        dependencies=["sync_authors"],
        parameters={}
    )


async def main():
    """Main entry point for orchestrate."""
    print("--- Setting up data-driven ETL orchestrator ---")
    
    # Set up orchestrator
    setup_orchestrator()
    
    # Validate dependencies
    orchestrator.validate_dependencies()
    
    # Build and run the flow
    flow = orchestrator.build_flow("ETL Câmara Insights")
    
    logging.info("--- Starting ETL flow ---")
    await flow()
    logging.info("--- ETL flow completed ---")


if __name__ == "__main__":
    asyncio.run(main())