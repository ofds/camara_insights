from typing import Optional, Dict, Any
from sqlalchemy.orm import Query
from sqlalchemy import asc, desc

def apply_filters_and_sorting(
    query: Query,
    model,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None,
    allowed_sort_fields: Dict[str, Any] = None,
    default_sort_field: str = None
) -> Query:
    # Apply filtering
    if filters:
        for field, value in filters.items():
            if hasattr(model, field):
                query = query.filter(getattr(model, field) == value)
    
    # Apply sorting
    if sort:
        sort_params = sort.split(',')
        for sort_param in sort_params:
            field, direction = sort_param.split(':')
            field = field.strip()
            direction = direction.strip().lower()
            
            # Validate field and direction
            if field in allowed_sort_fields and direction in ['asc', 'desc']:
                column = allowed_sort_fields[field]
                query = query.order_by(asc(column)) if direction == 'asc' else query.order_by(desc(column))

    elif default_sort_field and default_sort_field in allowed_sort_fields:
        query = query.order_by(asc(allowed_sort_fields[default_sort_field]))

    return query