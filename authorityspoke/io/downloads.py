"""Downloading data that can be converted to authorityspoke objects."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from justopinion.download import CAPClient, CaseAccessProjectAPIError

from authorityspoke.decisions import CAPCitation, Decision
from authorityspoke.io.schemas_json import RawDecision, DecisionSchema
