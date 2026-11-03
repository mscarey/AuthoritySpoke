from legislice.download import Client
from legislice.enactments import EnactmentPassage
from anchorpoint.textselectors import TextQuoteSelector


def passage_from_quotes(
    client: Client, node: str, quotes: list[str] | None = None
) -> EnactmentPassage:
    enactment = client.read(node)
    if not quotes:
        return enactment.select_all()
    selection = enactment.select(TextQuoteSelector(exact=quotes[0]))
    for quote in quotes[1:]:
        selection.select_more(TextQuoteSelector(exact=quote))
    return selection
