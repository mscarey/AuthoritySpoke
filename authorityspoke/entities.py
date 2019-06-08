"""
Classes representing things that exist in the outside world,
that can be mentioned in legal rules. Not concepts that
derive their meaning from litigation, such as a legal
Fact, an Allegation, a Pleading, etc.

Because of the challenge of describing the significance
of classifying an object as one kind of Entity rather than
another, all of Entity's subclasses might be collapsed into
a single Entity class.
"""

from __future__ import annotations

from typing import Dict, Iterator, Optional

from authorityspoke.factors import Factor, Entity, new_context_helper

from dataclasses import astuple, dataclass


class Association(Entity):
    """
    An :class:`Entity` representing a set of people such as members or shareholders,
    or a business such as a corporation or LLC, but not an unincorporated
    business such as a sole proprietorship.
    """


class Human(Entity):
    """
    A "natural person" mentioned as an :class:`Entity` in a factor. On the distinction
    between "human" and "person", see `Slaughter-House Cases
    <https://www.courtlistener.com/opinion/88661/slaughter-house-cases/>`_
    , 83 U.S. 36, 99.
    """


class Event(Entity):
    """
    An Event may be referenced as an :class:`Entity` in a
    :class:`Predicate`\'s ``content``.
    *See* Lepore, Ernest. Meaning and Argument: An Introduction to Logic
    Through Language. Section 17.2: The Event Approach.
    """
