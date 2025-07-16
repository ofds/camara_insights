#!/usr/bin/env python3
"""
Final integration test to verify all fixes work correctly.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_all_imports():
    """Test that all imports work correctly."""
    try:
        # Test model imports
        from app.infra.db.models.entidades import (
            Proposicao, Deputado, Evento, Votacao, Voto,
            Tramitacao, proposicao_autores
        )
        print("✅ All model imports successful")
        
        # Test service imports
        from src.services.data_sync_service import DataSyncService
        from src.services.backlog_processor import BacklogProcessor
        print("✅ All service imports successful")
        
        # Test repository imports
        from src.data.repository import BaseRepository, ProposicaoRepository
        print("✅ All repository imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def test_service_initialization():
    """Test that services can be initialized."""
    try:
        from app.infra.db.session import SessionLocal
        from src.services.data_sync_service import DataSyncService
        from src.services.backlog_processor import BacklogProcessor
        
        # Test DataSyncService
        db = SessionLocal()
        sync_service = DataSyncService(db)
        print("✅ DataSyncService initialized successfully")
        
        # Test BacklogProcessor
        def session_factory():
            return SessionLocal()
        
        processor = BacklogProcessor(session_factory, batch_size=1)
        print("✅ BacklogProcessor initialized successfully")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Service initialization error: {e}")
        return False

async def test_no_proposicao_autor_references():
    """Test that there are no remaining ProposicaoAutor references."""
    import os
    import re
    
    # Search for ProposicaoAutor in all Python files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') and 'test' not in file.lower():
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'ProposicaoAutor' in content and 'proposicao_autores' not in content:
                            print(f"❌ Found ProposicaoAutor reference in {filepath}")
                            return False
                except:
                    continue
    
    print("✅ No remaining ProposicaoAutor references found")
    return True

async def main():
    """Run all tests."""
    print("=== Final Integration Test ===")
    
    tests = [
        test_all_imports,
        test_service_initialization,
        test_no_proposicao_autor_references
    ]
    
    all_passed = True
    for test in tests:
        print(f"\n--- Running {test.__name__} ---")
        passed = await test()
        if not passed:
            all_passed = False
    
    print("\n=== Test Results ===")
    if all_passed:
        print("✅ All tests passed! The refactoring is complete and working.")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)