from typing import Any, Dict

from authorityspoke.io import schemas


def to_dict(item: Any) -> Dict:
    schema = schemas.get_schema_for_item(item)
    return schema.dump(obj=item)


def to_json(item: Any) -> str:
    schema = schemas.get_schema_for_item(item)
    return schema.dumps(obj=item)
