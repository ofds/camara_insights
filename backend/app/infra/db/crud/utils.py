from typing import Optional, Dict, Any
from sqlalchemy.orm import Query
from sqlalchemy import asc, desc

def apply_filters(query: Query, model, filters: Optional[Dict[str, Any]] = None) -> Query:
    """
    Applies advanced filtering to a SQLAlchemy query.

    Filters can be provided in the format: {'field__operator': value}
    
    Supported operators:
    - 'eq': equal (default if no operator is specified)
    - 'neq': not equal
    - 'gt': greater than
    - 'lt': less than
    - 'gte': greater than or equal
    - 'lte': less than or equal
    - 'in': in a list of values
    - 'like': case-sensitive like
    - 'ilike': case-insensitive like
    """
    if not filters:
        return query

    for key, value in filters.items():
        parts = key.split('__')
        field_name = parts[0]
        operator = parts[1] if len(parts) > 1 else 'eq'

        if hasattr(model, field_name):
            column = getattr(model, field_name)
            if operator == 'eq':
                query = query.filter(column == value)
            elif operator == 'neq':
                query = query.filter(column != value)
            elif operator == 'gt':
                query = query.filter(column > value)
            elif operator == 'lt':
                query = query.filter(column < value)
            elif operator == 'gte':
                query = query.filter(column >= value)
            elif operator == 'lte':
                query = query.filter(column <= value)
            elif operator == 'in':
                query = query.filter(column.in_(value))
            elif operator == 'like':
                query = query.filter(column.like(f"%{value}%"))
            elif operator == 'ilike':
                query = query.filter(column.ilike(f"%{value}%"))
    return query

def apply_sorting(
    query: Query,
    sort: Optional[str] = None,
    allowed_sort_fields: Dict[str, Any] = None,
    default_sort_field: str = None
) -> Query:
    """Applies sorting to a SQLAlchemy query."""
    if sort:
        sort_params = sort.split(',')
        for sort_param in sort_params:
            try:
                field, direction = sort_param.split(':')
                field = field.strip()
                direction = direction.strip().lower()

                if allowed_sort_fields and field in allowed_sort_fields and direction in ['asc', 'desc']:
                    column = allowed_sort_fields[field]
                    if direction == 'asc':
                        query = query.order_by(asc(column))
                    else:
                        query = query.order_by(desc(column))
            except ValueError:
                # Silently ignore malformed sort parameters
                pass
    elif default_sort_field and allowed_sort_fields and default_sort_field in allowed_sort_fields:
        default_column = allowed_sort_fields[default_sort_field]
        query = query.order_by(desc(default_column))

    return query

def apply_filters_and_sorting(
    query: Query,
    model,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None,
    allowed_sort_fields: Dict[str, Any] = None,
    default_sort_field: str = None
) -> Query:
    """
    Applies advanced filtering and sorting to a SQLAlchemy query by
    combining the apply_filters and apply_sorting functions.
    """
    query = apply_filters(query, model, filters)
    query = apply_sorting(query, sort, allowed_sort_fields, default_sort_field)
    return query