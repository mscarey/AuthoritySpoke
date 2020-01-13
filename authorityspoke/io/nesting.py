"""Nesting fields to prepare to load a dict with a Marshmallow schema."""

from typing import Callable, Dict, List, Sequence, Union


def nest_fields(data: Dict, nest: str, eggs: List[str]):
    """Make sure specified fields are nested under "nest" key."""
    for egg_field in eggs:
        if egg_field in data:
            if not data.get(nest):
                data[nest] = {}
            data[nest][egg_field] = data.pop(egg_field)
    return data


def walk_tree_and_modify(
    obj: Union[Dict, List], func: Callable, ignore: Sequence[str] = ()
) -> Union[Dict, List]:
    """
    Traverse tree of dicts and lists, and modify each node.

    :param obj: the object to traverse

    :param func:
        the function to call on each dict node, returning a dict

    :param ignore: the names of keys that should not be explored

    :returns: a version of the tree with every node modified by `func`
    """
    if isinstance(obj, List):
        return [walk_tree_and_modify(item, func, ignore) for item in obj]
    if isinstance(obj, Dict):

        obj_dict: Dict = func(obj)

        for key, value in obj_dict.items():
            if isinstance(value, (Dict, List)) and key not in ignore:
                obj_dict[key] = walk_tree_and_modify(value, func, ignore)

        return obj_dict

    return obj
