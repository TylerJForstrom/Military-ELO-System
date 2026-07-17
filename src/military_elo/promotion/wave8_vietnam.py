"""Candidate-keyed Wave 8 audit for HCED's unresolved ``vietnam`` label.

The authoritative funnel contains nine rows.  Seven can be promoted with
event- or campaign-bounded actors, one Siming assertion remains an unknown
outcome, and the anachronistically named Hanoi row is a duplicate of the
reviewed 1789 Thang Long event.  Nothing in this lane creates a generic
Vietnamese, Chinese, Mongol, Cham, dynastic, or modern-state identity.
"""

from __future__ import annotations

import hashlib
import json
import re
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


__all__ = (
    "WAVE8_VIETNAM_CONTRACT_IDS",
    "WAVE8_VIETNAM_CONTRACTS",
    "WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS",
    "WAVE8_VIETNAM_DUPLICATE_DISPOSITIONS",
    "WAVE8_VIETNAM_ENTITIES",
    "WAVE8_VIETNAM_EXCLUSIONS",
    "WAVE8_VIETNAM_EXCLUSION_IDS",
    "WAVE8_VIETNAM_EXPECTED_CANDIDATE_IDS",
    "WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS",
    "WAVE8_VIETNAM_FINAL_AUDIT_SIGNATURE",
    "WAVE8_VIETNAM_FUNNEL_SUMMARY",
    "WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS",
    "WAVE8_VIETNAM_HOLD_IDS",
    "WAVE8_VIETNAM_HOLDS",
    "WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS",
    "WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS",
    "WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT",
    "WAVE8_VIETNAM_LOCATION_QUARANTINE_ADDITIONS",
    "WAVE8_VIETNAM_LOCATION_QUARANTINE_REASONS",
    "WAVE8_VIETNAM_NONPROMOTIONS",
    "WAVE8_VIETNAM_OUTCOME_OVERRIDES",
    "WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS",
    "WAVE8_VIETNAM_RESERVED_IDS",
    "WAVE8_VIETNAM_SOURCES",
    "WAVE8_VIETNAM_TERMINAL_EXCLUSIONS",
    "WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS",
    "install_wave8_vietnam_entities",
    "install_wave8_vietnam_sources",
    "promote_wave8_vietnam_contracts",
    "validate_wave8_vietnam_funnel",
    "validate_wave8_vietnam_integration_dispositions",
    "validate_wave8_vietnam_queue_contracts",
    "wave8_vietnam_audit_signature",
    "wave8_vietnam_cohort_counts",
    "wave8_vietnam_counts",
    "wave8_vietnam_location_quarantine_additions",
)


_LANE_NAME = "Wave 8 Vietnam exact-funnel audit"
_EVENT_ID_PREFIX = "hced_wave8_vietnam_"
_MODULE_OWNER = "wave8_vietnam"

_TRAN_DAI_VIET_DONG_BO_DAU = "tran_dai_viet_dong_bo_dau_force_1258"
_URIYANGKHADAI_1258 = "uriyangkhadai_mongol_invasion_column_1258"
_TRAN_DAI_VIET_BACH_DANG = "tran_dai_viet_bach_dang_force_1288"
_OMAR_YUAN_BACH_DANG = "omar_yuan_bach_dang_fleet_1288"
_LAM_SON_NORTHERN = "lam_son_northern_campaign_forces_1426_1427"
_WANG_TONG_TOT_DONG = "wang_tong_ming_tot_dong_force_1426"
_WANG_TONG_DONG_QUAN = "wang_tong_ming_dong_quan_garrison_1426_1427"
_LIU_SHENG_CHI_LANG = "liu_sheng_ming_relief_column_chi_lang_1427"
_QUANG_TRUNG_1789 = "quang_trung_tay_son_thang_long_force_1789"
_SUN_SHIYI_1789 = "sun_shiyi_qing_thang_long_invasion_force_1789"
_LE_THANH_TONG_1471 = "le_thanh_tong_dai_viet_vijaya_force_1471"
_TRA_TOAN_1471 = "tra_toan_vijaya_champa_defenders_1471"


def _source(
    source_id: str,
    title: str,
    url: str,
    publisher: str,
    source_type: str,
    source_family_id: str,
    *,
    outcome: bool = False,
    crosscheck: bool = False,
) -> dict[str, Any]:
    roles = ["identity_boundary_or_context_reference"]
    if outcome:
        roles.append("outcome")
    if crosscheck:
        roles.append("outcome_consistency_crosscheck")
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": publisher,
        "license": "Citation and link only",
        "source_type": source_type,
        "accessed": "2026-07-16",
        "source_family_id": source_family_id,
        "evidence_roles": sorted(roles),
    }


WAVE8_VIETNAM_SOURCES: tuple[dict[str, Any], ...] = (
    _source(
        "wave8_vietnam_iseas_mongol_navy",
        "The Mongol Navy: Kublai Khan's Invasions of Dai Viet and Champa",
        "https://sealionplus.iseas.edu.sg/nodes/view/27200",
        "ISEAS - Yusof Ishak Institute",
        "academic_working_paper",
        "iseas_mongol_navy",
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_cambridge_brief_history_annan",
        "A brief history of Annan",
        (
            "https://www.cambridge.org/core/books/ming-china-and-vietnam/"
            "brief-history-of-annan/CD6E5A787696821ABFAFED6C47BC49A1"
        ),
        "Cambridge University Press",
        "academic_history_chapter",
        "cambridge_ming_china_vietnam",
        outcome=True,
    ),
    _source(
        "wave8_vietnam_ndj_waterborne_warfare",
        "Waterborne warfare in the resistance wars against the Mongol-ruled Yuan dynasty",
        (
            "https://tapchiqptd.vn/en/research-and-discussion/"
            "waterborne-warfare-a-key-characteristic-of-our-resistance-wars-against-"
            "the-mongolruled-yuan-dynasty/11454.html"
        ),
        "Vietnam National Defence Journal",
        "official_military_history",
        "vietnam_ndj_waterborne_warfare",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_vass_hannom_dong_bo_dau",
        "Bia chùa Hồng Phúc với địa danh Đông Bộ Đầu",
        (
            "https://hannom.vass.gov.vn/tong-muc-luc-tieng-viet/"
            "bia-chua-hong-phuc-voi-dia-danh-dong-bo-dau-tap-chi-han-nom-so-2-"
            "99-2010-tr-67-77-506625"
        ),
        "Vietnam Academy of Social Sciences, Institute of Hán-Nôm Studies",
        "peer_reviewed_journal_article",
        "vass_han_nom_dong_bo_dau",
        outcome=True,
    ),
    _source(
        "wave8_vietnam_scov_dong_bo_dau",
        "Chùa Hòe Nhai và bến Đông Bộ Đầu",
        (
            "https://scov.gov.vn/dat-nuoc-con-nguoi/1000-nam-thang-long-ha-noi/"
            "chua-hoe-nhai-va-ben-dong-bo-dau.html"
        ),
        "State Committee for Overseas Vietnamese",
        "government_public_history",
        "scov_dong_bo_dau",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_quang_ninh_bach_dang",
        "Chiến thắng Bạch Đằng năm 1288",
        (
            "https://www.quangninh.gov.vn/bannganh/bochihuyQST/Trang/"
            "ChiTietTinTuc.aspx?nid=1818"
        ),
        "Quảng Ninh Provincial Military Command",
        "official_military_history",
        "quang_ninh_military_bach_dang",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_anderson_siming_frontier",
        "Commissioner Li and Prefect Huang: Sino-Vietnamese Frontier Trade Networks and Political Alliances in the Southern Song",
        "https://www11.ihp.sinica.edu.tw/storage/w2_file/2168LqNtBFy.pdf",
        "Academia Sinica Institute of History and Philology",
        "peer_reviewed_academic_article",
        "academia_sinica_anderson_siming",
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_ndj_tot_dong",
        "The art of deception and strategic positioning in Tốt Động-Chúc Động",
        (
            "https://tapchiqptd.vn/en/research-and-discussion/"
            "the-art-of-deception-and-strategic-positioning-in-tot-dong-chuc-dong-"
            "battle-of-1426/26252.html"
        ),
        "Vietnam National Defence Journal",
        "official_military_history",
        "vietnam_ndj_tot_dong",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_vass_lam_son",
        "Khởi nghĩa Lam Sơn",
        (
            "https://bachkhoatoanthu.vass.gov.vn/noidung/tudien/Lists/GiaiNghia/"
            "View_Detail.aspx?ChuyenNganh=0&DiaLy=0&ItemID=11978&TuKhoa="
        ),
        "Vietnam Academy of Social Sciences",
        "scholarly_national_encyclopedia",
        "vass_vietnam_encyclopedia_lam_son",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_ndj_chi_lang",
        "Special features of posture establishment in the Battle of Chi Lăng-Xương Giang",
        (
            "https://tapchiqptd.vn/en/research-and-discussion/"
            "special-features-of-posture-establishment-in-the-battle-of-chi-lang-%"
            "E2%80%93-xuong-giang/16205.html"
        ),
        "Vietnam National Defence Journal",
        "official_military_history",
        "vietnam_ndj_chi_lang",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_lang_son_history",
        "Lạng Sơn through historical periods",
        "https://langson.gov.vn/en/tong-quan/lang-son-qua-cac-thoi-ky-lich-su",
        "Lạng Sơn Provincial Government",
        "government_history",
        "lang_son_provincial_history",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_museum_chi_lang",
        "Chiến thắng Chi Lăng-Xương Giang (8/10 đến 3/11/1427)",
        (
            "https://baotanglichsu.vn/VI/Articles/3097/15231/"
            "chien-thang-chi-lang-xuong-giang-8-10-djen-3-11-1427.html"
        ),
        "Vietnam National Museum of History",
        "national_museum_history",
        "vietnam_national_museum_chi_lang",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_museum_dong_quan",
        "Hội thề Đông Quan kết thúc thắng lợi cuộc kháng chiến chống quân Minh",
        (
            "https://baotanglichsu.vn/vi/Articles/2002/68094/"
            "ngay-10-12-1427-hoi-the-djong-quan-ket-thuc-thang-loi-cuoc-khang-"
            "chien-chong-quan-minh.html"
        ),
        "Vietnam National Museum of History",
        "national_museum_history",
        "vietnam_national_museum_dong_quan",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_government_dong_quan",
        "Từ Đông Quan đến Đông Kinh",
        "https://baochinhphu.vn/tu-dong-quan-den-dong-kinh-10230160.htm",
        "Government News of Vietnam",
        "government_history",
        "vietnam_government_news_dong_quan",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_vass_ngoc_hoi_dong_da",
        "Chiến thắng Ngọc Hồi-Đống Đa mùa xuân Kỷ Dậu 1789",
        (
            "https://vass.gov.vn/bai-nghien-cuu-khxh/"
            "chien-thang-ngoc-hoi-dong-da-mua-xuan-nam-ky-dau-1789-dau-an-lich-"
            "su-va-van-hoa-560611"
        ),
        "Vietnam Academy of Social Sciences",
        "academic_history_article",
        "vass_ngoc_hoi_dong_da",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_hanoi_ngoc_hoi_dong_da",
        "Hanoi celebrates the anniversary of the Ngọc Hồi-Đống Đa victory",
        (
            "https://english.hanoi.gov.vn/featured-news/"
            "hanoi-celebrates-the-236th-anniversary-of-the-ngoc-hoi-dong-da-"
            "victory-2655250205215840416.htm"
        ),
        "Hanoi People's Committee",
        "government_public_history",
        "hanoi_government_ngoc_hoi_dong_da",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_scov_ngoc_hoi_dong_da",
        "Trận Ngọc Hồi-Đống Đa",
        "https://scov.gov.vn/ban-sac-van-hoa/tu-dien-van-hoa/tran-ngoc-hoi-dong-da.html",
        "State Committee for Overseas Vietnamese",
        "government_historical_dictionary",
        "scov_ngoc_hoi_dong_da",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_uhpress_tay_son",
        "The Tây Sơn Uprising: Society and Rebellion in Eighteenth-Century Vietnam",
        (
            "https://uhpress.hawaii.edu/title/"
            "the-tay-son-uprising-society-and-rebellion-in-eighteenth-century-"
            "vietnam/?attribute_pa_format=hardback"
        ),
        "University of Hawai'i Press",
        "academic_monograph",
        "university_hawaii_press_tay_son",
    ),
    _source(
        "wave8_vietnam_vass_thang_long_hanoi_names",
        "Người đứng đầu Thăng Long-Hà Nội (1010-1945)",
        (
            "https://app.vass.gov.vn/an-pham-vien-han-lam/sach-hang-nam/"
            "nguoi-dung-dau-thang-long--ha-noi-1010-1945-1043"
        ),
        "Vietnam Academy of Social Sciences",
        "academic_reference_book",
        "vass_thang_long_hanoi_toponymy",
    ),
    _source(
        "wave8_vietnam_ebsco_vijaya",
        "Battle of Vijaya",
        "https://www.ebsco.com/research-starters/history/battle-vijaya",
        "EBSCO Research Starters",
        "scholarly_reference",
        "ebsco_battle_vijaya",
        outcome=True,
        crosscheck=True,
    ),
    _source(
        "wave8_vietnam_danang_vijaya",
        "Chiến thắng Trà Bàn của vua Lê Thánh Tông (1471)",
        (
            "https://www.danang.gov.vn/vi/web/dng/w/"
            "chien-thang-tra-ban-cua-vua-le-thanh-tong-1471-i"
        ),
        "Đà Nẵng City Government",
        "government_history",
        "danang_government_vijaya",
        outcome=True,
        crosscheck=True,
    ),
)

_SOURCE_BY_ID = {str(source["id"]): source for source in WAVE8_VIETNAM_SOURCES}


def _entity(
    entity_id: str,
    name: str,
    kind: str,
    start: int,
    end: int,
    region: str,
    source_ids: Iterable[str],
    boundary_note: str,
) -> dict[str, Any]:
    return {
        "id": entity_id,
        "name": name,
        "kind": kind,
        "start_year": start,
        "end_year": end,
        "region": region,
        "aliases": [],
        "predecessors": [],
        "continuity_note": (
            boundary_note
            + " No rating is inherited by generic Vietnam or Vietnamese people; "
            "the modern Socialist Republic of Vietnam, Democratic Republic of "
            "Vietnam, or Republic of Vietnam; generic China, the PRC, or ROC; "
            "generic Mongol or Cham peoples; or any predecessor or successor "
            "dynasty, regime, army, community, or state. A modern country field is "
            "location metadata only."
        ),
        "source_ids": sorted(set(map(str, source_ids))),
    }


WAVE8_VIETNAM_ENTITIES: tuple[dict[str, Any], ...] = (
    _entity(
        _TRAN_DAI_VIET_DONG_BO_DAU,
        "Trần Đại Việt counterattack force at Đông Bộ Đầu (1258)",
        "event_bounded_dynastic_field_force",
        1258,
        1258,
        "Đông Bộ Đầu landing, Thăng Long",
        [
            "wave8_vietnam_ndj_waterborne_warfare",
            "wave8_vietnam_scov_dong_bo_dau",
            "wave8_vietnam_vass_hannom_dong_bo_dau",
        ],
        (
            "Bounded to the Trần counterattack on the night of 28-29 January "
            "after the Mongol occupation of Thăng Long; it is not a timeless Đại "
            "Việt or Vietnamese actor."
        ),
    ),
    _entity(
        _URIYANGKHADAI_1258,
        "Uriyangkhadai's Mongol invasion column at Đông Bộ Đầu (1258)",
        "event_bounded_invasion_column",
        1258,
        1258,
        "Thăng Long and the Red River corridor",
        [
            "wave8_vietnam_iseas_mongol_navy",
            "wave8_vietnam_ndj_waterborne_warfare",
            "wave8_vietnam_scov_dong_bo_dau",
        ],
        (
            "Bounded to Uriyangkhadai's invasion column during the January 1258 "
            "occupation and Đông Bộ Đầu counterattack, not the Mongol Empire, Yuan "
            "dynasty, or a later invasion force."
        ),
    ),
    _entity(
        _TRAN_DAI_VIET_BACH_DANG,
        "Trần Đại Việt Bạch Đằng force under Trần Hưng Đạo (1288)",
        "event_bounded_combined_force",
        1288,
        1288,
        "Bạch Đằng river system",
        [
            "wave8_vietnam_cambridge_brief_history_annan",
            "wave8_vietnam_iseas_mongol_navy",
            "wave8_vietnam_quang_ninh_bach_dang",
        ],
        (
            "Bounded to Trần Hưng Đạo's riverine and shore forces in the 9 April "
            "Bạch Đằng action; no continuity is asserted to other Trần armies."
        ),
    ),
    _entity(
        _OMAR_YUAN_BACH_DANG,
        "Omar's Yuan withdrawal fleet at Bạch Đằng (1288)",
        "event_bounded_withdrawal_fleet",
        1288,
        1288,
        "Bạch Đằng river system",
        [
            "wave8_vietnam_cambridge_brief_history_annan",
            "wave8_vietnam_iseas_mongol_navy",
            "wave8_vietnam_quang_ninh_bach_dang",
        ],
        (
            "Bounded to Omar's returning Yuan fleet trapped on 9 April 1288; it "
            "does not represent the Yuan dynasty, Mongols generally, or the land "
            "column withdrawing by another route."
        ),
    ),
    _entity(
        _LAM_SON_NORTHERN,
        "Lam Sơn northern campaign forces (1426-1427)",
        "campaign_bounded_insurgent_field_forces",
        1426,
        1427,
        "Red River delta and northern Đại Việt",
        [
            "wave8_vietnam_government_dong_quan",
            "wave8_vietnam_museum_chi_lang",
            "wave8_vietnam_ndj_tot_dong",
            "wave8_vietnam_vass_lam_son",
        ],
        (
            "Bounded to the directly linked Lam Sơn northern operations from Tốt "
            "Động-Chúc Động through the Đông Quan siege and Chi Lăng relief defeat. "
            "It does not automatically become the Later Lê dynasty or every Lam "
            "Sơn formation."
        ),
    ),
    _entity(
        _WANG_TONG_TOT_DONG,
        "Wang Tong's Ming field force at Tốt Động-Chúc Động (1426)",
        "event_bounded_field_force",
        1426,
        1426,
        "Tốt Động and Chúc Động",
        ["wave8_vietnam_ndj_tot_dong", "wave8_vietnam_vass_lam_son"],
        (
            "Bounded to Wang Tong's field corps caught in the November 1426 "
            "ambushes; the surviving Đông Quan garrison is separately bounded."
        ),
    ),
    _entity(
        _WANG_TONG_DONG_QUAN,
        "Wang Tong's Ming Đông Quan garrison (1426-1427)",
        "siege_bounded_garrison",
        1426,
        1427,
        "Đông Quan citadel",
        [
            "wave8_vietnam_government_dong_quan",
            "wave8_vietnam_museum_dong_quan",
            "wave8_vietnam_vass_lam_son",
        ],
        (
            "Bounded to the Ming troops enclosed at Đông Quan from November 1426 "
            "through their December 1427 evacuation; it is not Wang Tong's lost "
            "Tốt Động field corps or Ming China across its reign."
        ),
    ),
    _entity(
        _LIU_SHENG_CHI_LANG,
        "Liu Sheng's Ming relief column at Chi Lăng (1427)",
        "event_bounded_relief_column",
        1427,
        1427,
        "Chi Lăng pass",
        [
            "wave8_vietnam_lang_son_history",
            "wave8_vietnam_museum_chi_lang",
            "wave8_vietnam_ndj_chi_lang",
        ],
        (
            "Bounded to Liu Sheng's relief column in the 10 October pass action; "
            "later Xương Giang phases and other Ming forces are outside this actor."
        ),
    ),
    _entity(
        _QUANG_TRUNG_1789,
        "Quang Trung's Tây Sơn Thăng Long offensive force (1789)",
        "event_bounded_offensive_force",
        1789,
        1789,
        "Ngọc Hồi, Đống Đa, and Thăng Long",
        [
            "wave8_vietnam_hanoi_ngoc_hoi_dong_da",
            "wave8_vietnam_uhpress_tay_son",
            "wave8_vietnam_vass_ngoc_hoi_dong_da",
        ],
        (
            "Bounded to Quang Trung's coordinated Tết offensive culminating at "
            "Thăng Long on 30 January 1789; it is neither all Tây Sơn forces nor a "
            "generic Vietnamese national army."
        ),
    ),
    _entity(
        _SUN_SHIYI_1789,
        "Sun Shiyi's Qing invasion force at Thăng Long (1789)",
        "event_bounded_invasion_force",
        1789,
        1789,
        "Ngọc Hồi, Đống Đa, and Thăng Long",
        [
            "wave8_vietnam_hanoi_ngoc_hoi_dong_da",
            "wave8_vietnam_scov_ngoc_hoi_dong_da",
            "wave8_vietnam_vass_ngoc_hoi_dong_da",
        ],
        (
            "Bounded to Sun Shiyi's deployed Qing invasion army defeated around "
            "Thăng Long; it is not the Qing dynasty across time or any modern "
            "Chinese state."
        ),
    ),
    _entity(
        _LE_THANH_TONG_1471,
        "Lê Thánh Tông's Đại Việt Vijaya expedition (1471)",
        "event_bounded_royal_expedition",
        1471,
        1471,
        "Vijaya (Trà Bàn), Champa",
        ["wave8_vietnam_danang_vijaya", "wave8_vietnam_ebsco_vijaya"],
        (
            "Bounded to Lê Thánh Tông's March 1471 expedition and capture of "
            "Vijaya; no rating passes to all Later Lê forces or to later Vietnamese "
            "polities."
        ),
    ),
    _entity(
        _TRA_TOAN_1471,
        "Trà Toàn's Vijaya defenders (1471)",
        "event_bounded_capital_defenders",
        1471,
        1471,
        "Vijaya (Trà Bàn), Champa",
        ["wave8_vietnam_danang_vijaya", "wave8_vietnam_ebsco_vijaya"],
        (
            "Bounded to Trà Toàn's armed capital defenders during the 18-22 March "
            "siege and capture. It excludes Champa outside Vijaya, successor centers "
            "such as Panduranga, captives, noncombatants, and modern Cham people."
        ),
    ),
)


def _canonical(
    name: str,
    year_low: int,
    year_high: int,
    date_text: str,
    *,
    date_precision: str,
    granularity: str = "engagement",
) -> dict[str, Any]:
    return {
        "canonical_key": f"{_slug(name)}:{year_low}:{year_high}",
        "date_precision": date_precision,
        "date_text": date_text,
        "granularity": granularity,
        "name": name,
        "year_low": year_low,
        "year_high": year_high,
    }


_ROW_HASHES: dict[str, str] = {
    "hced-Bach Dang1288-1": (
        "ef364f053834faa92241a908e2f641c19c7231182725b81da069e9061ed36360"
    ),
    "hced-Chi Lang Pass1427-1": (
        "96c60480dd880f4758435159d0fad4338f7b4f305a9b1aa2dfb9407a2ab434c7"
    ),
    "hced-Dong-do1426-1427-1": (
        "2566dcd135c02b6c21ddc9f01f6015dc8b45393b70e58e26de2d4972f04ef572"
    ),
    "hced-Hanoi1789-1": (
        "3034572de41f712b94ba30a4d8fe4f230f5f90a46452b1ae06ab3bb6dc5c7064"
    ),
    "hced-Siming1285-1": (
        "20e71617da98641add162d86c10632d98c52c907bc32c4af55694e8c0b146a8d"
    ),
    "hced-Thang Long1258-1": (
        "e2b378f2da07b5dcc8b49ba2c0a4287a4b927dc396e1e71b7ebac871084b8fec"
    ),
    "hced-Thang Long1789-1": (
        "b79ddc32e1c4a289d36de2a873a294b3a2f6e2d71a8af580a318945389fa656c"
    ),
    "hced-Tot-dong1426-1": (
        "a221dc9104d01fedbe645b1b87f69a4e3fcc0c1ca9a18882255c8ff4fe5647fa"
    ),
    "hced-Vijaya1471-1": (
        "2e0be2d3ac83a01bfdd3eec7a49f3e4248b138bb8b3e2d492fedb9dc00abc44d"
    ),
}


def _contract(
    candidate_id: str,
    canonical_event: dict[str, Any],
    cohort: str,
    side_1: Iterable[str],
    side_2: Iterable[str],
    evidence_refs: Iterable[str],
    outcome_source_ids: Iterable[str],
    audit_note: str,
    *,
    reviewed_sides: Iterable[str],
    reviewed_outcome: str,
    event_boundary: str,
    war_type: str,
    confidence: float,
) -> dict[str, Any]:
    evidence = sorted(set(map(str, evidence_refs)))
    outcomes = sorted(set(map(str, outcome_source_ids)))
    return {
        "raw_row_sha256": _ROW_HASHES[candidate_id],
        "canonical_event": canonical_event,
        "cohort": cohort,
        "side_1_entity_ids": sorted(set(map(str, side_1))),
        "side_2_entity_ids": sorted(set(map(str, side_2))),
        "result_type": "win",
        "winner_side": 1,
        "war_type": war_type,
        "confidence": confidence,
        "evidence_refs": evidence,
        "outcome_source_ids": outcomes,
        "outcome_source_family_ids": sorted(
            {
                str(_SOURCE_BY_ID[source_id]["source_family_id"])
                for source_id in outcomes
            }
        ),
        "source_outcome_override": False,
        "outcome_reversal": False,
        "actor_override": True,
        "direct_provenance": {
            "reviewed_date": canonical_event["date_text"],
            "reviewed_sides": list(map(str, reviewed_sides)),
            "reviewed_outcome": reviewed_outcome,
            "event_boundary": event_boundary,
        },
        "audit_note": audit_note,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        },
    }


WAVE8_VIETNAM_CONTRACTS: dict[str, dict[str, Any]] = {
    "hced-Thang Long1258-1": _contract(
        "hced-Thang Long1258-1",
        _canonical(
            "Battle of Đông Bộ Đầu",
            1258,
            1258,
            "Night of 28-29 January 1258",
            date_precision="day_range",
        ),
        "tran_mongol_wars",
        [_TRAN_DAI_VIET_DONG_BO_DAU],
        [_URIYANGKHADAI_1258],
        [
            "wave8_vietnam_iseas_mongol_navy",
            "wave8_vietnam_ndj_waterborne_warfare",
            "wave8_vietnam_scov_dong_bo_dau",
            "wave8_vietnam_vass_hannom_dong_bo_dau",
        ],
        [
            "wave8_vietnam_ndj_waterborne_warfare",
            "wave8_vietnam_scov_dong_bo_dau",
            "wave8_vietnam_vass_hannom_dong_bo_dau",
        ],
        (
            "The broad raw Thang Long label is bound to the Trần counterattack at "
            "Đông Bộ Đầu after the nine-day occupation, not to the invasion or city "
            "as a whole. The displaced raw point is withheld."
        ),
        reviewed_sides=[
            "Trần Đại Việt counterattack force",
            "Uriyangkhadai's Mongol invasion column",
        ],
        reviewed_outcome="Trần counterattack victory followed by Mongol withdrawal",
        event_boundary="The night counterattack at Đông Bộ Đầu after the occupation of Thăng Long.",
        war_type="interstate",
        confidence=0.91,
    ),
    "hced-Bach Dang1288-1": _contract(
        "hced-Bach Dang1288-1",
        _canonical(
            "Battle of Bạch Đằng",
            1288,
            1288,
            "9 April 1288",
            date_precision="day",
        ),
        "tran_mongol_wars",
        [_TRAN_DAI_VIET_BACH_DANG],
        [_OMAR_YUAN_BACH_DANG],
        [
            "wave8_vietnam_cambridge_brief_history_annan",
            "wave8_vietnam_iseas_mongol_navy",
            "wave8_vietnam_ndj_waterborne_warfare",
            "wave8_vietnam_quang_ninh_bach_dang",
        ],
        [
            "wave8_vietnam_cambridge_brief_history_annan",
            "wave8_vietnam_quang_ninh_bach_dang",
        ],
        (
            "The rating is limited to Trần Hưng Đạo's riverine ambush of Omar's "
            "withdrawal fleet. It does not merge the Yuan land retreat or rate "
            "generic Vietnam against generic China. The river-system point is "
            "withheld."
        ),
        reviewed_sides=[
            "Trần Hưng Đạo's Bạch Đằng combined force",
            "Omar's Yuan withdrawal fleet",
        ],
        reviewed_outcome="Trần destruction and capture of the Yuan withdrawal fleet",
        event_boundary="The 9 April river battle, not the entire third Yuan invasion.",
        war_type="interstate",
        confidence=0.97,
    ),
    "hced-Tot-dong1426-1": _contract(
        "hced-Tot-dong1426-1",
        _canonical(
            "Battle of Tốt Động-Chúc Động",
            1426,
            1426,
            "5-7 November 1426",
            date_precision="day_range",
        ),
        "lam_son_uprising",
        [_LAM_SON_NORTHERN],
        [_WANG_TONG_TOT_DONG],
        ["wave8_vietnam_ndj_tot_dong", "wave8_vietnam_vass_lam_son"],
        ["wave8_vietnam_ndj_tot_dong", "wave8_vietnam_vass_lam_son"],
        (
            "The row is the linked Tốt Động-Chúc Động ambush complex against Wang "
            "Tong's field force, not the whole Lam Sơn war. The two-position raw "
            "coordinate is withheld."
        ),
        reviewed_sides=[
            "Lam Sơn northern campaign forces",
            "Wang Tong's Ming field force",
        ],
        reviewed_outcome="Lam Sơn destruction and rout of Wang Tong's field force",
        event_boundary="The Tốt Động and Chúc Động ambush sequence of 5-7 November.",
        war_type="anti_imperial_revolt",
        confidence=0.94,
    ),
    "hced-Dong-do1426-1427-1": _contract(
        "hced-Dong-do1426-1427-1",
        _canonical(
            "Siege and evacuation of Đông Quan",
            1426,
            1427,
            "22 November 1426-29 December 1427",
            date_precision="day_range",
            granularity="siege",
        ),
        "lam_son_uprising",
        [_LAM_SON_NORTHERN],
        [_WANG_TONG_DONG_QUAN],
        [
            "wave8_vietnam_government_dong_quan",
            "wave8_vietnam_museum_dong_quan",
            "wave8_vietnam_vass_lam_son",
        ],
        [
            "wave8_vietnam_government_dong_quan",
            "wave8_vietnam_museum_dong_quan",
        ],
        (
            "The raw Dong-do row is bound to the investment, Đông Quan oath, and "
            "Ming evacuation within its locked 1426-1427 interval. It does not rate "
            "the later Lê state or duplicate Tốt Động. The city point is withheld."
        ),
        reviewed_sides=[
            "Lam Sơn northern campaign forces",
            "Wang Tong's Ming Đông Quan garrison",
        ],
        reviewed_outcome="Ming capitulation agreement and evacuation from Đông Quan",
        event_boundary="The siege from the first November attack through the start of the completed withdrawal.",
        war_type="anti_imperial_revolt",
        confidence=0.92,
    ),
    "hced-Chi Lang Pass1427-1": _contract(
        "hced-Chi Lang Pass1427-1",
        _canonical(
            "Battle of Chi Lăng Pass",
            1427,
            1427,
            "10 October 1427",
            date_precision="day",
        ),
        "lam_son_uprising",
        [_LAM_SON_NORTHERN],
        [_LIU_SHENG_CHI_LANG],
        [
            "wave8_vietnam_lang_son_history",
            "wave8_vietnam_museum_chi_lang",
            "wave8_vietnam_ndj_chi_lang",
            "wave8_vietnam_vass_lam_son",
        ],
        [
            "wave8_vietnam_lang_son_history",
            "wave8_vietnam_museum_chi_lang",
            "wave8_vietnam_ndj_chi_lang",
        ],
        (
            "The event stops at the pass action in which Liu Sheng's relief column "
            "was defeated; the later Xương Giang destruction is not a second result "
            "inside this row. The pass-locality point is withheld."
        ),
        reviewed_sides=[
            "Lam Sơn northern campaign forces at Chi Lăng",
            "Liu Sheng's Ming relief column",
        ],
        reviewed_outcome="Lam Sơn victory and defeat of Liu Sheng's relief column",
        event_boundary="The 10 October pass ambush, not the full October-November relief campaign.",
        war_type="anti_imperial_revolt",
        confidence=0.95,
    ),
    "hced-Vijaya1471-1": _contract(
        "hced-Vijaya1471-1",
        _canonical(
            "Capture of Vijaya",
            1471,
            1471,
            "18-22 March 1471",
            date_precision="day_range",
            granularity="siege",
        ),
        "dai_viet_champa_war",
        [_LE_THANH_TONG_1471],
        [_TRA_TOAN_1471],
        ["wave8_vietnam_danang_vijaya", "wave8_vietnam_ebsco_vijaya"],
        ["wave8_vietnam_danang_vijaya", "wave8_vietnam_ebsco_vijaya"],
        (
            "The contract rates the March siege and capture of Trà Toàn's capital "
            "defenders only. It excludes the reported post-capture massacre, "
            "noncombatants, surviving Champa centers, and modern Cham people. The "
            "far-inland raw point is withheld."
        ),
        reviewed_sides=[
            "Lê Thánh Tông's Đại Việt expedition",
            "Trà Toàn's Vijaya capital defenders",
        ],
        reviewed_outcome="Capture of Vijaya and Trà Toàn by Lê Thánh Tông's expedition",
        event_boundary="The 18-22 March siege and capture; post-capture killing is not a separate Elo event.",
        war_type="interstate",
        confidence=0.93,
    ),
    "hced-Thang Long1789-1": _contract(
        "hced-Thang Long1789-1",
        _canonical(
            "Ngọc Hồi-Đống Đa offensive at Thăng Long",
            1789,
            1789,
            "30 January 1789",
            date_precision="day",
        ),
        "tay_son_qing_war",
        [_QUANG_TRUNG_1789],
        [_SUN_SHIYI_1789],
        [
            "wave8_vietnam_hanoi_ngoc_hoi_dong_da",
            "wave8_vietnam_scov_ngoc_hoi_dong_da",
            "wave8_vietnam_uhpress_tay_son",
            "wave8_vietnam_vass_ngoc_hoi_dong_da",
            "wave8_vietnam_vass_thang_long_hanoi_names",
        ],
        [
            "wave8_vietnam_hanoi_ngoc_hoi_dong_da",
            "wave8_vietnam_scov_ngoc_hoi_dong_da",
            "wave8_vietnam_vass_ngoc_hoi_dong_da",
        ],
        (
            "The coordinated Ngọc Hồi-Đống Đa actions and Qing flight from Thăng "
            "Long form one bounded offensive result. The duplicate HCED Hanoi row "
            "is excluded because Hanoi was not the city's 1789 name. The displaced "
            "single point is withheld."
        ),
        reviewed_sides=[
            "Quang Trung's Tây Sơn Thăng Long offensive force",
            "Sun Shiyi's Qing invasion force",
        ],
        reviewed_outcome="Tây Sơn defeat of the Qing invasion force and recovery of Thăng Long",
        event_boundary="The culminating 30 January coordinated actions and Qing evacuation, not the whole invasion.",
        war_type="interstate",
        confidence=0.96,
    ),
}


WAVE8_VIETNAM_HOLDS: dict[str, dict[str, Any]] = {
    "hced-Siming1285-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Siming1285-1"],
        "canonical_event": _canonical(
            "Reported Siming frontier action",
            1285,
            1285,
            "1285",
            date_precision="year",
        ),
        "disposition": "hold",
        "terminal_exclusion": False,
        "hold_category": "actor_and_terminal_tactical_outcome_unresolved",
        "reviewed_outcome": "unknown",
        "result_type": "unknown",
        "unknown_is_never_draw": True,
        "reviewed_actor_description": [
            "Toghon's retreating Yuan forces near Siming",
            "Huang-lineage frontier forces loyal to the Trần court",
        ],
        "reviewed_granularity": "frontier_retreat_episode",
        "hold_reason": (
            "Academic evidence places Toghon's retreat at Siming and describes an "
            "attack by local Huang descendants aligned with the Trần court, but it "
            "does not establish a unique terminal tactical winner matching HCED's "
            "binary Vietnam-Mongols assertion. The participant string also conflates "
            "Champa, Yunnan, Siming, and generic labels. The row is not promoted, "
            "reversed, or converted to a draw: unknown remains unknown."
        ),
        "evidence_refs": [
            "wave8_vietnam_anderson_siming_frontier",
            "wave8_vietnam_iseas_mongol_navy",
        ],
        "full_row_audited": True,
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "provisional_hced_hold",
        },
    }
}


WAVE8_VIETNAM_TERMINAL_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "hced-Hanoi1789-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Hanoi1789-1"],
        "canonical_event": _canonical(
            "Ngọc Hồi-Đống Đa offensive at Thăng Long",
            1789,
            1789,
            "30 January 1789",
            date_precision="day",
        ),
        "disposition": "terminal_exclusion",
        "terminal_exclusion": True,
        "hold_category": "same_event_duplicate_and_anachronistic_toponym",
        "reviewed_outcome": (
            "The same Tây Sơn victory over Sun Shiyi's Qing invasion force already "
            "owned by hced-Thang Long1789-1"
        ),
        "reviewed_actor_description": [
            "Quang Trung's bounded Tây Sơn offensive force",
            "Sun Shiyi's bounded Qing invasion force",
        ],
        "reviewed_granularity": "duplicate_exact_event_assertion",
        "hold_reason": (
            "HCED's Hanoi and Thang Long 1789 rows describe the same Ngọc Hồi-Đống "
            "Đa/Qing-defeat episode. Thăng Long is the period-appropriate city name; "
            "Hanoi was introduced in 1831. Emitting both would double-rate one result, "
            "so this row is terminally excluded in favor of hced-Thang Long1789-1."
        ),
        "evidence_refs": [
            "wave8_vietnam_vass_ngoc_hoi_dong_da",
            "wave8_vietnam_vass_thang_long_hanoi_names",
        ],
        "full_row_audited": True,
        "duplicate_of_hced_candidate_id": "hced-Thang Long1789-1",
        "duplicate_ownership": {
            "owner_module": _MODULE_OWNER,
            "status": "terminal_duplicate_exclusion",
        },
    }
}

WAVE8_VIETNAM_EXCLUSIONS = WAVE8_VIETNAM_TERMINAL_EXCLUSIONS
WAVE8_VIETNAM_NONPROMOTIONS: dict[str, dict[str, Any]] = {
    **WAVE8_VIETNAM_HOLDS,
    **WAVE8_VIETNAM_TERMINAL_EXCLUSIONS,
}

WAVE8_VIETNAM_CONTRACT_IDS = frozenset(WAVE8_VIETNAM_CONTRACTS)
WAVE8_VIETNAM_HOLD_IDS = frozenset(WAVE8_VIETNAM_HOLDS)
WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS = frozenset(
    WAVE8_VIETNAM_TERMINAL_EXCLUSIONS
)
WAVE8_VIETNAM_EXCLUSION_IDS = WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS
WAVE8_VIETNAM_RESERVED_IDS = (
    WAVE8_VIETNAM_CONTRACT_IDS
    | WAVE8_VIETNAM_HOLD_IDS
    | WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS
)
WAVE8_VIETNAM_EXPECTED_CANDIDATE_IDS = frozenset(_ROW_HASHES)


# All emitted points are either displaced, over-precise for a multi-position
# event, or not source-audited to the reviewed event boundary. Country remains
# valid modern location metadata. Holds and exclusions receive no quarantine.
WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS = frozenset(
    WAVE8_VIETNAM_CONTRACT_IDS
)
WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS = frozenset()
WAVE8_VIETNAM_LOCATION_QUARANTINE_ADDITIONS = {
    "point": WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS,
    "country": WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS,
}
WAVE8_VIETNAM_LOCATION_QUARANTINE_REASONS: dict[str, str] = {
    "hced-Bach Dang1288-1": "River-system battlefield; the exact raw point is not source-audited.",
    "hced-Chi Lang Pass1427-1": "Pass ambush and relief action; the locality point is over-precise.",
    "hced-Dong-do1426-1427-1": "Year-long siege fronts cannot be represented by the generic city point.",
    "hced-Thang Long1258-1": "The raw point is displaced west of the reviewed Red River landing action.",
    "hced-Thang Long1789-1": "The raw point is displaced and the offensive spans several positions.",
    "hced-Tot-dong1426-1": "Tốt Động-Chúc Động is a linked multi-position ambush complex.",
    "hced-Vijaya1471-1": "The raw inland point does not identify the reviewed Vijaya capital site.",
}


WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "hced-Hanoi1789-1": {
        "raw_row_sha256": _ROW_HASHES["hced-Hanoi1789-1"],
        "related_hced_candidate_id": "hced-Thang Long1789-1",
        "related_raw_row_sha256": _ROW_HASHES["hced-Thang Long1789-1"],
        "disposition": "terminal_duplicate_exclusion",
        "relationship": "same_ngoc_hoi_dong_da_qing_defeat_episode",
        "canonical_owner": "hced-Thang Long1789-1",
        "reason": (
            "The rows share year, sides, result, theater, and episode. Thăng Long is "
            "the historically bounded 1789 toponym; Hanoi dates from 1831."
        ),
        "evidence_refs": [
            "wave8_vietnam_vass_ngoc_hoi_dong_da",
            "wave8_vietnam_vass_thang_long_hanoi_names",
        ],
    }
}
WAVE8_VIETNAM_DUPLICATE_DISPOSITIONS = (
    WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS
)
WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS: dict[str, dict[str, Any]] = {}
WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS: dict[
    str, dict[str, Any]
] = {}
WAVE8_VIETNAM_OUTCOME_OVERRIDES: dict[str, dict[str, Any]] = {}


WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT: dict[str, dict[str, Any]] = {
    "hced-Bach Dang1288-1": {
        "aliases": ("bach dang", "battle of bach dang"),
        "years": (1288, 1288),
    },
    "hced-Chi Lang Pass1427-1": {
        "aliases": (
            "battle of chi lang pass",
            "chi lang",
            "chi lang pass",
            "chi lang xuong giang",
        ),
        "years": (1427, 1427),
    },
    "hced-Dong-do1426-1427-1": {
        "aliases": (
            "dong do",
            "dong quan",
            "siege and evacuation of dong quan",
            "siege of dong quan",
        ),
        "years": (1426, 1427),
    },
    "hced-Hanoi1789-1": {
        "aliases": (
            "dong da",
            "hanoi",
            "ngoc hoi dong da",
            "ngoc hoi dong da offensive at thang long",
            "thang long",
        ),
        "years": (1789, 1789),
    },
    "hced-Siming1285-1": {
        "aliases": ("reported siming frontier action", "si ming", "siming"),
        "years": (1285, 1285),
    },
    "hced-Thang Long1258-1": {
        "aliases": (
            "battle of dong bo dau",
            "dong bo dau",
            "thang long",
        ),
        "years": (1258, 1258),
    },
    "hced-Thang Long1789-1": {
        "aliases": (
            "dong da",
            "hanoi",
            "ngoc hoi dong da",
            "ngoc hoi dong da offensive at thang long",
            "thang long",
        ),
        "years": (1789, 1789),
    },
    "hced-Tot-dong1426-1": {
        "aliases": (
            "battle of tot dong chuc dong",
            "chuc dong",
            "tot dong",
            "tot dong chuc dong",
        ),
        "years": (1426, 1426),
    },
    "hced-Vijaya1471-1": {
        "aliases": (
            "capture of vijaya",
            "cha ban",
            "tra ban",
            "vijaya",
        ),
        "years": (1471, 1471),
    },
}


_FUNNEL_SCOPE: dict[
    str, tuple[tuple[str, ...], bool, str | None, tuple[str, ...]]
] = {
    "hced-Bach Dang1288-1": (
        ("vietnam",),
        False,
        None,
        ("other_identity_blocker:no_unique_time_valid_polity",),
    ),
    "hced-Chi Lang Pass1427-1": (("vietnam",), True, "vietnam", ()),
    "hced-Dong-do1426-1427-1": (("vietnam",), True, "vietnam", ()),
    "hced-Hanoi1789-1": (("qing", "vietnam"), True, None, ()),
    "hced-Siming1285-1": (
        ("vietnam",),
        False,
        None,
        ("other_identity_blocker:faction_label_not_a_polity",),
    ),
    "hced-Thang Long1258-1": (("mongols china", "vietnam"), True, None, ()),
    "hced-Thang Long1789-1": (("vietnam",), True, "vietnam", ()),
    "hced-Tot-dong1426-1": (("vietnam",), True, "vietnam", ()),
    "hced-Vijaya1471-1": (
        ("vietnam",),
        False,
        None,
        ("other_identity_blocker:label_pending_identity_split",),
    ),
}

WAVE8_VIETNAM_FUNNEL_SUMMARY: dict[str, Any] = {
    "candidate_ids": ["clio_vt_vietnam_socialist_rep_1976_7f7549c0"],
    "centuries": {"CE_13": 3, "CE_15": 4, "CE_18": 2},
    "components_bridged": 0,
    "components_touched": 1,
    "event_candidate_id_sha256": (
        "1a6431d8b16f1868a7b7b6a4cc8d779c87b37418151703f1f312d1e8babe26dc"
    ),
    "events_touched": 9,
    "failure_cases": {
        "multiple_time_valid_candidates": 0,
        "one_wrong_interval_candidate": 9,
        "policy_denied_window": 0,
        "resolver_guard_or_tier_conflict": 0,
        "zero_time_valid_candidates": 0,
    },
    "label": "vietnam",
    "rated_counterpart_entities": 2,
    "sole_blocker_events": 4,
    "time_valid_candidate_ids": [],
    "unresolved_side_attempts": 9,
}


def _integration_dispositions() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for candidate_id, (labels, eligible, sole, other) in _FUNNEL_SCOPE.items():
        if candidate_id in WAVE8_VIETNAM_CONTRACTS:
            disposition = "PROMOTE"
            all_actors = True
        elif candidate_id in WAVE8_VIETNAM_HOLDS:
            disposition = "HOLD"
            all_actors = False
        else:
            disposition = "EXCLUDE"
            all_actors = True
        duplicate_ids = (
            ["hanoi_thang_long_1789"]
            if candidate_id in {"hced-Hanoi1789-1", "hced-Thang Long1789-1"}
            else []
        )
        result[candidate_id] = {
            "disposition": disposition,
            "full_row_audited": True,
            "blocker_labels": list(labels),
            "greedy_eligible": eligible,
            "sole_blocker_label": sole,
            "other_blockers": list(other),
            "all_opposing_actors_resolved": all_actors,
            "duplicate_review_ids": duplicate_ids,
            "release_duplicate_scan": (
                "duplicate_of_reserved_hced_candidate"
                if candidate_id == "hced-Hanoi1789-1"
                else "no_existing_release_event_twin_found"
            ),
        }
    return result


WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS = _integration_dispositions()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _signature_payload() -> dict[str, Any]:
    return {
        "contracts": WAVE8_VIETNAM_CONTRACTS,
        "country_quarantine_additions": sorted(
            WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "entities": WAVE8_VIETNAM_ENTITIES,
        "existing_release_duplicate_dispositions": (
            WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS
        ),
        "expected_candidate_ids": sorted(WAVE8_VIETNAM_EXPECTED_CANDIDATE_IDS),
        "funnel_summary": WAVE8_VIETNAM_FUNNEL_SUMMARY,
        "hced_duplicate_dispositions": WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS,
        "holds": WAVE8_VIETNAM_HOLDS,
        "integration_dispositions": WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS,
        "iwbd_duplicate_dispositions": WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS,
        "iwbd_zero_overlap_audit": WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT,
        "location_quarantine_reasons": WAVE8_VIETNAM_LOCATION_QUARANTINE_REASONS,
        "outcome_overrides": WAVE8_VIETNAM_OUTCOME_OVERRIDES,
        "point_quarantine_additions": sorted(
            WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS
        ),
        "sources": WAVE8_VIETNAM_SOURCES,
        "terminal_exclusions": WAVE8_VIETNAM_TERMINAL_EXCLUSIONS,
    }


def wave8_vietnam_audit_signature() -> str:
    """Return the deterministic digest of the complete Vietnam audit state."""

    return hashlib.sha256(
        _canonical_json(_signature_payload()).encode("utf-8")
    ).hexdigest()


WAVE8_VIETNAM_FINAL_AUDIT_SIGNATURE = (
    "9153c2022ad61e0b47e877b89c75c5623c2276b3509c3003dc366ed036fd1dee"
)


def _is_sorted_unique(values: Iterable[str]) -> bool:
    items = list(map(str, values))
    return items == sorted(set(items))


def _validate_static() -> None:
    if (
        len(WAVE8_VIETNAM_CONTRACTS),
        len(WAVE8_VIETNAM_HOLDS),
        len(WAVE8_VIETNAM_TERMINAL_EXCLUSIONS),
    ) != (7, 1, 1):
        raise ValueError(f"{_LANE_NAME} disposition inventory changed")
    if (len(WAVE8_VIETNAM_ENTITIES), len(WAVE8_VIETNAM_SOURCES)) != (12, 21):
        raise ValueError(f"{_LANE_NAME} fixture inventory changed")
    if WAVE8_VIETNAM_RESERVED_IDS != WAVE8_VIETNAM_EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"{_LANE_NAME} reservations are incomplete")
    disposition_sets = (
        WAVE8_VIETNAM_CONTRACT_IDS,
        WAVE8_VIETNAM_HOLD_IDS,
        WAVE8_VIETNAM_TERMINAL_EXCLUSION_IDS,
    )
    if any(
        disposition_sets[left] & disposition_sets[right]
        for left in range(3)
        for right in range(left + 1, 3)
    ):
        raise ValueError(f"{_LANE_NAME} dispositions overlap")
    if wave8_vietnam_audit_signature() != WAVE8_VIETNAM_FINAL_AUDIT_SIGNATURE:
        raise ValueError(f"{_LANE_NAME} final audit signature changed")

    if len(_SOURCE_BY_ID) != 21:
        raise ValueError(f"{_LANE_NAME} source IDs are not unique")
    if len({source["source_family_id"] for source in WAVE8_VIETNAM_SOURCES}) != 21:
        raise ValueError(f"{_LANE_NAME} source families are not unique")
    for source in WAVE8_VIETNAM_SOURCES:
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"{_LANE_NAME} source is not an HTTPS direct link")
        if source["accessed"] != "2026-07-16":
            raise ValueError(f"{_LANE_NAME} source access date drifted")
        if not _is_sorted_unique(source["evidence_roles"]):
            raise ValueError(f"{_LANE_NAME} source roles are not canonical")

    entity_by_id = {str(entity["id"]): entity for entity in WAVE8_VIETNAM_ENTITIES}
    if len(entity_by_id) != 12:
        raise ValueError(f"{_LANE_NAME} entity IDs are not unique")
    forbidden_names = {
        "champa",
        "china",
        "mongols",
        "qing",
        "vietnam",
        "vietnamese",
    }
    for entity in WAVE8_VIETNAM_ENTITIES:
        low = int(entity["start_year"])
        high = int(entity["end_year"])
        if low > high or high - low > 1 or entity["aliases"] or entity["predecessors"]:
            raise ValueError(f"{_LANE_NAME} identity is not event/campaign bounded")
        if normalize_label(entity["name"]) in forbidden_names:
            raise ValueError(f"{_LANE_NAME} installed a generic identity")
        note = str(entity["continuity_note"]).casefold()
        if not all(
            token in note
            for token in (
                "no rating is inherited",
                "modern",
                "predecessor or successor",
            )
        ):
            raise ValueError(f"{_LANE_NAME} identity lacks a continuity firewall")
        if not _is_sorted_unique(entity["source_ids"]):
            raise ValueError(f"{_LANE_NAME} identity provenance is not canonical")
        if not set(map(str, entity["source_ids"])) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} identity names an unknown source")

    used_entities: set[str] = set()
    used_sources: set[str] = set()
    for candidate_id, contract in WAVE8_VIETNAM_CONTRACTS.items():
        if contract["raw_row_sha256"] != _ROW_HASHES[candidate_id]:
            raise ValueError(f"{_LANE_NAME} promotion hash drifted")
        canonical = contract["canonical_event"]
        expected_key = (
            f"{_slug(str(canonical['name']))}:"
            f"{int(canonical['year_low'])}:{int(canonical['year_high'])}"
        )
        if canonical["canonical_key"] != expected_key or not canonical["date_text"]:
            raise ValueError(f"{_LANE_NAME} canonical event drifted")
        if canonical["date_precision"] not in {"day", "day_range"}:
            raise ValueError(f"{_LANE_NAME} promotion lacks a direct date")
        if canonical["granularity"] not in {"engagement", "siege"}:
            raise ValueError(f"{_LANE_NAME} event boundary drifted")
        side_1 = set(map(str, contract["side_1_entity_ids"]))
        side_2 = set(map(str, contract["side_2_entity_ids"]))
        if not side_1 or not side_2 or side_1 & side_2:
            raise ValueError(f"{_LANE_NAME} has invalid opposing sides")
        if not (side_1 | side_2) <= set(entity_by_id):
            raise ValueError(f"{_LANE_NAME} uses an unknown identity")
        used_entities.update(side_1 | side_2)
        low = int(canonical["year_low"])
        high = int(canonical["year_high"])
        for entity_id in side_1 | side_2:
            entity = entity_by_id[entity_id]
            if not int(entity["start_year"]) <= low <= high <= int(entity["end_year"]):
                raise ValueError(f"{_LANE_NAME} exceeds an identity window")
        if (
            contract["result_type"] != "win"
            or contract["winner_side"] != 1
            or contract["source_outcome_override"] is not False
            or contract["outcome_reversal"] is not False
            or contract["actor_override"] is not True
        ):
            raise ValueError(f"{_LANE_NAME} invented or reversed an outcome")
        if contract["duplicate_ownership"] != {
            "owner_module": _MODULE_OWNER,
            "status": "canonical_hced_owner",
        }:
            raise ValueError(f"{_LANE_NAME} duplicate ownership drifted")
        evidence = list(map(str, contract["evidence_refs"]))
        outcomes = list(map(str, contract["outcome_source_ids"]))
        families = list(map(str, contract["outcome_source_family_ids"]))
        if not _is_sorted_unique(evidence) or not set(evidence) <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} evidence provenance drifted")
        if (
            len(outcomes) < 2
            or not _is_sorted_unique(outcomes)
            or not set(outcomes) <= set(evidence)
        ):
            raise ValueError(f"{_LANE_NAME} lacks independent outcome sources")
        if any("outcome" not in _SOURCE_BY_ID[item]["evidence_roles"] for item in outcomes):
            raise ValueError(f"{_LANE_NAME} uses a non-outcome source")
        expected_families = sorted(
            {str(_SOURCE_BY_ID[item]["source_family_id"]) for item in outcomes}
        )
        if families != expected_families or len(families) < 2:
            raise ValueError(f"{_LANE_NAME} outcome families drifted")
        provenance = contract["direct_provenance"]
        if set(provenance) != {
            "event_boundary",
            "reviewed_date",
            "reviewed_outcome",
            "reviewed_sides",
        } or not all(provenance.values()):
            raise ValueError(f"{_LANE_NAME} direct provenance drifted")
        used_sources.update(evidence)

    if used_entities != set(entity_by_id):
        raise ValueError(f"{_LANE_NAME} entities are not exactly consumed")

    siming = WAVE8_VIETNAM_HOLDS["hced-Siming1285-1"]
    if (
        siming["raw_row_sha256"] != _ROW_HASHES["hced-Siming1285-1"]
        or siming["disposition"] != "hold"
        or siming["terminal_exclusion"] is not False
        or siming["reviewed_outcome"] != "unknown"
        or siming["result_type"] != "unknown"
        or siming["unknown_is_never_draw"] is not True
        or any(
            key in siming
            for key in (
                "outcome_source_ids",
                "side_1_entity_ids",
                "side_2_entity_ids",
                "winner_side",
            )
        )
    ):
        raise ValueError(f"{_LANE_NAME} Siming hold became rateable")
    siming_reason = str(siming["hold_reason"]).casefold()
    if "draw" not in siming_reason or "unknown remains unknown" not in siming_reason:
        raise ValueError(f"{_LANE_NAME} unknown/draw firewall drifted")

    hanoi = WAVE8_VIETNAM_TERMINAL_EXCLUSIONS["hced-Hanoi1789-1"]
    if (
        hanoi["raw_row_sha256"] != _ROW_HASHES["hced-Hanoi1789-1"]
        or hanoi["disposition"] != "terminal_exclusion"
        or hanoi["terminal_exclusion"] is not True
        or hanoi["duplicate_of_hced_candidate_id"] != "hced-Thang Long1789-1"
        or any(
            key in hanoi
            for key in (
                "result_type",
                "side_1_entity_ids",
                "side_2_entity_ids",
                "winner_side",
            )
        )
    ):
        raise ValueError(f"{_LANE_NAME} Hanoi duplicate exclusion drifted")

    for item in WAVE8_VIETNAM_NONPROMOTIONS.values():
        if item["full_row_audited"] is not True:
            raise ValueError(f"{_LANE_NAME} reserved an unaudited row")
        evidence = set(map(str, item["evidence_refs"]))
        if not evidence <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} nonpromotion names an unknown source")
        used_sources.update(evidence)
    used_sources.update(
        source_id
        for entity in WAVE8_VIETNAM_ENTITIES
        for source_id in map(str, entity["source_ids"])
    )
    for disposition in WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS.values():
        evidence = set(map(str, disposition["evidence_refs"]))
        if not evidence <= set(_SOURCE_BY_ID):
            raise ValueError(f"{_LANE_NAME} duplicate evidence drifted")
        used_sources.update(evidence)
    if used_sources != set(_SOURCE_BY_ID):
        raise ValueError(f"{_LANE_NAME} sources are not exactly consumed")

    if WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS != WAVE8_VIETNAM_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} point quarantine inventory changed")
    if WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS:
        raise ValueError(f"{_LANE_NAME} invented a country quarantine")
    if set(WAVE8_VIETNAM_LOCATION_QUARANTINE_REASONS) != WAVE8_VIETNAM_CONTRACT_IDS:
        raise ValueError(f"{_LANE_NAME} quarantine reasons are incomplete")
    if WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an IWBD duplicate")
    if WAVE8_VIETNAM_EXISTING_RELEASE_DUPLICATE_DISPOSITIONS:
        raise ValueError(f"{_LANE_NAME} acquired an existing-release duplicate")
    if WAVE8_VIETNAM_OUTCOME_OVERRIDES:
        raise ValueError(f"{_LANE_NAME} acquired an outcome override")
    if set(WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT) != WAVE8_VIETNAM_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} IWBD negative audit is incomplete")
    if set(WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS) != {"hced-Hanoi1789-1"}:
        raise ValueError(f"{_LANE_NAME} HCED duplicate inventory changed")
    if set(WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS) != WAVE8_VIETNAM_RESERVED_IDS:
        raise ValueError(f"{_LANE_NAME} integration inventory is incomplete")
    if sum(
        bool(item["greedy_eligible"])
        for item in WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.values()
    ) != 6:
        raise ValueError(f"{_LANE_NAME} greedy eligibility count drifted")
    if sum(
        item["sole_blocker_label"] == "vietnam"
        for item in WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.values()
    ) != 4:
        raise ValueError(f"{_LANE_NAME} sole-blocker count drifted")
    if not all(
        WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS[candidate_id]["disposition"]
        == "PROMOTE"
        for candidate_id, item in WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.items()
        if item["sole_blocker_label"] == "vietnam"
    ):
        raise ValueError(f"{_LANE_NAME} did not resolve every sole blocker")


def validate_wave8_vietnam_queue_contracts(
    hced_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Validate all nine funnel-owned rows and their complete raw fingerprints."""

    _validate_static()
    result = validate_exact_hced_inventory(
        hced_rows,
        WAVE8_VIETNAM_CONTRACTS,
        WAVE8_VIETNAM_NONPROMOTIONS,
        lane_name=_LANE_NAME,
    )
    return {
        "promotion_contracts": result["promotion_contracts"],
        "holds": len(WAVE8_VIETNAM_HOLDS),
        "reviewed_hced_rows": result["reviewed_hced_rows"],
        "terminal_exclusions": len(WAVE8_VIETNAM_TERMINAL_EXCLUSIONS),
    }


def validate_wave8_vietnam_funnel(funnel: Mapping[str, Any]) -> dict[str, int]:
    """Fail closed if the authoritative unresolved-label cohort changes."""

    _validate_static()
    label_rows = [
        item
        for item in funnel.get("labels", [])
        if normalize_label(item.get("label")) == "vietnam"
    ]
    if len(label_rows) != 1:
        raise ValueError(
            f"{_LANE_NAME} expected one Vietnam funnel summary, found {len(label_rows)}"
        )
    actual_summary = {
        key: label_rows[0].get(key) for key in WAVE8_VIETNAM_FUNNEL_SUMMARY
    }
    if actual_summary != WAVE8_VIETNAM_FUNNEL_SUMMARY:
        raise ValueError(f"{_LANE_NAME} Vietnam funnel summary changed")

    scoped = {
        str(row.get("candidate_id")): row
        for row in funnel.get("row_label_data", [])
        if "vietnam" in list(map(str, row.get("blocker_labels", [])))
    }
    if set(scoped) != WAVE8_VIETNAM_RESERVED_IDS:
        raise ValueError(
            f"{_LANE_NAME} exact funnel cohort changed: {sorted(scoped)}"
        )
    for candidate_id, row in scoped.items():
        labels, eligible, sole, other = _FUNNEL_SCOPE[candidate_id]
        actual = (
            tuple(map(str, row.get("blocker_labels", []))),
            bool(row.get("greedy_eligible")),
            row.get("sole_blocker_label"),
            tuple(map(str, row.get("other_blockers", []))),
        )
        if actual != (labels, eligible, sole, other):
            raise ValueError(f"{_LANE_NAME} funnel row changed for {candidate_id}")
        vietnam_failures = [
            failure
            for failure in row.get("label_failures", [])
            if normalize_label(failure.get("label")) == "vietnam"
        ]
        expected_failure = {
            "candidate_ids": ["clio_vt_vietnam_socialist_rep_1976_7f7549c0"],
            "failure_case": "one_wrong_interval_candidate",
            "label": "vietnam",
            "time_valid_candidate_ids": [],
        }
        if vietnam_failures != [expected_failure]:
            raise ValueError(
                f"{_LANE_NAME} Vietnam label failure changed for {candidate_id}"
            )
    return {
        "events_touched": len(scoped),
        "greedy_eligible_rows": sum(
            bool(row["greedy_eligible"]) for row in scoped.values()
        ),
        "sole_blocker_rows": sum(
            row.get("sole_blocker_label") == "vietnam" for row in scoped.values()
        ),
    }


def _year_from_date(value: Any) -> int | None:
    match = re.search(r"(?<!\d)(\d{4})(?!\d)", str(value or ""))
    return int(match.group(1)) if match else None


def _row_year_range(row: Mapping[str, Any]) -> tuple[int, int] | None:
    if row.get("year_low") is not None:
        low = int(row["year_low"])
        high_value = row.get("year_high")
        high = int(high_value) if high_value is not None else low
        return low, high
    if row.get("year") is not None:
        low = int(row["year"])
        high_value = row.get("end_year")
        high = int(high_value) if high_value is not None else low
        return low, high
    low = _year_from_date(row.get("start_date"))
    high = _year_from_date(row.get("end_date"))
    if low is None and high is None:
        return None
    return low if low is not None else high, high if high is not None else low


def _normalize_event_label(value: Any) -> str:
    # Unicode decomposition does not fold Vietnamese đ/Đ to ASCII d.  Duplicate
    # audits must treat the accented and ASCII source spellings as equivalent.
    return normalize_label(str(value or "").replace("Đ", "D").replace("đ", "d"))


def _normalized_event_names(row: Mapping[str, Any]) -> set[str]:
    values = [row.get("name"), *(row.get("aliases") or [])]
    result: set[str] = set()
    for value in values:
        normalized = _normalize_event_label(value)
        if not normalized:
            continue
        result.add(normalized)
        result.add(
            re.sub(
                r"^(?:battle|capture|siege)(?: of| at| and evacuation of)? ",
                "",
                normalized,
            )
        )
    return result


def _audit_aliases(item: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for alias in item["aliases"]:
        normalized = _normalize_event_label(alias)
        result.add(normalized)
        result.add(
            re.sub(
                r"^(?:battle|capture|siege)(?: of| at| and evacuation of)? ",
                "",
                normalized,
            )
        )
    return result


def _find_unreviewed_overlap(
    rows: Iterable[Mapping[str, Any]],
    *,
    skip_candidate_ids: frozenset[str] = frozenset(),
) -> tuple[str, str] | None:
    audits = {
        candidate_id: (
            _audit_aliases(item),
            tuple(map(int, item["years"])),
        )
        for candidate_id, item in WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT.items()
    }
    for row in rows:
        row_id = str(row.get("candidate_id") or row.get("id") or "unidentified")
        if row_id in skip_candidate_ids:
            continue
        years = _row_year_range(row)
        if years is None:
            continue
        names = _normalized_event_names(row)
        for candidate_id, (aliases, audit_years) in audits.items():
            if (
                years[0] <= audit_years[1]
                and years[1] >= audit_years[0]
                and names & aliases
            ):
                return row_id, candidate_id
    return None


def validate_wave8_vietnam_integration_dispositions(
    hced_rows: list[dict[str, Any]],
    iwbd_rows: list[dict[str, Any]],
    existing_events: Iterable[Mapping[str, Any]] = (),
) -> dict[str, int]:
    """Pin the reviewed HCED duplicate and negative IWBD/release scans."""

    validate_wave8_vietnam_queue_contracts(hced_rows)
    indexed: dict[str, list[dict[str, Any]]] = {}
    for row in hced_rows:
        indexed.setdefault(str(row.get("candidate_id") or ""), []).append(row)
    for candidate_id, disposition in WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS.items():
        related_id = str(disposition["related_hced_candidate_id"])
        for row_id, hash_key in (
            (candidate_id, "raw_row_sha256"),
            (related_id, "related_raw_row_sha256"),
        ):
            rows = indexed.get(row_id, [])
            if len(rows) != 1:
                raise ValueError(
                    f"{_LANE_NAME} expected one duplicate-review row {row_id}"
                )
            if canonical_hced_row_sha256(rows[0]) != disposition[hash_key]:
                raise ValueError(f"{_LANE_NAME} duplicate-review fingerprint changed")

    hced_overlap = _find_unreviewed_overlap(
        hced_rows,
        skip_candidate_ids=WAVE8_VIETNAM_RESERVED_IDS,
    )
    if hced_overlap:
        raise ValueError(
            f"{_LANE_NAME} found unreviewed cross-lane HCED twin "
            f"{hced_overlap[0]} for {hced_overlap[1]}"
        )
    iwbd_overlap = _find_unreviewed_overlap(iwbd_rows)
    if iwbd_overlap:
        raise ValueError(
            f"{_LANE_NAME} found plausible IWBD overlap "
            f"{iwbd_overlap[0]} for {iwbd_overlap[1]}"
        )
    release_overlap = _find_unreviewed_overlap(existing_events)
    if release_overlap:
        raise ValueError(
            f"{_LANE_NAME} found existing release duplicate "
            f"{release_overlap[0]} for {release_overlap[1]}"
        )
    return {
        "hced_duplicate_dispositions": len(
            WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS
        ),
        "iwbd_duplicate_dispositions": 0,
        "iwbd_zero_overlap_candidates": len(
            WAVE8_VIETNAM_IWBD_ZERO_OVERLAP_AUDIT
        ),
        "existing_release_duplicate_dispositions": 0,
    }


def install_wave8_vietnam_entities(
    release_entities: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_entities(
        release_entities,
        WAVE8_VIETNAM_ENTITIES,
        lane_name=_LANE_NAME,
    )


def install_wave8_vietnam_sources(
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    _validate_static()
    install_exact_sources(
        sources_by_id,
        WAVE8_VIETNAM_SOURCES,
        lane_name=_LANE_NAME,
    )


def _apply_location_quarantine_additions(events: list[dict[str, Any]]) -> None:
    for event in events:
        candidate_id = str(event["hced_candidate_id"])
        if candidate_id in WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS:
            event.pop("geometry", None)
        if candidate_id in WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS:
            event.pop("modern_location_country", None)
        if "geometry" not in event and "modern_location_country" not in event:
            event.pop("location_provenance", None)


def promote_wave8_vietnam_contracts(
    hced_rows: list[dict[str, Any]],
    release_entities: Mapping[str, Mapping[str, Any]],
    existing_events: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_wave8_vietnam_queue_contracts(hced_rows)
    events = promote_exact_hced_contracts(
        hced_rows,
        release_entities,
        existing_events,
        WAVE8_VIETNAM_CONTRACTS,
        lane_name=_LANE_NAME,
        event_id_prefix=_EVENT_ID_PREFIX,
    )
    _apply_location_quarantine_additions(events)
    return events


def wave8_vietnam_cohort_counts() -> dict[str, int]:
    _validate_static()
    return dict(
        sorted(
            Counter(
                str(contract["cohort"])
                for contract in WAVE8_VIETNAM_CONTRACTS.values()
            ).items()
        )
    )


def wave8_vietnam_counts() -> dict[str, int]:
    _validate_static()
    return {
        "country_quarantine_additions": len(
            WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS
        ),
        "greedy_eligible_rows": sum(
            bool(item["greedy_eligible"])
            for item in WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.values()
        ),
        "hced_duplicate_dispositions": len(
            WAVE8_VIETNAM_HCED_DUPLICATE_DISPOSITIONS
        ),
        "holds": len(WAVE8_VIETNAM_HOLDS),
        "integration_dispositions": len(WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS),
        "iwbd_duplicate_dispositions": len(
            WAVE8_VIETNAM_IWBD_DUPLICATE_DISPOSITIONS
        ),
        "new_entities": len(WAVE8_VIETNAM_ENTITIES),
        "new_sources": len(WAVE8_VIETNAM_SOURCES),
        "newly_rated_events": len(WAVE8_VIETNAM_CONTRACTS),
        "outcome_overrides": len(WAVE8_VIETNAM_OUTCOME_OVERRIDES),
        "point_quarantine_additions": len(
            WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS
        ),
        "promotion_contracts": len(WAVE8_VIETNAM_CONTRACTS),
        "reviewed_hced_rows": len(WAVE8_VIETNAM_RESERVED_IDS),
        "sole_blocker_promotions": sum(
            candidate_id in WAVE8_VIETNAM_CONTRACT_IDS
            and item["sole_blocker_label"] == "vietnam"
            for candidate_id, item in WAVE8_VIETNAM_INTEGRATION_DISPOSITIONS.items()
        ),
        "terminal_exclusions": len(WAVE8_VIETNAM_TERMINAL_EXCLUSIONS),
    }


def wave8_vietnam_location_quarantine_additions() -> dict[str, frozenset[str]]:
    """Return promoted-only location additions for coordinated integration."""

    _validate_static()
    return {
        "country": WAVE8_VIETNAM_COUNTRY_QUARANTINE_ADDITIONS,
        "point": WAVE8_VIETNAM_POINT_QUARANTINE_ADDITIONS,
    }
