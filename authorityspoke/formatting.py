import textwrap


TAB_WIDTH = 2
TEXT_WIDTH = 80


def indented(text: str, tabs: int = 1) -> str:
    indent = TAB_WIDTH * tabs * " "
    return textwrap.indent(text, prefix=indent)


def wrapped(text: str) -> str:
    return textwrap.fill(text, width=TEXT_WIDTH)
