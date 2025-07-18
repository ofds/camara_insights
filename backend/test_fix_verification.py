#!/usr/bin/env python3
import logging

"""
Quick test to verify the ProposicaoAutor import fix works correctly.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all imports work correctly."""
    try:
        from app.infra.db.models import entidades as models
        from sqlalchemy import insert
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        
        # Test that we can access the relationship table
        logging.info("✅ Successfully imported models")
        logging.info(f"✅ proposicao_autores table exists: {hasattr(models, 'proposicao_autores')}")
        
        # Test that ProposicaoAutor doesn't exist (as expected)
        try:
            getattr(models, 'ProposicaoAutor')
            logging.error("❌ ProposicaoAutor should not exist as a model")
            return False
        except AttributeError:
            logging.info("✅ ProposicaoAutor correctly doesn't exist as a model")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Import error: {e}")
        return False

async def main():
    """Main test runner."""
    logging.info("Testing import fixes...")
    success = await test_imports()
    
    if success:
        logging.info("\n✅ All import tests passed!")
    else:
        logging.error("\n❌ Import tests failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)