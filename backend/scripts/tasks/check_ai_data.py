"""
Refactored check_ai_data.py using SOLID principles.
This script now separates data access from presentation logic.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.infra.db.session import SessionLocal
from src.data.repository import AIDataRepository
from src.services.presentation_service import PresentationService


def check_ai_data(limit: int = 10, format_type: str = "console") -> str:
    """
    Check and display AI analysis results.
    
    Args:
        limit: Maximum number of results to display
        format_type: Output format ("console", "json", "csv")
        
    Returns:
        Formatted string with AI analysis results
    """
    session = SessionLocal()
    try:
        # Data access layer
        repository = AIDataRepository(session, None)
        results = repository.get_latest_results(limit)
        
        # Presentation layer
        output = PresentationService.display_ai_results(results, format_type)
        
        return output
        
    finally:
        session.close()


def main():
    """Main entry point for check_ai_data."""
    print("--- Checking AI Analysis Results ---")
    
    # Default parameters
    limit = 10
    format_type = "console"
    
    # Parse command line arguments if provided
    import argparse
    parser = argparse.ArgumentParser(description="Check AI analysis results")
    parser.add_argument("--limit", type=int, default=10, help="Number of results to display")
    parser.add_argument("--format", choices=["console", "json", "csv"], default="console", help="Output format")
    
    args = parser.parse_args()
    limit = args.limit
    format_type = args.format
    
    # Get and display results
    output = check_ai_data(limit, format_type)
    print(output)


if __name__ == "__main__":
    main()