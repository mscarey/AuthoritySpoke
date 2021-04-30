"""Functions for dumping AuthoritySpoke objects to external formats."""

from typing import Any, Dict

from authorityspoke.io import schemas_json as schemas


def to_dict(item: Any) -> Dict:
    """Serialize AuthoritySpoke object to dict."""
    schema = schemas.get_schema_for_item(item.__class__.__name__)
    return schema.dump(obj=item)


def to_json(item: Any) -> str:
    """Serialize AuthoritySpoke object to JSON string."""
    schema = schemas.get_schema_for_item(item.__class__.__name__)
    return schema.dumps(obj=item)
