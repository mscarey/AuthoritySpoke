"""
Functions to load JSON or XML files for conversion into authorityspoke objects.

Will usually hand off data to the io.readers module to create authorityspoke objects.
"""
import json
import pathlib

from typing import Any, Dict, List, Iterator, Optional, Tuple, Union

import yaml

from legislice.download import Client


from authorityspoke.decisions import Decision, DecisionReading
from authorityspoke.holdings import Holding
from authorityspoke.opinions import AnchoredHoldings
from authorityspoke.rules import Rule

from authorityspoke.io import filepaths, readers
from authorityspoke.io.name_index import Mentioned
from authorityspoke.io.schemas_yaml import (
    RawEnactment,
    RawFactor,
    RawHolding,
    RawDecision,
)


def load_anchored_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> Dict[str, Union[Dict[str, RawFactor], Dict[str, RawEnactment], List[RawHolding]]]:
    r"""
    Load list of records from YAML or JSON to create :class:`.Holding`\s with text selectors.

    :param filename:
        the name of the JSON file to look in for :class:`Holding`
        data in the format that lists ``mentioned_factors``
        followed by a list of holdings.

    :param directory:
        the path of the directory containing the JSON file.

    :param filepath:
        Complete path to the XML file representing the :class:`.Code`,
        including filename.

    :returns:
        a list of :class:`Holding`\s from a JSON file in the
        ``example_data/holdings`` subdirectory, from a JSON
        file.
    """
    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="holdings"
    )

    with open(validated_filepath, "r") as f:
        if validated_filepath.suffix == ".yaml":
            holdings = yaml.safe_load(f)
        else:
            holdings = json.load(f)

    return holdings


def load_holdings(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> Dict[str, Union[Dict[str, RawFactor], Dict[str, RawEnactment], List[RawHolding]]]:
    r"""
    Load a list of records from JSON to create :class:`.Holding`\s.

    :param filename:
        the name of the JSON file to look in for :class:`Holding`
        data in the format that lists ``mentioned_factors``
        followed by a list of holdings.

    :param directory:
        the path of the directory containing the JSON file.

    :param filepath:
        Complete path to the XML file representing the :class:`.Code`,
        including filename.

    :returns:
        a list of :class:`Holding`\s from a JSON file in the
        ``example_data/holdings`` subdirectory, from a JSON
        file.
    """
    holdings = load_anchored_holdings(
        filename=filename, directory=directory, filepath=filepath
    )

    if isinstance(holdings, Dict):
        return holdings["holdings"]
    return holdings


def load_rules_with_index(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    client: Optional[Client] = None,
    many: bool = True,
) -> Tuple[List[Rule], Mentioned]:
    r"""
    Read :class:`.Rule`\s from a file.

    Even though this function will generate :class:`.Rule`\s instead
    of :class:`.Holding`\s, it uses the :func:`load_holding` function.
    Some fields that can exist in a :class:`.Holding` object (rule_valid,
    decided, exclusive) are not applicable to :class:`.Rule`\s.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.

    :param regime:
        The regime to reference for the :class:`Enactment`\s
        mentioned in the holding.
    """
    raw_rules = load_holdings(filename=filename, directory=directory, filepath=filepath)
    return readers.read_rules_with_index(raw_rules, client=client, many=many)


def read_holdings_from_file(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    client: Optional[Client] = None,
) -> List[Holding]:
    r"""
    Read holdings from a file.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.

    :param client:
        The client with an API key to download :class:`Enactment`\s
        mentioned in the holding.
    """
    raw_holdings = load_holdings(
        filename=filename, directory=directory, filepath=filepath
    )

    return readers.read_holdings(raw_holdings, client=client)


def read_anchored_holdings_from_file(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
    client: Optional[Client] = None,
) -> AnchoredHoldings:
    r"""
    Read holdings from file, with Opinion text anchors for holdings and factors.

    This function can accept a file containing :class:`.authorityspoke.holdings.Holding`
    summaries in the YAML format
    that may contain abbreviations and expandable named entities.

    In the example below, a :class:`~authorityspoke.io.fake_enactments.FakeClient` is used to
    add fields to :class:`~legislice.enactments.Enactment`\s in the Holding
    objects, to avoid using the network or making API calls. The
    real :class:`~authorityspoke.io.downloads.LegisClient` class
    would also have worked (with an appropriate API key).

        >>> from authorityspoke.io.fake_enactments import FakeClient
        >>> fake_client = FakeClient.from_file("usc.json")
        >>> filepath = filepaths.make_filepath(filename="holding_mazza_alaluf.yaml")
        >>> with open(filepath, "r") as f:
        ...     yaml.safe_load(f)
        {'holdings': [{'inputs': [{'type': 'fact', 'content': "{Mazza-Alaluf} used Mazza-Alaluf's business {Turismo Costa Brava} to commit the New York offense of engaging in the business of receiving money for transmission or transmitting the same, without a license therefor"}], 'outputs': [{'type': 'fact', 'content': 'Mazza-Alaluf operated Turismo Costa Brava without an appropriate money transmitting license in a State where such operation was punishable as a misdemeanor or a felony under State law', 'anchors': "we conclude that sufficient evidence supports Mazza-Alaluf's convictions under 18 U.S.C. § 1960(b)(1)(A) for conspiring to operate and operating a money transmitting business without appropriate state licenses.", 'name': 'operated without license'}], 'enactments': [{'node': '/us/usc/t18/s1960/b/1', 'anchors': 'state money transmitting licenses, see |18 U.S.C. § 1960(b)(1)(A)|', 'exact': 'is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law, whether or not the defendant knew that the operation was required to be licensed or that the operation was so punishable', 'name': 'state money transmitting license provision'}], 'universal': True}, {'inputs': ['operated without license', {'type': 'fact', 'content': 'Mazza-Alaluf operated Turismo Costa Brava as a business', 'anchors': 'Mazza-Alaluf does not contest that he owned and managed Turismo'}, {'type': 'fact', 'content': 'Turismo Costa Brava was a money transmitting business', 'anchors': 'record evidence that Turismo conducted substantial money transmitting business in the three states'}], 'despite': [{'type': 'fact', 'content': 'Turismo Costa Brava was a domestic financial institution', 'truth': False, 'anchors': 'without respect to whether or not Turismo was a "domestic financial institution"'}], 'outputs': [{'type': 'fact', 'content': 'Mazza-Alaluf committed the offense of conducting a money transmitting business without a license required by state law', 'anchors': 'a crime to operate a money transmitting business without appropriate state licenses,'}], 'enactments': ['state money transmitting license provision'], 'enactments_despite': [{'node': '/us/usc/t31/s5312/b/1', 'anchors': ['§ 5312(b)(1) (defining "domestic financial institution")']}], 'anchors': [{'prefix': 'Accordingly, we conclude that the', 'suffix': 'In any event'}], 'universal': True, 'mandatory': True}]}
        >>> result = read_anchored_holdings_from_file(filepath=filepath, client=fake_client)
        >>> selector = result.named_anchors["the fact it was false that <Turismo Costa Brava> was a domestic financial institution"][0]
        >>> selector.exact
        'without respect to whether or not Turismo was a "domestic financial institution"'
        >>> print(result.holdings[0].outputs[0])
        the fact that <Mazza-Alaluf> operated <Turismo Costa Brava> without an appropriate money transmitting license in a State where such operation was punishable as a misdemeanor or a felony under State law
    """
    raw_holdings = load_anchored_holdings(
        filename=filename, directory=directory, filepath=filepath
    )
    return readers.read_holdings_with_anchors(raw_holdings, client=client)


def load_decision(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> RawDecision:
    r"""
    Load file containing a judicial decision with one or more opinions.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.
    """

    validated_filepath = filepaths.make_filepath(
        filename, directory, filepath, default_folder="cases"
    )

    with open(validated_filepath, "r") as f:
        decision_dict = json.load(f)

    return decision_dict


def load_decision_as_reading(
    filename: Optional[str] = None,
    directory: Optional[pathlib.Path] = None,
    filepath: Optional[pathlib.Path] = None,
) -> DecisionReading:
    r"""
    Load file containing a judicial decision with one or more opinions.

    Relies on the JSON format from the `Caselaw Access Project
    API <https://api.case.law/v1/cases/>`_.

    :param filename: The name of the input JSON file.

    :param directory: The directory where the input JSON file is located.

    :param filepath:
        Complete path to the JSON file representing the :class:`.Opinion`,
        including filename.
    """

    loaded = load_decision(filename=filename, directory=directory, filepath=filepath)
    return readers.read_decision(loaded)
