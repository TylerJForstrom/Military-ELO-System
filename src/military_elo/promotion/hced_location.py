"""Fail-closed HCED location transcription helpers.

The audit-owned quarantine manifests are supplied by stable candidate ID.  No
event name, year, slug, coordinate cluster, or country spelling participates in
the runtime quarantine decision.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import AbstractSet, Any


_PLAIN_NUMBER = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$")

HCED_LOCATION_MACHINE_LOCAL_AUDIT_SNAPSHOT_SHA256 = (
    "670300a7dd145c675fa5219d3d6cbe371d1437c358174650c3124baeb9eea954"
)
HCED_LOCATION_QUARANTINE_POLICY_SHA256 = (
    "6cc38d85f4f6656212a5ae14a2afe86e16f9416bd5167c373327200ecf29ad4e"
)
HCED_POINT_QUARANTINE_CANDIDATE_SHA256 = (
    "16f5dcd54bb3dd3e58e16dadd97f652a5fa03b790d641b934a69212a5488e3ba"
)
HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256 = (
    "84d8ef956f580256e028f07d4ca988a30b17bdd3b601cfe6db5f60153b335ad9"
)
HCED_POINT_QUARANTINE_EVENT_SHA256 = (
    "f606bd3bfed52c21e587edf9e0b79719bc7d6aa1370ff7e029294e579ff8bfad"
)
HCED_COUNTRY_QUARANTINE_EVENT_SHA256 = (
    "52cbb0636bbb0707e9fdce9127cfb4dc4a744f43fab29fcd9deb4cddb1793eb0"
)
# Wave 5 is the immutable base to which reviewed lane manifests are added
# during release construction. The final pins below are independently measured
# from the coupled Wave 7 release/registry build and consumed by dashboard and
# coverage validation.
HCED_WAVE5_CANDIDATE_BINDINGS = 4_195
HCED_WAVE5_POINT_ASSERTIONS = 4_158
HCED_WAVE5_COUNTRY_ASSERTIONS = 4_115
HCED_WAVE5_PROVENANCE_OBJECTS = 4_162
HCED_EXPECTED_CANDIDATE_BINDINGS = 4_796
HCED_EXPECTED_CANDIDATE_KEYED_REVIEWED_CONTRACTS = 487
HCED_EXPECTED_POINT_ASSERTIONS = 4_712
HCED_EXPECTED_COUNTRY_ASSERTIONS = 4_709
HCED_EXPECTED_PROVENANCE_OBJECTS = 4_758
HCED_EXPECTED_QUARANTINE_UNION = 132
HCED_EXPECTED_QUARANTINE_OVERLAP = 38
HCED_SOURCE_BLANK_COUNTRY_IDS = frozenset({"hced-Amadiye1973-1"})
HCED_LOCATION_WARNING = (
    "HCED location fields are unreviewed source assertions. Quarantined values "
    "are withheld, not corrected. Coordinate precision is unknown."
)

# Mechanically copied from data/policy/hced-location-quarantine.tsv after
# checksum verification. Runtime decisions use these exact stable candidate
# IDs only. The machine-local audit snapshot digest above is provenance for
# the original Wave 3 review, not a clean-checkout release gate.
HCED_POINT_QUARANTINE_CANDIDATE_IDS = (
    "hced-Aghdash Awkh1831-1",
    "hced-Akhulgo1839-1",
    "hced-Aleutians1942-1",
    "hced-Ap Bac1963-1",
    "hced-Apacheta1814-1",
    "hced-Attu1943-1",
    "hced-Ayacucho1824-1",
    "hced-Bacolod1903-1",
    "hced-Bagh Dera1788-1",
    "hced-Bagh1919-1",
    "hced-Balkans1941-1",
    "hced-Balkans1944-1",
    "hced-Bayan1902-1",
    "hced-Belfast1900-1",
    "hced-Belfast1901-1",
    "hced-Blackwater1598-1",
    "hced-Bridge634-1",
    "hced-Bud Bagsak1913-1",
    "hced-Burtinah1839-1",
    "hced-Cape St Vincent1797-1",
    "hced-Chacaltaya1814-1",
    "hced-Clontarf1014-1",
    "hced-Clontibret1595-1",
    "hced-Crazy Woman Creek1876-1",
    "hced-Crooked Creek1859-1",
    "hced-Dublin (2nd)1171-1",
    "hced-Dysert ODea1318-1",
    "hced-Empress Augusta Bay1943-1",
    "hced-Focchies1649-1",
    "hced-Ford of the Biscuits1594-1",
    "hced-Freeman's Farm1776-1",
    "hced-Gilbert Islands1943-1",
    "hced-Girgil1847-1",
    "hced-Groenkloof1901-1",
    "hced-Guadalete711-1",
    "hced-Gumburu1903-1",
    "hced-Harenc1098-1",
    "hced-Huon Peninsula1943-1",
    "hced-Issus-333-1",
    "hced-Iwo Jima1945-1",
    "hced-Junin1824-1",
    "hced-Kagul Lagoon1574-1",
    "hced-Komandorski Islands1943-1",
    "hced-Kota Bharu1941-1",
    "hced-Kudarangan1904-1",
    "hced-Lake Seit1903-1",
    "hced-Limerick1651-1",
    "hced-Lizard1707-1",
    "hced-Malala1905-1",
    "hced-Mitla Pass1956-1",
    "hced-Monte Suella1866-1",
    "hced-Montserrat1811-1",
    "hced-Monzon1809-1",
    "hced-Ningyuan1626-1",
    "hced-Nish1809-1",
    "hced-Niumaozhai1619-1",
    "hced-O'Connell Street1922-1",
    "hced-Pearl Harbour1941-1",
    "hced-Perimeter (2nd)1950-1",
    "hced-Plum Creek, Nebraska1867-1",
    "hced-Plum Creek, Texas1840-1",
    "hced-Porto Praya1781-1",
    "hced-Rennell Island1943-1",
    "hced-Riviera1944-1",
    "hced-Rush Springs1858-1",
    "hced-Salaita1916-1",
    "hced-Sandfontein1914-1",
    "hced-Santa Rosa Island1861-1",
    "hced-Sas van Gent1644-1",
    "hced-Slaak1631-1",
    "hced-Solomon Forks1857-1",
    "hced-St Pierre and Miquelon1793-1",
    "hced-Tara980-1",
    "hced-Tatishchevo1774-1",
    "hced-Torata1823-1",
    "hced-Tristan de Cunha1815-1",
    "hced-Vaal Kranz1900-1",
    "hced-Villa Glori1867-1",
    "hced-Wake1941-1",
    "hced-Walkers Creek1844-1",
    "hced-Waynesborough, Georgia1864-1",
    "hced-Whitehaven1778-1",
    "hced-Xiaoling1631-1",
    "hced-Zhovnyne1638-1",
)
HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS = (
    "hced-Aghdash Awkh1831-1",
    "hced-Aleutians1942-1",
    "hced-Ap Bac1963-1",
    "hced-Atlantic1915-1917-1",
    "hced-Atlantic1939-1945-1",
    "hced-Attu1943-1",
    "hced-Augusta, Sicily1676-1",
    "hced-Bagh Dera1788-1",
    "hced-Bagh1919-1",
    "hced-Balkans1941-1",
    "hced-Balkans1944-1",
    "hced-Belfast1900-1",
    "hced-Belfast1901-1",
    "hced-Bismarck1941-1",
    "hced-Burtinah1839-1",
    "hced-Cape Engano1944-1",
    "hced-Cape St Vincent1797-1",
    "hced-Chieveley1899-1",
    "hced-Czernowitz1914-1",
    "hced-Czernowitz1916-1",
    "hced-Dogger Bank1781-1",
    "hced-Dogger Bank1915-1",
    "hced-Empress Augusta Bay1943-1",
    "hced-Es Salt (1st)1918-1",
    "hced-Es Salt (2nd)1918-1",
    "hced-Fort Erie (2nd)1814-1",
    "hced-Fort Erie1812-1",
    "hced-Fort Erie1814-1",
    "hced-Freeman's Farm1776-1",
    "hced-Gilbert Islands1943-1",
    "hced-Glowworm1940-1",
    "hced-Gumburu1903-1",
    "hced-Han, Korea1950-1",
    "hced-Hansan1592-1",
    "hced-Harenc1098-1",
    "hced-Helvetia1900-1",
    "hced-Huj1917-1",
    "hced-Huon Peninsula1943-1",
    "hced-Illig1904-1",
    "hced-Iwo Jima1945-1",
    "hced-Java Sea1941-1942-1",
    "hced-Kagul Lagoon1574-1",
    "hced-Kagul1770-1",
    "hced-Komandorski Islands1943-1",
    "hced-Kota Bharu1941-1",
    "hced-Kumanovo1912-1",
    "hced-La Maddalena1793-1",
    "hced-Lake Prespa1917-1",
    "hced-Lizard1707-1",
    "hced-Mariana Islands1944-1",
    "hced-Mitla Pass1956-1",
    "hced-Montserrat1811-1",
    "hced-Monzon1809-1",
    "hced-Noryang1598-1",
    "hced-Paardeberg1900-1",
    "hced-Pearl Harbour1941-1",
    "hced-Perimeter (2nd)1950-1",
    "hced-Pescadores1885-1",
    "hced-Pescadores1895-1",
    "hced-Plamam Mapu1965-1",
    "hced-Pork Chop Hill1953-1",
    "hced-Porto Praya1781-1",
    "hced-Pruth1770-1",
    "hced-Rennell Island1943-1",
    "hced-Reunion1810-1",
    "hced-Riviera1944-1",
    "hced-Rymenant1578-1",
    "hced-Sachon1592-1",
    "hced-Sachon1598-1",
    "hced-Saints1782-1",
    "hced-Sandfontein1914-1",
    "hced-Santa Rosa Island1861-1",
    "hced-Sas van Gent1644-1",
    "hced-St Kitts1782-1",
    "hced-St Kitts1805-1",
    "hced-St Lucia1778-1",
    "hced-St Lucia1780-1",
    "hced-St Lucia1794-1",
    "hced-St Lucia1796-1",
    "hced-St Lucia1803-1",
    "hced-St Paul1809-1",
    "hced-St Pierre and Miquelon1793-1",
    "hced-Tristan de Cunha1815-1",
    "hced-Wake1941-1",
    "hced-Whitehaven1778-1",
    "hced-Zand1900-1",
)
HCED_POINT_QUARANTINE_IDS = frozenset(HCED_POINT_QUARANTINE_CANDIDATE_IDS)
HCED_COUNTRY_QUARANTINE_IDS = frozenset(HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS)


def hced_candidate_id(candidate: Mapping[str, Any]) -> str:
    """Return the exact stable candidate ID without coercion or reconstruction."""

    value = candidate.get("candidate_id")
    if not isinstance(value, str):
        raise TypeError("HCED candidate_id must be a string")
    if not value.strip():
        raise ValueError("HCED candidate_id must be non-blank")
    if value != value.strip():
        raise ValueError("HCED candidate_id must not contain surrounding whitespace")
    return value


def _hced_coordinate(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if value != text or not text or _PLAIN_NUMBER.fullmatch(text) is None:
            return None
        value = text
    elif not isinstance(value, (int, float)):
        return None
    try:
        coordinate = float(value)
    except (OverflowError, TypeError, ValueError):
        return None
    return coordinate if math.isfinite(coordinate) else None


def parse_hced_point(latitude: Any, longitude: Any) -> dict[str, Any] | None:
    """Parse one HCED pair as a GeoJSON Point in longitude/latitude order.

    This source-specific gate rejects booleans, blanks, malformed or non-finite
    numbers, out-of-range ordinates, and the HCED sentinel pair ``(0, 0)``.  It
    never swaps or otherwise infers coordinates.  General GeoJSON validation
    remains independent and continues to allow the valid geographic point
    ``[0, 0]``.
    """

    parsed_latitude = _hced_coordinate(latitude)
    parsed_longitude = _hced_coordinate(longitude)
    if parsed_latitude is None or parsed_longitude is None:
        return None
    if not -90.0 <= parsed_latitude <= 90.0:
        return None
    if not -180.0 <= parsed_longitude <= 180.0:
        return None
    if parsed_latitude == 0.0 and parsed_longitude == 0.0:
        return None
    return {
        "type": "Point",
        "coordinates": [parsed_longitude, parsed_latitude],
    }


def build_hced_location_fields(
    candidate: Mapping[str, Any],
    *,
    point_quarantine_ids: AbstractSet[str],
    country_quarantine_ids: AbstractSet[str],
) -> dict[str, Any]:
    """Build candidate-bound location fields under explicit audit manifests."""

    candidate_id = hced_candidate_id(candidate)
    result: dict[str, Any] = {"hced_candidate_id": candidate_id}

    country = candidate.get("modern_location_country")
    if candidate_id not in country_quarantine_ids and country is not None:
        if not isinstance(country, str):
            raise TypeError("HCED modern_location_country must be a string or null")
        if country.strip():
            if country != country.strip():
                raise ValueError(
                    "HCED modern_location_country must not contain surrounding whitespace"
                )
            result["modern_location_country"] = country

    if candidate_id not in point_quarantine_ids:
        geometry = parse_hced_point(
            candidate.get("latitude"), candidate.get("longitude")
        )
        if geometry is not None:
            result["geometry"] = geometry

    if "modern_location_country" in result or "geometry" in result:
        source_record_id = candidate.get("source_record_id")
        if not isinstance(source_record_id, str):
            raise TypeError("HCED source_record_id must be a string")
        if not source_record_id.strip():
            raise ValueError("HCED source_record_id must be non-blank")
        if source_record_id != source_record_id.strip():
            raise ValueError(
                "HCED source_record_id must not contain surrounding whitespace"
            )
        result["location_provenance"] = {
            "source_id": "hced_dataset",
            "source_record_id": source_record_id,
            "assertion_status": "unreviewed_source_assertion",
            "coordinate_precision": "unknown",
        }

    return result
