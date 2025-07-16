# SOLID Refactoring Guide

This document explains how the Câmara Insights project has been refactored to follow SOLID principles.

## Overview

The refactoring transforms the original monolithic scripts into a well-structured, maintainable codebase following SOLID design principles.

## SOLID Principles Applied

### 1. Single Responsibility Principle (SRP)
- **Before**: Scripts mixed data access, business logic, and presentation
- **After**: Each class has a single, well-defined responsibility

### 2. Open/Closed Principle (OCP)
- **Before**: Adding new tasks required modifying existing orchestrator
- **After**: New tasks can be added without modifying existing code

### 3. Liskov Substitution Principle (LSP)
- **Before**: Tight coupling to concrete implementations
- **After**: Interfaces and abstractions allow for substitution

### 4. Interface Segregation Principle (ISP)
- **Before**: Large interfaces with unused methods
- **After**: Focused interfaces for specific use cases

### 5. Dependency Inversion Principle (DIP)
- **Before**: High-level modules depended on low-level modules
- **After**: Both depend on abstractions

## New Project Structure

```
backend/
├── src/
│   ├── data/
│   │   ├── repository.py          # Repository pattern implementation
│   │   └── __init__.py
│   ├── services/
│   │   ├── data_sync_service.py   # Consolidated sync logic
│   │   ├── backlog_processor.py   # AI scoring processor
│   │   ├── orchestrator_service.py # Data-driven orchestrator
│   │   ├── presentation_service.py # Presentation logic
│   │   └── __init__.py
│   └── __init__.py
├── scripts/
│   ├── tasks/
│   │   ├── sync_all.py           # Refactored sync_all
│   │   ├── sync_authors_only.py  # Refactored sync_authors_only
│   │   ├── sync_referencias.py   # Refactored sync_referencias
│   │   ├── check_ai_data.py      # Refactored check_ai_data
│   │   ├── score_propositions.py # Refactored score_propositions
│   │   ├── orchestrate.py        # Refactored orchestrate
│   │   └── __init__.py
│   └── main.py                   # Unified CLI interface
└── app/                          # Existing application code
```

## Usage Examples

### Using the CLI
```bash
# Sync all data
python scripts/main.py sync-all --year 2023

# Sync only authors
python scripts/main.py sync-authors

# Check AI results
python scripts/main.py check-ai --limit 20 --format json

# Score propositions
python scripts/main.py score --batch-size 5 --rate-limit 10

# Run complete orchestration
python scripts/main.py orchestrate
```

### Using Services Directly
```python
from src.services.data_sync_service import DataSyncService
from app.infra.db.session import SessionLocal

async def custom_sync():
    session = SessionLocal()
    service = DataSyncService(session)
    await service.sync_entity_with_details(Deputado, "/deputados")
```

## Key Improvements

1. **Testability**: Services can be easily mocked and tested
2. **Reusability**: Core logic is now reusable across different contexts
3. **Maintainability**: Clear separation of concerns makes changes easier
4. **Extensibility**: New features can be added without modifying existing code
5. **Configuration**: All parameters are configurable via dependency injection

## Migration Guide

1. **Phase 1**: Start using the new CLI interface
2. **Phase 2**: Gradually migrate old scripts to use new services
3. **Phase 3**: Deprecate old scripts once new ones are validated
4. **Phase 4**: Add comprehensive tests for new services

## Testing

The refactored code is designed to be easily testable:
- Services accept dependencies via constructor injection
- Repository pattern allows for in-memory testing
- Async/await patterns work well with testing frameworks