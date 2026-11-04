"""Nesting fields to prepare to load a dict with a Marshmallow schema."""

from collections.abc import Callable, Sequence


def nest_fields(data: dict, nest: str, eggs: list[str]):
    """Make sure specified fields are nested under "nest" key."""
    for egg_field in eggs:
        if egg_field in data:
            if not data.get(nest):
                data[nest] = {}
            data[nest][egg_field] = data.pop(egg_field)
    return data


def walk_tree_and_modify(
    obj: dict | list, func: Callable, ignore: Sequence[str] = ()
) -> dict | list:
    """
    Traverse tree of dicts and lists, and modify each node.

    :param obj: the object to traverse

    :param func:
        the function to call on each dict node, returning a dict

    :param ignore: the names of keys that should not be explored

    :returns: a version of the tree with every node modified by `func`
    """
    if isinstance(obj, list):
        return [walk_tree_and_modify(item, func, ignore) for item in obj]
    if isinstance(obj, dict):
        obj_dict: dict = func(obj)

        for key, value in obj_dict.items():
            if isinstance(value, (dict, list)) and key not in ignore:
                obj_dict[key] = walk_tree_and_modify(value, func, ignore)

        return obj_dict

    return obj
