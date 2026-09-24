"""Parser for schema_id `dbxlisting.v1` -- the Databricks Marketplace sitemap.

WHAT MOVES HERE IS A DATA PRODUCT LEAVING THE MARKET

The sitemap is the only observable, and unusually it is also the only place any
FACT about a listing appears. The detail page is 58,299 chars with `<title>
Databricks Marketplace`, no og:title, no h1, no meta description and no JSON-LD;
its only embedded JSON is feature flags. There is no product name on the product
page. Everything below is read out of the URL.

THE URL IS /details/<uuid>/<Vendor>_<Product-Name>

    /details/67f372d9-.../CoreLogic_Rent-Amount-Model

All 2,211 listings carry the name segment, so the uuid is a stable key AND the
product and vendor are free. An earlier screen of this source recorded the
opposite -- "uuid only, no name" -- from a single URL that happened to end in a
trailing slash, and planned a 2,211-page pass to resolve names while listings
were still live. None of that is needed.

THE VENDOR SPLITS ON THE UNDERSCORE, NOT THE HYPHEN. Product names are
hyphen-separated and vendor names contain hyphens themselves -- `john-snow-labs`
splits into three useless tokens on `-` and appeared as the second largest
"vendor" in a first count. The underscore is the real boundary and gives 385
vendors, of which `techsalerator` alone holds 242 listings, 11% of the store.

NO DENOMINATOR EXISTS. Nothing here is a popularity signal.
"""
import re
from urllib.parse import unquote

from wss import derive

PARSER_VERSION = "1"
SCHEMA_ID = "dbxlisting.v1"

# uuid, then an optional <Vendor>_<Product> segment.
LISTING = re.compile(r"/details/([0-9a-f]{8}-[0-9a-f-]{27})(?:/([^<\s]+))?")


def parse(body: bytes, ctx: derive.ParseContext):
    text = body.decode("utf-8", "replace")
    seen = set()
    for uuid, tail in LISTING.findall(text):
        if uuid in seen:
            continue
        seen.add(uuid)

        yield derive.Observation(entity_id=uuid, metric="listed", value=1, unit="count")
        if not tail:
            continue
        name = unquote(tail).rstrip("/")
        yield derive.Observation(entity_id=uuid, metric="listing_name", value=name)
        # Vendor is everything before the FIRST underscore. Splitting on "-"
        # shreds hyphenated vendor names; see the docstring.
        if "_" in name:
            yield derive.Observation(entity_id=uuid, metric="vendor",
                                     value=name.split("_", 1)[0])
        # Databricks marks trial/sample products in the name itself. It is the
        # only product attribute available anywhere, so it is emitted.
        if "-SAMPLE-" in name.upper() or name.upper().startswith("SAMPLE"):
            yield derive.Observation(entity_id=uuid, metric="is_sample", value="true")


derive.register(SCHEMA_ID, parse, PARSER_VERSION)
