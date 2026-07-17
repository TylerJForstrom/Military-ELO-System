"""Exact-label Wave 8 contracts for HCED ``Saudis`` and ``Rashidis`` rows.

The raw labels are routing keys, never reusable identities.  Every emitted
participant is an event-bounded formation.  The lane also owns the composite
``Saudis, Qasim`` spelling only because that exact row is jointly blocked by
``Rashidis`` and the composite label; no generic Saudi, Rashidi, dynastic, or
modern-state fallback is opened.

Unknown or conflicting outcomes remain holds and are never converted to draws.
The sole terminal exclusion is backed by sources that describe a surrender
without fighting rather than a competitive engagement.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping

from .common import _slug, normalize_label
from .wave7_global import canonical_hced_row_sha256
from .wave8_exact import (
    install_exact_entities,
    install_exact_sources,
    promote_exact_hced_contracts,
    validate_exact_hced_inventory,
)
from .wave8_first_saudi import WAVE8_FIRST_SAUDI_RESERVED_IDS


__all__ = (
    "WAVE8_SAUDI_RASHIDI_CONTRACT_IDS",
    "WAVE8_SAUDI_RASHIDI_CONTRACTS",
    "WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES",
    "WAVE8_SAUDI_RASHIDI_ENTITIES",
    "WAVE8_SAUDI_RASHIDI_EXPECTED_CANDIDATE_IDS",
    "WAVE8_SAUDI_RASHIDI_FINAL_AUDIT_SIGNATURE",
    "WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT",
    "WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS",
    "WAVE8_SAUDI_RASHIDI_HOLD_IDS",
    "WAVE8_SAUDI_RASHIDI_HOLDS",
    "WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS",
    "WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT",
    "WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT",
    "WAVE8_SAUDI_RASHIDI_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_SAUDI_RASHIDI_LOCATION_REVIEW",
    "WAVE8_SAUDI_RASHIDI_NONPROMOTIONS",
    "WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES",
    "WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT",
    "WAVE8_SAUDI_RASHIDI_RESERVED_IDS",
    "WAVE8_SAUDI_RASHIDI_ROW_INVENTORY",
    "WAVE8_SAUDI_RASHIDI_SOURCES",
    "WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS",
    "WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS",
    "install_wave8_saudi_rashidi_entities",
    "install_wave8_saudi_rashidi_sources",
    "promote_wave8_saudi_rashidi_contracts",
    "validate_wave8_saudi_rashidi_integration_dispositions",
    "validate_wave8_saudi_rashidi_queue_contracts",
    "wave8_saudi_rashidi_audit_signature",
    "wave8_saudi_rashidi_cohort_counts",
    "wave8_saudi_rashidi_counts",
    "wave8_saudi_rashidi_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 exact HCED Saudi-Rashidi forces audit"
_EVENT_ID_PREFIX = "hced_wave8_saudi_rashidi_"
_OWNED_NORMALIZED_LABELS = frozenset({"rashidis", "saudis", "saudis qasim"})

WAVE8_SAUDI_RASHIDI_FINAL_AUDIT_SIGNATURE = (
    "c0eed830eff323042ba1904d71752f26c2f49602e02fcab44194a278d4c0e1c0"
)


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "linked_reference",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": [
            "identity_boundary_or_context_reference",
            "outcome",
        ],
    }


WAVE8_SAUDI_RASHIDI_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_saudi_rashidi_abedin_kcl_2002",
        "Abdul Aziz Al-Saud and the Great Game in Arabia, 1896-1946",
        "https://kclpure.kcl.ac.uk/portal/files/2925835/397151.pdf",
        "King's College London Research Portal",
        "doctoral_dissertation",
        "kings_college_london_research",
    ),
    _source(
        "wave8_saudi_rashidi_al_azma_durham_1999",
        "The role of the Ikhwan under 'Abdul-'Aziz Al Sa'ud, 1916-1934",
        "https://etheses.dur.ac.uk/1472/1/1472.pdf",
        "Durham University E-Theses",
        "doctoral_dissertation",
        "durham_university_etheses",
    ),
    _source(
        "wave8_saudi_rashidi_almutairi_uea_2019",
        "British-Saudi Relations 1902-1932",
        "https://ueaeprints.uea.ac.uk/id/eprint/94658/",
        "University of East Anglia Digital Repository",
        "doctoral_dissertation",
        "university_east_anglia_repository",
    ),
    _source(
        "wave8_saudi_rashidi_alotaibi_bangor_2017",
        "Ibn Sa'ud and Britain: Early changing relationship and pre-state formation 1902-1914",
        "https://pure.bangor.ac.uk/ws/portalfiles/portal/20572121/file",
        "Bangor University Research Portal",
        "doctoral_dissertation",
        "bangor_university_research",
    ),
    _source(
        "wave8_saudi_rashidi_britannica_1926",
        "Arabia",
        "https://en.wikisource.org/wiki/Page:EB1926_-_Supplement_Volume_1.pdf/196",
        "Encyclopaedia Britannica, 13th edition supplement",
        "contemporary_reference_work",
        "encyclopaedia_britannica_1926",
    ),
    _source(
        "wave8_saudi_rashidi_bunzel_princeton_2023",
        "Wahhabism: The History of a Militant Islamic Movement",
        "https://www.jstor.org/stable/j.ctv321jd1x",
        "Princeton University Press / JSTOR",
        "academic_monograph",
        "princeton_university_press",
    ),
    _source(
        "wave8_saudi_rashidi_cambridge_al_rasheed_2010",
        "The emerging state, 1902-1932",
        "https://www.cambridge.org/core/books/abs/history-of-saudi-arabia/emerging-state-19021932/89B3D34A6AC46FB63ACC9387D19C9B10",
        "Cambridge University Press",
        "academic_monograph_chapter",
        "cambridge_history_saudi_arabia",
    ),
    _source(
        "wave8_saudi_rashidi_gungordu_aybu_2015",
        "Turkey-Saudi Arabia relations since the establishment of the Saudi Kingdom",
        "https://avesis.aybu.edu.tr/yonetilen-tez/03c04be1-496a-4110-bbd1-b86675463ef3/turkey-saudi-arabia-relations-since-the-establishment-of-the-saudi-kingdom",
        "Ankara Yildirim Beyazit University Research Portal",
        "masters_dissertation",
        "ankara_yildirim_beyazit_university",
    ),
    _source(
        "wave8_saudi_rashidi_loc_country_profile_2006",
        "Saudi Arabia: Country Profile",
        "https://tile.loc.gov/storage-services/master/frd/copr/Saudi_Arabia.pdf",
        "Library of Congress Federal Research Division",
        "institutional_country_profile",
        "library_of_congress_federal_research",
    ),
    _source(
        "wave8_saudi_rashidi_loc_country_study_1992",
        "Saudi Arabia: A Country Study",
        "https://tile.loc.gov/storage-services/master/frd/frdcstdy/sa/saudiarabiacount00metz_0/saudiarabiacount00metz_0.pdf",
        "Library of Congress Federal Research Division",
        "institutional_country_study",
        "library_of_congress_country_studies",
    ),
    _source(
        "wave8_saudi_rashidi_qdl_jarrab_1915",
        "The Death of Captain Shakespear, 1915",
        "https://qdl.qa/en/death-captain-shakespear-1915",
        "Qatar Digital Library / British Library",
        "curated_primary_source",
        "british_library_india_office_records",
    ),
    _source(
        "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        "Vision or Mirage: Saudi Arabia at the Crossroads",
        "https://www.bloomsbury.com/us/vision-or-mirage-9781838605933/",
        "I.B. Tauris / Bloomsbury",
        "academic_trade_monograph",
        "bloomsbury_ib_tauris",
    ),
    _source(
        "wave8_saudi_rashidi_saudipedia_dilam",
        "Ad-Dilam Wall",
        "https://saudipedia.com/en/ad-dilam-wall",
        "Saudipedia / Ministry of Media, Saudi Arabia",
        "official_history",
        "saudipedia_heritage_commission",
    ),
    _source(
        "wave8_saudi_rashidi_saudipedia_rawdat",
        "Battle of Rawdat Muhanna",
        "https://saudipedia.com/%D9%85%D8%B9%D8%B1%D9%83%D8%A9-%D8%B1%D9%88%D8%B6%D8%A9-%D9%85%D9%87%D9%86%D8%A7",
        "Saudipedia / Ministry of Media, Saudi Arabia",
        "official_history",
        "saudipedia_king_abdulaziz_history",
    ),
)

_SOURCE_BY_ID = {
    str(source["id"]): source for source in WAVE8_SAUDI_RASHIDI_SOURCES
}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    year: int,
    source_ids: Iterable[str],
    boundary: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": year,
        "end_year": year,
        "region": "Arabian Peninsula",
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary
            + " No rating is inherited by a Saudi or Rashidi dynasty/state "
            "label, the modern Kingdom of Saudi Arabia, or any other campaign "
            "formation."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


_MULAYDA_RASHIDI = "muhammad_ibn_abdullah_rashidi_army_mulayda_1891"
_MULAYDA_COALITION = "abd_al_rahman_qassim_coalition_mulayda_1891"
_RIYADH_SAUDI = "ibn_saud_riyadh_raiding_party_1902"
_RIYADH_RASHIDI = "ajlan_rashidi_riyadh_garrison_1902"
_DILAM_SAUDI = "ibn_saud_dilam_force_1902"
_DILAM_RASHIDI = "ibn_rashid_dilam_force_1902"
_UNAYZAH_SAUDI = "ibn_saud_unayzah_assault_force_1904"
_UNAYZAH_RASHIDI = "majid_ibn_hamoud_rashidi_unayzah_force_1904"
_RAWDAT_SAUDI = "ibn_saud_rawdat_muhanna_force_1906"
_RAWDAT_RASHIDI = "abdulaziz_ibn_mutaib_rashidi_force_rawdat_muhanna_1906"
_HOFUF_SAUDI = "ibn_saud_hofuf_assault_force_1913"
_HOFUF_OTTOMAN = "ottoman_hofuf_garrison_1913"
_KANZAN_AJMAN = "dhaydan_ibn_hithlayn_ajman_force_kanzan_1915"
_KANZAN_SAUDI = "ibn_saud_kanzan_force_1915"
_TURABAH_IKHWAN = "khalid_sultan_ikhwan_force_turabah_1919"
_TURABAH_HASHEMITE = "abdullah_hashemite_army_turabah_1919"
_MEDINA_SAUDI = "ibn_saud_medina_siege_force_1925"
_MEDINA_HASHEMITE = "hashemite_medina_garrison_1925"
_SABILLA_LOYALIST = "ibn_saud_loyalist_army_sabilla_1929"
_SABILLA_REBEL = "faisal_sultan_rebel_ikhwan_sabilla_1929"
_UMM_RADHMAH_LOYALIST = "ibn_musaid_loyal_shammar_force_umm_radhmah_1929"
_UMM_RADHMAH_REBEL = "azaiyiz_mutair_ikhwan_force_umm_radhmah_1929"


WAVE8_SAUDI_RASHIDI_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _MULAYDA_RASHIDI,
        "Muhammad ibn Abdullah Al Rashid's army at al-Mulayda in 1891",
        "event_bounded_field_army",
        1891,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_bunzel_princeton_2023",
            "wave8_saudi_rashidi_cambridge_al_rasheed_2010",
        ],
        "This identity is limited to the Rashidi army in the 1891 al-Mulayda engagement.",
    ),
    _entity(
        _MULAYDA_COALITION,
        "Abdul Rahman Al Saud-Qassim coalition at al-Mulayda in 1891",
        "event_bounded_coalition",
        1891,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_bunzel_princeton_2023",
        ],
        "This identity combines only the source-attested Saudi and Qassim forces opposed at al-Mulayda.",
    ),
    _entity(
        _RIYADH_SAUDI,
        "Ibn Saud's Riyadh raiding party in January 1902",
        "event_bounded_raiding_party",
        1902,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_loc_country_profile_2006",
        ],
        "This identity covers the small party that entered Riyadh and attacked Ajlan's position in January 1902.",
    ),
    _entity(
        _RIYADH_RASHIDI,
        "Ajlan's Rashidi Riyadh garrison in January 1902",
        "event_bounded_city_garrison",
        1902,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_loc_country_profile_2006",
        ],
        "This identity ends with the January 1902 capture of Ajlan's Riyadh position.",
    ),
    _entity(
        _DILAM_SAUDI,
        "Ibn Saud's force at Dilam in 1902",
        "event_bounded_field_force",
        1902,
        [
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
            "wave8_saudi_rashidi_saudipedia_dilam",
        ],
        "This identity is limited to the force engaged at Dilam in 1902.",
    ),
    _entity(
        _DILAM_RASHIDI,
        "Ibn Rashid's force at Dilam in 1902",
        "event_bounded_field_force",
        1902,
        [
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
            "wave8_saudi_rashidi_saudipedia_dilam",
        ],
        "This identity is limited to the Rashidi force that withdrew after the Dilam engagement.",
    ),
    _entity(
        _UNAYZAH_SAUDI,
        "Ibn Saud's Unayzah assault force in March 1904",
        "event_bounded_assault_force",
        1904,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
        ],
        "This identity covers the force that attacked the Rashidi position and entered Unayzah in March 1904.",
    ),
    _entity(
        _UNAYZAH_RASHIDI,
        "Majid ibn Hamoud's Rashidi force at Unayzah in March 1904",
        "event_bounded_city_force",
        1904,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
        ],
        "This identity ends with the commander's death and the garrison's surrender or flight at Unayzah.",
    ),
    _entity(
        _RAWDAT_SAUDI,
        "Ibn Saud's force at Rawdat Muhanna in 1906",
        "event_bounded_field_force",
        1906,
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_saudipedia_rawdat",
        ],
        "This identity is limited to the Saudi force in the 1906 Rawdat Muhanna engagement.",
    ),
    _entity(
        _RAWDAT_RASHIDI,
        "Abdulaziz ibn Mutaib's Rashidi force at Rawdat Muhanna in 1906",
        "event_bounded_field_force",
        1906,
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_saudipedia_rawdat",
        ],
        "This identity ends with Abdulaziz ibn Mutaib Al Rashid's death in the Rawdat Muhanna fighting.",
    ),
    _entity(
        _HOFUF_SAUDI,
        "Ibn Saud's Hofuf assault force in May 1913",
        "event_bounded_assault_force",
        1913,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        "This identity covers the wall-scaling assault and capture operation at Hofuf in May 1913.",
    ),
    _entity(
        _HOFUF_OTTOMAN,
        "Ottoman Hofuf garrison in May 1913",
        "event_bounded_city_garrison",
        1913,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
        ],
        "This identity ends with the Ottoman garrison's surrender and removal from Hofuf.",
    ),
    _entity(
        _KANZAN_AJMAN,
        "Dhaydan ibn Hithlayn's al-Ajman force at Kanzan in 1915",
        "event_bounded_tribal_force",
        1915,
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_al_azma_durham_1999",
        ],
        "This identity is the al-Ajman force in the Kanzan engagement, not HCED's erroneous Rashidi label.",
    ),
    _entity(
        _KANZAN_SAUDI,
        "Ibn Saud's force at Kanzan in 1915",
        "event_bounded_field_force",
        1915,
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_al_azma_durham_1999",
        ],
        "This identity covers Ibn Saud's force in the Kanzan attack and immediate defeat only.",
    ),
    _entity(
        _TURABAH_IKHWAN,
        "Khalid ibn Luayy and Sultan ibn Bijad's Ikhwan force at Turabah in 1919",
        "event_bounded_allied_force",
        1919,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        "This identity covers the source-attested Ikhwan-led force in the May 1919 Turabah attack.",
    ),
    _entity(
        _TURABAH_HASHEMITE,
        "Abdullah's Hashemite army at Turabah in 1919",
        "event_bounded_field_army",
        1919,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        "This identity is limited to Abdullah's Hashemite army defeated at Turabah in May 1919.",
    ),
    _entity(
        _MEDINA_SAUDI,
        "Ibn Saud's Medina siege force in 1925",
        "event_bounded_siege_force",
        1925,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        "This identity is limited to the force maintaining the 1925 Medina siege through surrender.",
    ),
    _entity(
        _MEDINA_HASHEMITE,
        "Hashemite Medina garrison in 1925",
        "event_bounded_city_garrison",
        1925,
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
        ],
        "This identity ends with the Hashemite garrison's December 1925 surrender after the siege.",
    ),
    _entity(
        _SABILLA_LOYALIST,
        "Ibn Saud's loyalist army at Sabilla in March 1929",
        "event_bounded_combined_arms_force",
        1929,
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        "This identity is limited to Ibn Saud's loyalist army and machine-gun element at Sabilla.",
    ),
    _entity(
        _SABILLA_REBEL,
        "Faisal al-Dawish and Sultan ibn Bijad's rebel Ikhwan at Sabilla in 1929",
        "event_bounded_rebel_force",
        1929,
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        "This identity is limited to the rebel Ikhwan formation defeated at Sabilla in March 1929.",
    ),
    _entity(
        _UMM_RADHMAH_LOYALIST,
        "Ibn Musa'id's loyal Shammar force at Umm Radhmah in 1929",
        "event_bounded_loyal_tribal_force",
        1929,
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        "This identity covers the loyal Shammar force that held the Umm Radhmah wells in September 1929.",
    ),
    _entity(
        _UMM_RADHMAH_REBEL,
        "Azaiyiz al-Dawish's Mutair Ikhwan force at Umm Radhmah in 1929",
        "event_bounded_rebel_force",
        1929,
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        "This identity is limited to the Mutair Ikhwan force defeated at the Umm Radhmah wells.",
    ),
)


_ROW_HASHES: dict[str, str] = {
    "hced-Bukairiya1904-1": "2e449823da05e2699a4a8f88d9d34a475e477f08414ee854926352f77b4238dc",
    "hced-Dilam1902-1": "4cb4c4140779fa565f146e51eac6051a5665fc600f725e9d92490f74e7e49ccd",
    "hced-Hail1921-1": "3eefee2789251ac32073ec2cf2180dc222207b8dd7c33b2393d3a53f843a5f42",
    "hced-Hofuf1913-1": "7aafc03b086f8da6c74ab3676ca0083ac1e60fdf941cd28099459d94b333ce4d",
    "hced-Jirab1915-1": "74bea832c007e7bd23f41918f99ec85c575478bb21dcc62894d980f45b9c537a",
    "hced-Kinzan1915-1": "115804e0f4b20769b32a641c12f3b52029edea4da838b49386bde1a01c2eda38",
    "hced-Medina, Saudi Arabia1925-1": "0532da857627f2998425fdf93f2ff7d8edcbedd886cc4e9deda150523a595541",
    "hced-Mulaydah1891-1": "a0b90809191e2de5db77a58959c334bea9973037624066a87ebd1f125b8b921e",
    "hced-Rawdhat al Muhanna1906-1": "8517d97b66be9ce23958ce1fee46bbac524f90e15623cd9694df610f87931111",
    "hced-Riyadh1887-1": "916cf6857f46133066b8b48c1f1f0b317dcd6c36b31ce3a2a99e2e0c45980aa6",
    "hced-Riyadh1902-1": "1b4a96466f7958ef05c8a0425916cc0c025139771dbcc61ca631ade9d9d5a7c2",
    "hced-Sabalah1929-1": "0096ea71787c644d90655bd117fb63ee1fcd91c0042f44660472208b32c0f645",
    "hced-Taif1924-1": "9c4e3360661f7e35b520cf60fb61e746d5604b6dbc0e89370c3fb60b0ab387e3",
    "hced-Turabah1919-1": "5fa12ceb438a52af8824785224e4dcbff006eacc20ffa9dac20d10a9ab15a212",
    "hced-Umm Urdhumah1929-1": "721f2c449ec859c7e426f2817befff22541edb2e90fddd3e5849f87a016442fb",
    "hced-Unayzah1904-1": "939b47b8934c80c1236b7210327a612e2e9b45e3c5b0781951899dc7e6666463",
}

_ROW_LABELS: dict[str, tuple[str, str]] = {
    "hced-Bukairiya1904-1": ("Saudis", "Ottoman Empire, Rashidis"),
    "hced-Dilam1902-1": ("Saudis", "Rashidis"),
    "hced-Hail1921-1": ("Saudis", "Rashidis"),
    "hced-Hofuf1913-1": ("Saudis", "Ottoman Empire"),
    "hced-Jirab1915-1": ("Rashidis", "Saudis"),
    "hced-Kinzan1915-1": ("Rashidis", "Saudis"),
    "hced-Medina, Saudi Arabia1925-1": ("Saudis", "Hashemites"),
    "hced-Mulaydah1891-1": ("Rashidis", "Saudis, Qasim"),
    "hced-Rawdhat al Muhanna1906-1": ("Saudis", "Rashidis"),
    "hced-Riyadh1887-1": ("Rashidis", "Saudis"),
    "hced-Riyadh1902-1": ("Saudis", "Rashidis"),
    "hced-Sabalah1929-1": ("Saudis", "Ikhwan Brotherhood"),
    "hced-Taif1924-1": ("Saudis", "Hashemites"),
    "hced-Turabah1919-1": ("Saudis", "Hashemites"),
    "hced-Umm Urdhumah1929-1": ("Saudis", "Ikhwan Rebels"),
    "hced-Unayzah1904-1": ("Saudis", "Ottoman Empire"),
}

_FUNNEL_SCOPE: dict[str, tuple[tuple[str, ...], str | None]] = {
    "hced-Bukairiya1904-1": (("saudis",), "saudis"),
    "hced-Dilam1902-1": (("rashidis", "saudis"), None),
    "hced-Hail1921-1": (("rashidis", "saudis"), None),
    "hced-Hofuf1913-1": (("saudis",), "saudis"),
    "hced-Jirab1915-1": (("rashidis", "saudis"), None),
    "hced-Kinzan1915-1": (("rashidis", "saudis"), None),
    "hced-Medina, Saudi Arabia1925-1": (("hashemites", "saudis"), None),
    "hced-Mulaydah1891-1": (("rashidis", "saudis qasim"), None),
    "hced-Rawdhat al Muhanna1906-1": (("rashidis", "saudis"), None),
    "hced-Riyadh1887-1": (("rashidis", "saudis"), None),
    "hced-Riyadh1902-1": (("rashidis", "saudis"), None),
    "hced-Sabalah1929-1": (("ikhwan brotherhood", "saudis"), None),
    "hced-Taif1924-1": (("hashemites", "saudis"), None),
    "hced-Turabah1919-1": (("hashemites", "saudis"), None),
    "hced-Umm Urdhumah1929-1": (("ikhwan rebels", "saudis"), None),
    "hced-Unayzah1904-1": (("saudis",), "saudis"),
}


WAVE8_SAUDI_RASHIDI_ROW_INVENTORY: dict[str, dict[str, Any]] = {
    candidate_id: {
        "blocker_labels": list(_FUNNEL_SCOPE[candidate_id][0]),
        "greedy_eligible": True,
        "normalized_side_labels": [
            normalize_label(side_1),
            normalize_label(side_2),
        ],
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "raw_side_labels": [side_1, side_2],
        "sole_blocker_label": _FUNNEL_SCOPE[candidate_id][1],
    }
    for candidate_id, (side_1, side_2) in _ROW_LABELS.items()
}


_FUNNEL_LABEL_SIGNATURES = {
    "rashidis": "02c7ad2ff436088c5d5c0ff4106af8f99fbcc4b7b91bd8f6f33886cdb16880a6",
    "saudis": "eaa1ab3a42b774324714a4c7c1edfffd4b2374b3204c66bf25459b09b83f39f0",
    "saudis qasim": "858031ba91aaf34bef903c02ac4ae649d5a1e3b5a57d9411e4f3d09d077940e1",
}


def _label_ownership_audit() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for label in sorted(_OWNED_NORMALIZED_LABELS):
        candidate_ids = sorted(
            candidate_id
            for candidate_id, raw_labels in _ROW_LABELS.items()
            if label in {normalize_label(value) for value in raw_labels}
        )
        result[label] = {
            "candidate_ids": candidate_ids,
            "events_touched": len(candidate_ids),
            "funnel_event_candidate_id_sha256": _FUNNEL_LABEL_SIGNATURES[label],
            "mechanically_necessary_variant": label == "saudis qasim",
            "ownership_rule": (
                "exact normalized side label only; no token or dynasty expansion"
            ),
            "sole_blocker_events": sum(
                _FUNNEL_SCOPE[candidate_id][1] == label
                for candidate_id in candidate_ids
            ),
        }
    return result


WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT = _label_ownership_audit()

WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES: dict[str, dict[str, Any]] = {
    "house of saud": {
        "candidate_ids": sorted(WAVE8_FIRST_SAUDI_RESERVED_IDS),
        "disposition": "owned_by_wave8_first_saudi",
        "reason": (
            "The six House of Saud rows concern the First Saudi State lane; "
            "this lane does not acquire that dynastic spelling."
        ),
    },
    "saudi": {
        "candidate_ids": [],
        "disposition": "not_owned_no_locked_exact_rows",
        "reason": "A singular token is not inferred from the plural exact label.",
    },
    "saudi arabia": {
        "candidate_ids": [
            "hced-Hamad1920-1",
            "hced-Hudayda1934-1",
            "hced-Jahrah1920-1",
        ],
        "disposition": "outside_exact_label_lane",
        "reason": (
            "These rows use the modern-state label and require a separate "
            "identity and duplicate review."
        ),
    },
    "ottoman empire rashidis": {
        "candidate_ids": ["hced-Bukairiya1904-1"],
        "disposition": "opposing_composite_resolved_inside_owned_row_only",
        "reason": (
            "The composite is not a lane alias; Bukayriyah is reserved through "
            "its exact Saudis side and the opposing actors are reviewed there."
        ),
    },
}


def _canonical(
    name: str,
    year: int,
    date_precision: str,
    date_text: str,
    *,
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year}:{year}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year,
        "year_high": year,
    }


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1_entity_ids: Iterable[str],
    side_2_entity_ids: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    war_type: str = "state_formation_conflict",
    source_outcome_override: bool = False,
    confidence: float = 0.86,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1_entity_ids))),
        "side_2_entity_ids": sorted(set(map(str, side_2_entity_ids))),
        "winner_side": 1,
        "result_type": "win",
        "war_type": war_type,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": source_outcome_override,
        "outcome_reversal": False,
        "actor_override": True,
        "confidence": confidence,
        "direct_provenance": {
            "event_boundary": str(canonical_event["date_text"]),
            "reviewed_date": str(canonical_event["date_text"]),
            "reviewed_outcome": (
                "Source-backed side-1 victory; the HCED outcome/actor coding is "
                "explicitly overridden."
                if source_outcome_override
                else "Independent sources support the HCED side-1 victory."
            ),
            "reviewed_sides": (
                "Both raw labels were replaced by source-attested, event-bounded "
                "formations."
            ),
        },
        "audit_note": audit_note,
    }


WAVE8_SAUDI_RASHIDI_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Mulaydah1891-1": _contract(
        "hced-Mulaydah1891-1",
        _canonical("Battle of al-Mulayda", 1891, "year", "1891"),
        "second_saudi_rashidi_climax_1891",
        [_MULAYDA_RASHIDI],
        [_MULAYDA_COALITION],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_bunzel_princeton_2023",
            "wave8_saudi_rashidi_cambridge_al_rasheed_2010",
        ],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_bunzel_princeton_2023",
        ],
        "The reviewed event is Muhammad ibn Abdullah Al Rashid's 1891 victory over Abdul Rahman Al Saud and allied Qassim forces, not a timeless dynasty result.",
    ),
    "hced-Riyadh1902-1": _contract(
        "hced-Riyadh1902-1",
        _canonical("Capture of Riyadh", 1902, "day", "15 January 1902"),
        "riyadh_qassim_reconquest_1902_1906",
        [_RIYADH_SAUDI],
        [_RIYADH_RASHIDI],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_cambridge_al_rasheed_2010",
            "wave8_saudi_rashidi_loc_country_profile_2006",
        ],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_loc_country_profile_2006",
        ],
        "The contract is the small-party assault on Ajlan's Rashidi-held Riyadh position; later state formation is not folded into this tactical result.",
    ),
    "hced-Dilam1902-1": _contract(
        "hced-Dilam1902-1",
        _canonical("Battle of Dilam", 1902, "month", "November 1902"),
        "riyadh_qassim_reconquest_1902_1906",
        [_DILAM_SAUDI],
        [_DILAM_RASHIDI],
        [
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
            "wave8_saudi_rashidi_saudipedia_dilam",
        ],
        [
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
            "wave8_saudi_rashidi_saudipedia_dilam",
        ],
        "The Bangor study describes a limited Ibn Saud victory and Rashidi withdrawal, independently cross-checked by the official Ad-Dilam history.",
    ),
    "hced-Unayzah1904-1": _contract(
        "hced-Unayzah1904-1",
        _canonical(
            "Assault and capture of Unayzah",
            1904,
            "day",
            "22 March 1904",
        ),
        "riyadh_qassim_reconquest_1902_1906",
        [_UNAYZAH_SAUDI],
        [_UNAYZAH_RASHIDI],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
        ],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
        ],
        "HCED's Draw/unnamed-loser coding is rejected: the Rashidi commander was killed, the defending force surrendered or fled, and Ibn Saud entered Unayzah.",
        source_outcome_override=True,
    ),
    "hced-Rawdhat al Muhanna1906-1": _contract(
        "hced-Rawdhat al Muhanna1906-1",
        _canonical(
            "Battle of Rawdat Muhanna",
            1906,
            "month",
            "April 1906",
        ),
        "riyadh_qassim_reconquest_1902_1906",
        [_RAWDAT_SAUDI],
        [_RAWDAT_RASHIDI],
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_saudipedia_rawdat",
        ],
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_saudipedia_rawdat",
        ],
        "Independent accounts support Ibn Saud's victory and the death of Abdulaziz ibn Mutaib Al Rashid in the 1906 fighting.",
    ),
    "hced-Hofuf1913-1": _contract(
        "hced-Hofuf1913-1",
        _canonical(
            "Assault and capture of Hofuf",
            1913,
            "month",
            "May 1913",
        ),
        "hasa_and_wartime_consolidation_1913_1915",
        [_HOFUF_SAUDI],
        [_HOFUF_OTTOMAN],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
        ],
        "The bounded result is the May 1913 wall-scaling assault and Ottoman garrison surrender, not credit for all of al-Hasa's political incorporation.",
        war_type="interstate",
    ),
    "hced-Kinzan1915-1": _contract(
        "hced-Kinzan1915-1",
        _canonical("Battle of Kanzan", 1915, "season", "summer 1915"),
        "hasa_and_wartime_consolidation_1913_1915",
        [_KANZAN_AJMAN],
        [_KANZAN_SAUDI],
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_al_azma_durham_1999",
        ],
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_al_azma_durham_1999",
        ],
        "HCED's Rashidis actor is wrong. Sources identify Dhaydan ibn Hithlayn's al-Ajman as the force that defeated and wounded Ibn Saud and killed his brother Saad at Kanzan.",
        source_outcome_override=True,
    ),
    "hced-Turabah1919-1": _contract(
        "hced-Turabah1919-1",
        _canonical("Battle of Turabah", 1919, "month", "May 1919"),
        "hijaz_expansion_1919_1925",
        [_TURABAH_IKHWAN],
        [_TURABAH_HASHEMITE],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        "The reviewed outcome is the May 1919 destruction of Abdullah's Hashemite army by the Ikhwan-led Turabah force; no later Hijaz conquest is inferred.",
        war_type="interstate",
    ),
    "hced-Medina, Saudi Arabia1925-1": _contract(
        "hced-Medina, Saudi Arabia1925-1",
        _canonical(
            "Siege and surrender of Medina",
            1925,
            "year",
            "1925; surrender on 5 December",
            granularity="siege",
        ),
        "hijaz_expansion_1919_1925",
        [_MEDINA_SAUDI],
        [_MEDINA_HASHEMITE],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        "A roughly ten-month siege ending in the garrison's 5 December surrender supplies a competitive siege outcome; peaceful city-entry alone is not rated.",
        war_type="interstate",
    ),
    "hced-Sabalah1929-1": _contract(
        "hced-Sabalah1929-1",
        _canonical("Battle of Sabilla", 1929, "month", "March 1929"),
        "ikhwan_rebellion_1929",
        [_SABILLA_LOYALIST],
        [_SABILLA_REBEL],
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        "The contract is Ibn Saud's loyalist army defeating the rebel Ikhwan at Sabilla; neither side is replaced by a state or religious generic.",
    ),
    "hced-Umm Urdhumah1929-1": _contract(
        "hced-Umm Urdhumah1929-1",
        _canonical(
            "Battle of Umm Radhmah",
            1929,
            "month",
            "September 1929",
        ),
        "ikhwan_rebellion_1929",
        [_UMM_RADHMAH_LOYALIST],
        [_UMM_RADHMAH_REBEL],
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        [
            "wave8_saudi_rashidi_al_azma_durham_1999",
            "wave8_saudi_rashidi_rundell_bloomsbury_2020",
        ],
        "The rated result is the loyal Shammar defense of the wells against Azaiyiz al-Dawish's Mutair Ikhwan, not a generic Saudi-versus-Ikhwan result.",
    ),
}


def _nonpromotion(
    candidate_id: str,
    disposition: str,
    category: str,
    canonical_event: dict[str, Any],
    reason: str,
    evidence_refs: Iterable[str],
    *,
    reviewed_actors: Iterable[str],
    reviewed_event: str,
    reviewed_date: str,
    reviewed_outcome: str,
) -> dict[str, Any]:
    terminal = disposition == "terminal_exclusion"
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "disposition": disposition,
        "hold_category": category,
        "hold_reason": reason,
        "evidence_refs": sorted(set(map(str, evidence_refs))),
        "full_row_audited": True,
        "terminal_exclusion": terminal,
        "historical_event": {
            "reviewed_actors": sorted(set(map(str, reviewed_actors))),
            "reviewed_date": reviewed_date,
            "reviewed_event": reviewed_event,
            "reviewed_outcome": reviewed_outcome,
        },
    }


WAVE8_SAUDI_RASHIDI_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Riyadh1887-1": _nonpromotion(
        "hced-Riyadh1887-1",
        "hold",
        "discrete_engagement_not_independently_located",
        _canonical(
            "Riyadh transition asserted for 1887",
            1887,
            "year",
            "1887 assertion; exact engagement unlocated",
            granularity="unresolved_transition",
        ),
        "Reviewed histories describe the broader late-1880s collapse of Saudi control but do not independently locate one binary Rashidi victory at Riyadh in 1887. The exact event and tactical outcome remain unknown; unknown is never converted to a draw.",
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_bunzel_princeton_2023",
            "wave8_saudi_rashidi_cambridge_al_rasheed_2010",
        ],
        reviewed_actors=[
            "late Second Saudi State forces associated with Riyadh",
            "Rashidi expansion forces",
        ],
        reviewed_event="Late-1880s transfer of power around Riyadh",
        reviewed_date="broader transition in the late 1880s; no exact 1887 battle located",
        reviewed_outcome="Rashidi ascendancy is known, but a single 1887 tactical result is not",
    ),
    "hced-Bukairiya1904-1": _nonpromotion(
        "hced-Bukairiya1904-1",
        "hold",
        "campaign_phase_and_outcome_conflict",
        _canonical(
            "Bukayriyah campaign phases",
            1904,
            "year",
            "1904; initial and renewed phases unresolved",
            granularity="multi_phase_campaign",
        ),
        "Sources distinguish an initial Saudi setback from renewed fighting and a later Saudi success, while some accounts attach victory differently across Bukayriyah and the following campaign phase. The locked row does not identify which phase it rates, so its exact outcome remains unknown and is never converted to a draw.",
        [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_gungordu_aybu_2015",
        ],
        reviewed_actors=[
            "Ibn Saud's Qassim campaign force",
            "Rashidi and Ottoman forces in successive Bukayriyah phases",
        ],
        reviewed_event="Successive actions around Bukayriyah in the 1904 Qassim campaign",
        reviewed_date="1904; exact initial-versus-renewed phase binding unresolved",
        reviewed_outcome="Sources support different outcomes for successive phases; the row's phase is not fixed",
    ),
    "hced-Jirab1915-1": _nonpromotion(
        "hced-Jirab1915-1",
        "hold",
        "direct_source_outcome_conflict",
        _canonical(
            "Battle of Jarrab",
            1915,
            "day",
            "24 January 1915",
        ),
        "The British Library eyewitness account describes Ibn Saud's complete rout and later official reporting calls the day disastrous, while the contemporary Britannica supplement calls the battle indecisive. This direct outcome conflict is held as unknown and is never converted to a draw.",
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_qdl_jarrab_1915",
        ],
        reviewed_actors=[
            "Ibn Saud's force at Jarrab",
            "Ibn Rashid's Bani Shammar force at Jarrab",
        ],
        reviewed_event="Battle of Jarrab and death of Captain William Shakespear",
        reviewed_date="24 January 1915",
        reviewed_outcome="Rashidi rout in eyewitness and official accounts versus a contemporary indecisive characterization",
    ),
    "hced-Taif1924-1": _nonpromotion(
        "hced-Taif1924-1",
        "hold",
        "approach_battle_and_city_capture_boundary_conflict",
        _canonical(
            "Taif and al-Hawiyah operations",
            1924,
            "month",
            "September 1924",
            granularity="approach_battle_and_city_capture",
        ),
        "One reviewed account locates the Hashemite defeat at nearby al-Hawiyah before the force entered Taif, while the contemporary Britannica account says Taif itself was captured without opposition. The row does not fix approach battle versus city entry, so no tactical winner is emitted; unknown is never converted to a draw.",
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        reviewed_actors=[
            "Ikhwan advance force toward Taif",
            "Hashemite force at al-Hawiyah or Taif",
        ],
        reviewed_event="Defeat near al-Hawiyah followed by entry into Taif",
        reviewed_date="September 1924",
        reviewed_outcome="A Hashemite defeat is reported outside the city, but no opposed capture at Taif is secure",
    ),
}


WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Hail1921-1": _nonpromotion(
        "hced-Hail1921-1",
        "terminal_exclusion",
        "surrender_without_fighting_after_blockade",
        _canonical(
            "Surrender of Hail",
            1921,
            "year",
            "1921 surrender after economic and military pressure",
            granularity="noncombat_surrender_after_blockade",
        ),
        "Independent accounts state that Hail surrendered without a fight and emphasize blockade or economic pressure rather than a competitive battle. That is affirmative proof of a non-ratable transfer, so this row is excluded rather than assigned an invented outcome.",
        [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_britannica_1926",
            "wave8_saudi_rashidi_loc_country_study_1992",
        ],
        reviewed_actors=[
            "Ibn Saud's encircling forces at Hail",
            "Hail authorities and remaining Rashidi defenders",
        ],
        reviewed_event="Surrender and transfer of Hail after blockade pressure",
        reviewed_date="1921",
        reviewed_outcome="Surrender without fighting; no competitive engagement outcome exists",
    ),
}

WAVE8_SAUDI_RASHIDI_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_SAUDI_RASHIDI_HOLDS,
    **WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS,
}

WAVE8_SAUDI_RASHIDI_CONTRACT_IDS = frozenset(WAVE8_SAUDI_RASHIDI_CONTRACTS)
WAVE8_SAUDI_RASHIDI_HOLD_IDS = frozenset(WAVE8_SAUDI_RASHIDI_HOLDS)
WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS
)
WAVE8_SAUDI_RASHIDI_RESERVED_IDS = (
    WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
    | WAVE8_SAUDI_RASHIDI_HOLD_IDS
    | WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS
)
WAVE8_SAUDI_RASHIDI_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {
    "hced-Kinzan1915-1": {
        "raw_side_1_label": "Rashidis",
        "raw_winner_label": "Rashidis",
        "reviewed_result": "side_1_win",
        "reviewed_side_1_entity_ids": [_KANZAN_AJMAN],
        "override_type": "winner_actor_correction",
        "reason": (
            "The winning orientation is retained, but the documented victor was "
            "al-Ajman, not a Rashidi formation."
        ),
        "source_ids": [
            "wave8_saudi_rashidi_abedin_kcl_2002",
            "wave8_saudi_rashidi_al_azma_durham_1999",
        ],
    },
    "hced-Unayzah1904-1": {
        "raw_loser_label": None,
        "raw_winner_label": "Draw",
        "reviewed_result": "side_1_win",
        "reviewed_side_1_entity_ids": [_UNAYZAH_SAUDI],
        "reviewed_side_2_entity_ids": [_UNAYZAH_RASHIDI],
        "override_type": "draw_to_source_backed_win",
        "reason": (
            "The Rashidi commander was killed, the defending force surrendered "
            "or fled, and Ibn Saud's force entered Unayzah."
        ),
        "source_ids": [
            "wave8_saudi_rashidi_almutairi_uea_2019",
            "wave8_saudi_rashidi_alotaibi_bangor_2017",
        ],
    },
}


WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
)
WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS: frozenset[str] = frozenset()
WAVE8_SAUDI_RASHIDI_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS,
}

_RAW_POINTS: dict[str, tuple[str, str]] = {
    "hced-Dilam1902-1": ("23.976619", "47.1557087"),
    "hced-Hofuf1913-1": ("25.380026", "49.5887652"),
    "hced-Kinzan1915-1": ("25.3057092", "49.5432732"),
    "hced-Medina, Saudi Arabia1925-1": ("24.4710078", "39.4774711"),
    "hced-Mulaydah1891-1": ("26.3479206", "43.7833397"),
    "hced-Rawdhat al Muhanna1906-1": ("26.991823", "43.9096303"),
    "hced-Riyadh1902-1": ("24.7135517", "46.6752957"),
    "hced-Sabalah1929-1": ("21.4799872", "39.2513326"),
    "hced-Turabah1919-1": ("21.2075957", "41.62114"),
    "hced-Umm Urdhumah1929-1": ("28.2138277", "41.7282723"),
    "hced-Unayzah1904-1": ("26.0833976", "43.9627492"),
}

WAVE8_SAUDI_RASHIDI_LOCATION_REVIEW: dict[str, dict[str, Any]] = {
    candidate_id: {
        "country_disposition": "retain_modern_country_saudi_arabia",
        "point_disposition": "quarantine_unproven_source_point",
        "raw_latitude": latitude,
        "raw_longitude": longitude,
        "reason": (
            "The staged coordinates are geocoder assertions without "
            "claim-level historical-site provenance; country-level placement is "
            "unambiguous, but the point is not released."
        ),
    }
    for candidate_id, (latitude, longitude) in _RAW_POINTS.items()
}


WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT: dict[str, Any] = {
    "imported_lane": "wave8_first_saudi",
    "imported_reserved_candidate_ids": sorted(WAVE8_FIRST_SAUDI_RESERVED_IDS),
    "target_overlap": sorted(
        WAVE8_SAUDI_RASHIDI_RESERVED_IDS & WAVE8_FIRST_SAUDI_RESERVED_IDS
    ),
    "disposition": "separate_exact_label_ownership",
    "reason": (
        "First Saudi owns six House of Saud rows ending in 1818; this lane owns "
        "only the 1887-1929 Saudis/Rashidis exact-label inventory."
    ),
}

WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT: dict[str, dict[str, Any]] = {
    "hced_wave8_first_saudi_hced_diriyah1818_1": {
        "candidate_id": "hced-Diriyah1818-1",
        "name": "Siege of Diriyah",
        "owner": "wave8_first_saudi",
        "reviewed_target_entity_id": "first_saudi_state",
        "year": 1818,
    },
    "iwd_war_48_saudi_arabia_yemen_1934": {
        "candidate_id": None,
        "name": "Saudi Arabia-Yemen 1934",
        "owner": "existing_iwd_parent_war",
        "reviewed_target_entity_id": "kingdom_saudi_arabia",
        "year": 1934,
    },
    "iwd_war_70_yom_kippur_1973": {
        "candidate_id": None,
        "name": "Yom Kippur 1973",
        "owner": "existing_iwd_parent_war",
        "reviewed_target_entity_id": "kingdom_saudi_arabia",
        "year": 1973,
    },
    "iwd_war_82_gulf_war_1991": {
        "candidate_id": None,
        "name": "Gulf War 1991",
        "owner": "existing_iwd_parent_war",
        "reviewed_target_entity_id": "kingdom_saudi_arabia",
        "year": 1991,
    },
}


WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "medina_1812_1925": {
        "candidate_ids": [
            "hced-Medina1812-1",
            "hced-Medina, Saudi Arabia1925-1",
        ],
        "disposition": "distinct_states_centuries_and_conflicts",
        "reason": "The First Saudi 1812 row and the Hashemite siege ending in 1925 are not twins.",
    },
    "qassim_campaign_1904": {
        "candidate_ids": ["hced-Bukairiya1904-1", "hced-Unayzah1904-1"],
        "disposition": "distinct_engagements_same_campaign",
        "reason": "Unayzah's March capture is distinct from the unresolved multi-phase Bukayriyah fighting.",
    },
    "riyadh_1887_1902": {
        "candidate_ids": ["hced-Riyadh1887-1", "hced-Riyadh1902-1"],
        "disposition": "same_place_distinct_events",
        "reason": "The unresolved 1887 transition and the documented January 1902 assault are fifteen years apart.",
    },
    "taif_1916_1924": {
        "candidate_ids": ["hced-Taif1916-1", "hced-Taif1924-1"],
        "disposition": "distinct_wars_and_forces",
        "reason": "The 1916 Arab Revolt capture from the Ottomans is distinct from the 1924 Saudi-Hashemite operations.",
    },
}


def _aliases(*values: str) -> tuple[str, ...]:
    return tuple(sorted({normalize_label(value) for value in values}))


WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Bukairiya1904-1": {
        "year": 1904,
        "aliases": _aliases(
            "al-Bukayriyah",
            "Battle of Bukayriyah",
            "Bukairiya",
            "Bukayriyah",
        ),
    },
    "hced-Dilam1902-1": {
        "year": 1902,
        "aliases": _aliases("Battle of Dilam", "Dilam"),
    },
    "hced-Hail1921-1": {
        "year": 1921,
        "aliases": _aliases("Fall of Hail", "Hail", "Siege of Hail"),
    },
    "hced-Hofuf1913-1": {
        "year": 1913,
        "aliases": _aliases(
            "Assault and capture of Hofuf",
            "Capture of Hofuf",
            "Hofuf",
        ),
    },
    "hced-Jirab1915-1": {
        "year": 1915,
        "aliases": _aliases("Battle of Jarrab", "Jarrab", "Jirab"),
    },
    "hced-Kinzan1915-1": {
        "year": 1915,
        "aliases": _aliases("Battle of Kanzan", "Kanzan", "Kinzan"),
    },
    "hced-Medina, Saudi Arabia1925-1": {
        "year": 1925,
        "aliases": _aliases(
            "Medina",
            "Medina, Saudi Arabia",
            "Siege and surrender of Medina",
            "Siege of Medina",
        ),
    },
    "hced-Mulaydah1891-1": {
        "year": 1891,
        "aliases": _aliases(
            "al-Mulayda",
            "Battle of al-Mulayda",
            "Mulayda",
            "Mulaydah",
        ),
    },
    "hced-Rawdhat al Muhanna1906-1": {
        "year": 1906,
        "aliases": _aliases(
            "Battle of Rawdat Muhanna",
            "Rawdat al Muhanna",
            "Rawdat Muhanna",
            "Rawdhat al Muhanna",
        ),
    },
    "hced-Riyadh1887-1": {
        "year": 1887,
        "aliases": _aliases("Riyadh", "Riyadh transition"),
    },
    "hced-Riyadh1902-1": {
        "year": 1902,
        "aliases": _aliases("Capture of Riyadh", "Riyadh"),
    },
    "hced-Sabalah1929-1": {
        "year": 1929,
        "aliases": _aliases(
            "Battle of Sabilla",
            "Sabalah",
            "Sabilla",
            "Sablah",
        ),
    },
    "hced-Taif1924-1": {
        "year": 1924,
        "aliases": _aliases(
            "Battle of Taif",
            "Capture of Taif",
            "Taif",
            "Taif and al-Hawiyah operations",
        ),
    },
    "hced-Turabah1919-1": {
        "year": 1919,
        "aliases": _aliases(
            "Battle of Turabah",
            "Battle of Turubah",
            "Turabah",
            "Turubah",
        ),
    },
    "hced-Umm Urdhumah1929-1": {
        "year": 1929,
        "aliases": _aliases(
            "Battle of Umm Radhmah",
            "Battle of Umm Urdhumah",
            "Umm Radhma",
            "Umm Radhmah",
            "Umm Radmah",
            "Umm Urdhumah",
        ),
    },
    "hced-Unayzah1904-1": {
        "year": 1904,
        "aliases": _aliases(
            "Assault and capture of Unayzah",
            "Unaizah",
            "Unayzah",
        ),
    },
}

WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}

WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT: dict[str, dict[str, Any]] = {
    "iwbd-125-48-872": {
        "raw_row_sha256": "a2a2c654330cadc5e469c31d2875487cef692b36a4220fcef6b94507465eb5e2",
        "name": "Hudayda",
        "year": 1934,
        "attacker_raw": "Yemen",
        "defender_raw": "Saudi Arabia",
        "winner_raw": "Saudi Arabia",
        "related_hced_candidate_id": "hced-Hudayda1934-1",
        "disposition": "outside_exact_label_lane",
        "reason": (
            "The only Saudi-related IWBD row is a 1934 Saudi Arabia/Yemen row. "
            "It is a probable twin of an HCED Saudi Arabia row, not any exact "
            "Saudis/Rashidis event owned here."
        ),
    },
}


def _integration_dispositions() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for candidate_id, (labels, sole) in _FUNNEL_SCOPE.items():
        if candidate_id in WAVE8_SAUDI_RASHIDI_CONTRACTS:
            disposition = "PROMOTE"
            actors_resolved = True
        elif candidate_id in WAVE8_SAUDI_RASHIDI_HOLDS:
            disposition = "HOLD"
            actors_resolved = False
        else:
            disposition = "EXCLUDE"
            actors_resolved = False
        result[candidate_id] = {
            "all_opposing_actors_resolved": actors_resolved,
            "blocker_labels": list(labels),
            "cross_label_duplicate_scan": "reviewed_no_rating_collision",
            "disposition": disposition,
            "full_row_audited": True,
            "greedy_eligible": True,
            "iwbd_duplicate_scan": "reviewed_no_exact_or_probable_twin",
            "other_blockers": [],
            "release_duplicate_scan": "reviewed_no_existing_release_twin",
            "sole_blocker_label": sole,
        }
    return result


WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS = _integration_dispositions()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_SAUDI_RASHIDI_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_label_boundaries": WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES,
        "entities": WAVE8_SAUDI_RASHIDI_ENTITIES,
        "first_saudi_ownership_audit": (
            WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT
        ),
        "hced_twin_dispositions": WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS,
        "holds": WAVE8_SAUDI_RASHIDI_HOLDS,
        "integration_dispositions": (
            WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": (
            WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_outside_lane_audit": WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT,
        "iwbd_zero_overlap_audit": (
            WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "label_ownership_audit": WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT,
        "location_review": WAVE8_SAUDI_RASHIDI_LOCATION_REVIEW,
        "outcome_overrides": WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS
        ),
        "release_ownership_audit": WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT,
        "row_inventory": WAVE8_SAUDI_RASHIDI_ROW_INVENTORY,
        "sources": WAVE8_SAUDI_RASHIDI_SOURCES,
        "terminal_exclusions": WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS,
    }


def wave8_saudi_rashidi_audit_signature() -> str:
    """Return the SHA-256 pin over every disposition and integration audit."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _canonical_row_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(dict(row)).encode("utf-8")).hexdigest()


def _validate_static() -> None:
    if (
        len(WAVE8_SAUDI_RASHIDI_CONTRACTS),
        len(WAVE8_SAUDI_RASHIDI_HOLDS),
        len(WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS),
    ) != (11, 4, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (
        len(WAVE8_SAUDI_RASHIDI_ENTITIES),
        len(WAVE8_SAUDI_RASHIDI_SOURCES),
    ) != (22, 14):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if (
        WAVE8_SAUDI_RASHIDI_RESERVED_IDS
        != WAVE8_SAUDI_RASHIDI_EXPECTED_CANDIDATE_IDS
    ):
        raise ValueError(f"{_LANE_NAME} reservation inventory is incomplete")
    dispositions = (
        WAVE8_SAUDI_RASHIDI_CONTRACT_IDS,
        WAVE8_SAUDI_RASHIDI_HOLD_IDS,
        WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        dispositions[left] & dispositions[right]
        for left in range(3)
        for right in range(left + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if WAVE8_SAUDI_RASHIDI_RESERVED_IDS & WAVE8_FIRST_SAUDI_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} overlaps Wave 8 First Saudi ownership")
    if (
        wave8_saudi_rashidi_audit_signature()
        != WAVE8_SAUDI_RASHIDI_FINAL_AUDIT_SIGNATURE
    ):
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if len(_SOURCE_BY_ID) != 14:
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    for source in WAVE8_SAUDI_RASHIDI_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source URL is not HTTPS")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {
        str(entity["id"]): entity for entity in WAVE8_SAUDI_RASHIDI_ENTITIES
    }
    if len(entity_by_id) != 22:
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_generic = {
        "house of saud",
        "rashidi",
        "rashidis",
        "saudi",
        "saudi arabia",
        "saudis",
        "saudis qasim",
    }
    used_sources: set[str] = set()
    for entity in WAVE8_SAUDI_RASHIDI_ENTITIES:
        if entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} entity opens a generic alias")
        if int(entity["start_year"]) != int(entity["end_year"]):
            raise ValueError(f"{_LANE_NAME} entity is not event bounded")
        if not str(entity["kind"]).startswith("event_bounded_"):
            raise ValueError(f"{_LANE_NAME} entity kind is not event bounded")
        if "no rating is inherited" not in str(entity["continuity_note"]).casefold():
            raise ValueError(f"{_LANE_NAME} entity lacks a continuity firewall")
        if normalize_label(entity["name"]) in forbidden_generic:
            raise ValueError(f"{_LANE_NAME} installs a generic identity")
        if normalize_label(entity["id"]) in forbidden_generic:
            raise ValueError(f"{_LANE_NAME} installs a generic identity ID")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} entity sources are not canonical")
        if not set(map(str, entity["source_ids"])) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} entity names an unknown source")
        used_sources.update(map(str, entity["source_ids"]))

    used_entities: set[str] = set()
    override_ids: set[str] = set()
    for candidate_id, contract in WAVE8_SAUDI_RASHIDI_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} promotion hash drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key:
            raise ValueError(f"{_LANE_NAME} canonical event key drifted")
        if int(canonical["year_low"]) != int(canonical["year_high"]):
            raise ValueError(f"{_LANE_NAME} canonical event is not time bounded")
        if not canonical["date_text"] or not canonical["date_precision"]:
            raise ValueError(f"{_LANE_NAME} canonical date provenance is empty")
        side_1 = list(map(str, contract["side_1_entity_ids"]))
        side_2 = list(map(str, contract["side_2_entity_ids"]))
        if not _is_sorted_unique(side_1) or not _is_sorted_unique(side_2):
            raise ValueError(f"{_LANE_NAME} contract sides are not canonical")
        if not side_1 or not side_2 or set(side_1) & set(side_2):
            raise ValueError(f"{_LANE_NAME} contract has invalid opposing sides")
        if not (set(side_1) | set(side_2)) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} contract uses an unknown identity")
        used_entities.update(set(side_1) | set(side_2))
        for entity_id in set(side_1) | set(side_2):
            entity = entity_by_id[entity_id]
            year = int(canonical["year_low"])
            if not int(entity["start_year"]) <= year <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} contract exceeds an entity window")

        if contract["result_type"] != "win" or int(contract["winner_side"]) != 1:
            raise ValueError(f"{_LANE_NAME} invented a draw or unknown outcome")
        if contract["outcome_reversal"] is not False:
            raise ValueError(f"{_LANE_NAME} reverses an HCED outcome")
        if contract["actor_override"] is not True:
            raise ValueError(f"{_LANE_NAME} actor resolution is not explicit")
        if contract["source_outcome_override"]:
            override_ids.add(candidate_id)

        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} contract evidence is not canonical")
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} contract lacks independent outcomes")
        if any(
            "outcome" not in _SOURCE_BY_ID[source_id]["evidence_roles"]
            for source_id in outcomes
        ):
            raise ValueError(f"{_LANE_NAME} outcome source lacks outcome role")
        expected_families = sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome families are not independent")
        if set(contract["direct_provenance"]) != {
            "event_boundary",
            "reviewed_date",
            "reviewed_outcome",
            "reviewed_sides",
        } or not all(contract["direct_provenance"].values()):
            raise ValueError(f"{_LANE_NAME} direct provenance is incomplete")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} bounded entities are not exactly consumed")
    if override_ids != set(WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES):
        raise ValueError(f"{_LANE_NAME} outcome override inventory changed")
    if override_ids != {"hced-Kinzan1915-1", "hced-Unayzah1904-1"}:
        raise ValueError(f"{_LANE_NAME} unexpected outcome override")

    forbidden_result_keys = {
        "losers",
        "outcome_source_family_ids",
        "outcome_source_ids",
        "result_type",
        "side_1_entity_ids",
        "side_2_entity_ids",
        "winner_side",
        "winners",
    }
    for candidate_id, item in WAVE8_SAUDI_RASHIDI_NONPROMOTIONS.items():
        if item["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} nonpromotion hash drifted")
        if item["full_row_audited"] is not True:
            raise ValueError(f"{_LANE_NAME} reserves an unaudited row")
        if forbidden_result_keys & set(item):
            raise ValueError(f"{_LANE_NAME} nonpromotion contains a result")
        evidence = list(map(str, item["evidence_refs"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} nonpromotion evidence drifted")
        used_sources.update(evidence)
    for hold in WAVE8_SAUDI_RASHIDI_HOLDS.values():
        if hold["disposition"] != "hold" or hold["terminal_exclusion"] is not False:
            raise ValueError(f"{_LANE_NAME} hold disposition drifted")
        reason = str(hold["hold_reason"]).casefold()
        if "unknown" not in reason or "never converted to a draw" not in reason:
            raise ValueError(f"{_LANE_NAME} hold could invent a draw")
    if set(WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS) != {"hced-Hail1921-1"}:
        raise ValueError(f"{_LANE_NAME} exclusion inventory changed")
    hail = WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS["hced-Hail1921-1"]
    if (
        hail["disposition"] != "terminal_exclusion"
        or hail["terminal_exclusion"] is not True
        or "without a fight" not in str(hail["hold_reason"]).casefold()
    ):
        raise ValueError(f"{_LANE_NAME} Hail exclusion lacks proof")

    if used_sources != set(_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if set(WAVE8_SAUDI_RASHIDI_ROW_INVENTORY) != set(_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} row inventory changed")
    for candidate_id, item in WAVE8_SAUDI_RASHIDI_ROW_INVENTORY.items():
        if item["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} row fingerprint inventory drifted")
        if item["raw_side_labels"] != list(_ROW_LABELS[candidate_id]):
            raise ValueError(f"{_LANE_NAME} raw labels drifted")
        if item["blocker_labels"] != list(_FUNNEL_SCOPE[candidate_id][0]):
            raise ValueError(f"{_LANE_NAME} blocker labels drifted")
        if item["greedy_eligible"] is not True:
            raise ValueError(f"{_LANE_NAME} greedy eligibility drifted")
    expected_label_counts = {"rashidis": 8, "saudis": 15, "saudis qasim": 1}
    if {
        label: len(item["candidate_ids"])
        for label, item in WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT.items()
    } != expected_label_counts:
        raise ValueError(f"{_LANE_NAME} exact-label counts changed")
    if set(WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT) != set(
        _OWNED_NORMALIZED_LABELS
    ):
        raise ValueError(f"{_LANE_NAME} label ownership expanded")
    if (
        WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT["saudis qasim"][
            "candidate_ids"
        ]
        != ["hced-Mulaydah1891-1"]
    ):
        raise ValueError(f"{_LANE_NAME} spelling-variant ownership expanded")

    if set(WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS) != set(_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} integration inventory changed")
    for candidate_id, item in WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS.items():
        expected = (
            "PROMOTE"
            if candidate_id in WAVE8_SAUDI_RASHIDI_CONTRACTS
            else "HOLD"
            if candidate_id in WAVE8_SAUDI_RASHIDI_HOLDS
            else "EXCLUDE"
        )
        if item["disposition"] != expected or item["full_row_audited"] is not True:
            raise ValueError(f"{_LANE_NAME} integration disposition drifted")
        if expected == "PROMOTE" and item["all_opposing_actors_resolved"] is not True:
            raise ValueError(f"{_LANE_NAME} promotes an unresolved opposing side")

    if (
        WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS
        != WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
    ):
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} country quarantine inventory changed")
    if set(WAVE8_SAUDI_RASHIDI_LOCATION_REVIEW) != set(
        WAVE8_SAUDI_RASHIDI_CONTRACTS
    ):
        raise ValueError(f"{_LANE_NAME} location review is incomplete")

    if WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} IWBD duplicate inventory changed")
    if set(WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT) != set(_ROW_HASHES):
        raise ValueError(f"{_LANE_NAME} IWBD zero-overlap audit is incomplete")
    for audit in WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT.values():
        aliases = list(map(str, audit["aliases"]))
        if not _is_sorted_unique(aliases) or any(
            alias != normalize_label(alias) for alias in aliases
        ):
            raise ValueError(f"{_LANE_NAME} duplicate aliases are not canonical")
    if set(WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT) != {
        "iwbd-125-48-872"
    }:
        raise ValueError(f"{_LANE_NAME} outside-lane IWBD audit changed")

    first_audit = WAVE8_SAUDI_RASHIDI_FIRST_SAUDI_OWNERSHIP_AUDIT
    if first_audit["imported_reserved_candidate_ids"] != sorted(
        WAVE8_FIRST_SAUDI_RESERVED_IDS
    ) or first_audit["target_overlap"]:
        raise ValueError(f"{_LANE_NAME} First Saudi overlap audit changed")
    if set(WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT) != {
        "hced_wave8_first_saudi_hced_diriyah1818_1",
        "iwd_war_48_saudi_arabia_yemen_1934",
        "iwd_war_70_yom_kippur_1973",
        "iwd_war_82_gulf_war_1991",
    }:
        raise ValueError(f"{_LANE_NAME} release ownership audit changed")


def _row_year(row: Mapping[str, Any]) -> int | None:
    for field in ("year", "year_best", "year_low"):
        value = row.get(field)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    for field in ("start_date", "end_date"):
        value = str(row.get(field) or "")
        if len(value) >= 4 and value[:4].isdigit():
            return int(value[:4])
    return None


_DUPLICATE_MATCH_KEYS = {
    (int(audit["year"]), str(alias))
    for audit in WAVE8_SAUDI_RASHIDI_IWBD_ZERO_OVERLAP_AUDIT.values()
    for alias in audit["aliases"]
}


def validate_wave8_saudi_rashidi_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate the 16-row exact-label inventory and every raw fingerprint."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_SAUDI_RASHIDI_CONTRACTS,
        WAVE8_SAUDI_RASHIDI_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    exact_ids = {
        str(row.get("candidate_id"))
        for row in hced_rows
        if {
            normalize_label(row.get("side_1_raw")),
            normalize_label(row.get("side_2_raw")),
        }
        & _OWNED_NORMALIZED_LABELS
    }
    if exact_ids != WAVE8_SAUDI_RASHIDI_EXPECTED_CANDIDATE_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact-label inventory changed: {sorted(exact_ids)}"
        )
    for label, audit in WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT.items():
        actual = sorted(
            str(row.get("candidate_id"))
            for row in hced_rows
            if label
            in {
                normalize_label(row.get("side_1_raw")),
                normalize_label(row.get("side_2_raw")),
            }
        )
        if actual != audit["candidate_ids"]:
            raise ValueError(f"{_LANE_NAME} ownership changed for exact label {label}")
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_SAUDI_RASHIDI_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_saudi_rashidi_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Fail closed on HCED/IWBD/release twins and partial release ownership."""

    validate_wave8_saudi_rashidi_queue_contracts(hced_rows)
    existing = list(existing_events)

    iwbd_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in iwbd_rows:
        iwbd_by_id.setdefault(str(row.get("candidate_id")), []).append(row)
    for candidate_id, audit in WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT.items():
        rows = iwbd_by_id.get(candidate_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one audited outside-lane IWBD row "
                f"{candidate_id}, found {len(rows)}"
            )
        if _canonical_row_sha256(rows[0]) != audit["raw_row_sha256"]:
            raise ValueError(f"{_LANE_NAME} outside-lane IWBD fingerprint changed")

    hced_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in hced_rows
        if str(row.get("candidate_id"))
        not in WAVE8_SAUDI_RASHIDI_EXPECTED_CANDIDATE_IDS
        and (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if hced_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed cross-label HCED twin(s): {hced_matches}")

    iwbd_matches = sorted(
        str(row.get("candidate_id") or "<missing-id>")
        for row in iwbd_rows
        if (_row_year(row), normalize_label(row.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if iwbd_matches:
        raise ValueError(f"{_LANE_NAME} unreviewed probable IWBD twin(s): {iwbd_matches}")

    held_or_excluded_release_ids = sorted(
        str(event.get("hced_candidate_id"))
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_SAUDI_RASHIDI_NONPROMOTIONS
    )
    if held_or_excluded_release_ids:
        raise ValueError(
            f"{_LANE_NAME} held/excluded candidate was rated: "
            f"{held_or_excluded_release_ids}"
        )

    released_target_events = [
        event
        for event in existing
        if event.get("hced_candidate_id") in WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
    ]
    released_target_ids = {
        str(event.get("hced_candidate_id")) for event in released_target_events
    }
    if released_target_ids and released_target_ids != WAVE8_SAUDI_RASHIDI_CONTRACT_IDS:
        raise ValueError(
            f"{_LANE_NAME} partial candidate release: {sorted(released_target_ids)}"
        )
    if released_target_events and len(released_target_events) != len(
        WAVE8_SAUDI_RASHIDI_CONTRACTS
    ):
        raise ValueError(f"{_LANE_NAME} duplicate candidate release")
    for event in released_target_events:
        candidate_id = str(event["hced_candidate_id"])
        expected_event_id = f"{_EVENT_ID_PREFIX}{_slug(candidate_id, 80)}"
        if str(event.get("id")) != expected_event_id:
            raise ValueError(f"{_LANE_NAME} candidate release owner ID changed")

    release_matches = sorted(
        str(event.get("id") or "<missing-id>")
        for event in existing
        if event.get("hced_candidate_id")
        not in WAVE8_SAUDI_RASHIDI_CONTRACT_IDS
        and (_row_year(event), normalize_label(event.get("name")))
        in _DUPLICATE_MATCH_KEYS
    )
    if release_matches:
        raise ValueError(
            f"{_LANE_NAME} unreviewed probable release twin(s): {release_matches}"
        )

    existing_by_id: dict[str, list[Mapping[str, Any]]] = {}
    for event in existing:
        existing_by_id.setdefault(str(event.get("id")), []).append(event)
    for event_id, audit in WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT.items():
        rows = existing_by_id.get(event_id, [])
        if len(rows) != 1:
            raise ValueError(
                f"{_LANE_NAME} expected one audited release owner {event_id}, "
                f"found {len(rows)}"
            )
        event = rows[0]
        entity_ids = {
            str(participant.get("entity_id"))
            for participant in event.get("participants", [])
        }
        if (
            str(event.get("name")) != audit["name"]
            or _row_year(event) != audit["year"]
            or event.get("hced_candidate_id") != audit["candidate_id"]
            or audit["reviewed_target_entity_id"] not in entity_ids
        ):
            raise ValueError(f"{_LANE_NAME} audited release ownership changed")

    audited_release_entity_ids = {"first_saudi_state", "kingdom_saudi_arabia"}
    actual_owner_event_ids = {
        str(event.get("id"))
        for event in existing
        if {
            str(participant.get("entity_id"))
            for participant in event.get("participants", [])
        }
        & audited_release_entity_ids
    }
    if actual_owner_event_ids != set(WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT):
        raise ValueError(f"{_LANE_NAME} already-rated Saudi ownership changed")

    return {
        "cross_label_boundaries": len(
            WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES
        ),
        "first_saudi_candidate_overlap": 0,
        "hced_twin_dispositions": len(
            WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS
        ),
        "integration_dispositions": len(
            WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_outside_lane_rows": len(
            WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT
        ),
        "iwbd_probable_twins": 0,
        "release_ownership_rows": len(
            WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT
        ),
        "release_probable_twins": 0,
        "released_target_candidates": len(released_target_ids),
    }


def install_wave8_saudi_rashidi_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_SAUDI_RASHIDI_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_saudi_rashidi_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_SAUDI_RASHIDI_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_saudi_rashidi_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Promote all and only the eleven reviewed exact candidate contracts."""

    validate_wave8_saudi_rashidi_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_SAUDI_RASHIDI_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_saudi_rashidi_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_SAUDI_RASHIDI_CONTRACTS.values()
            ).items()
        )
    )


def wave8_saudi_rashidi_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "cross_label_boundaries": len(
            WAVE8_SAUDI_RASHIDI_CROSS_LABEL_BOUNDARIES
        ),
        "exact_owned_labels": len(WAVE8_SAUDI_RASHIDI_LABEL_OWNERSHIP_AUDIT),
        "first_saudi_candidate_overlap": len(
            WAVE8_SAUDI_RASHIDI_RESERVED_IDS & WAVE8_FIRST_SAUDI_RESERVED_IDS
        ),
        "hced_twin_dispositions": len(
            WAVE8_SAUDI_RASHIDI_HCED_TWIN_DISPOSITIONS
        ),
        "holds": len(WAVE8_SAUDI_RASHIDI_HOLDS),
        "integration_dispositions": len(
            WAVE8_SAUDI_RASHIDI_INTEGRATION_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": len(
            WAVE8_SAUDI_RASHIDI_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_outside_lane_rows": len(
            WAVE8_SAUDI_RASHIDI_IWBD_OUTSIDE_LANE_AUDIT
        ),
        "new_entities": len(WAVE8_SAUDI_RASHIDI_ENTITIES),
        "new_sources": len(WAVE8_SAUDI_RASHIDI_SOURCES),
        "newly_rated_events": len(WAVE8_SAUDI_RASHIDI_CONTRACTS),
        "outcome_overrides": len(WAVE8_SAUDI_RASHIDI_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_SAUDI_RASHIDI_CONTRACTS),
        "release_ownership_rows": len(
            WAVE8_SAUDI_RASHIDI_RELEASE_OWNERSHIP_AUDIT
        ),
        "reviewed_hced_rows": len(WAVE8_SAUDI_RASHIDI_RESERVED_IDS),
        "terminal_exclusions": len(
            WAVE8_SAUDI_RASHIDI_TERMINAL_EXCLUSIONS
        ),
    }


def wave8_saudi_rashidi_location_quarantine_additions() -> dict[
    str, frozenset[str]
]:
    """Return immutable local additions for later coordinated integration."""

    _validate_static()
    return {
        "country": WAVE8_SAUDI_RASHIDI_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_SAUDI_RASHIDI_POINT_QUARANTINE_ADDITIONS,
    }
