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
    "4b47ac509695ed3eae88179e28626a607b347ead805f0bf81a37e8e68b87c6eb"
)
HCED_POINT_QUARANTINE_CANDIDATE_SHA256 = (
    "db361f319fd27e4e60b2a07cfa5d0675c6cde02d3e07108929d54c3dbe36e425"
)
HCED_COUNTRY_QUARANTINE_CANDIDATE_SHA256 = (
    "bbe783ce4b366d02c0b30634f054740aac2479e809029b2692d4a510ed377bd6"
)
HCED_POINT_QUARANTINE_EVENT_SHA256 = (
    "b785cb763178bd0390ca9b93defa8e0a203fe443f2b3c0e1160445a604c45138"
)
HCED_COUNTRY_QUARANTINE_EVENT_SHA256 = (
    "a8d96507bcbfef9498b8d8f1d5e8310e8eb7555832c928ded353adad26a5353c"
)
# Wave 5 is the immutable base to which reviewed lane manifests are added
# during release construction. The final pins below are independently measured
# from the coupled Wave 7 release/registry build and consumed by dashboard and
# coverage validation.
HCED_WAVE5_CANDIDATE_BINDINGS = 4_272
HCED_WAVE5_POINT_ASSERTIONS = 4_235
HCED_WAVE5_COUNTRY_ASSERTIONS = 4_192
HCED_WAVE5_PROVENANCE_OBJECTS = 4_239
HCED_EXPECTED_CANDIDATE_BINDINGS = 5_220
HCED_EXPECTED_CANDIDATE_KEYED_REVIEWED_CONTRACTS = 833
HCED_EXPECTED_POINT_ASSERTIONS = 4_819
HCED_EXPECTED_COUNTRY_ASSERTIONS = 5_125
HCED_EXPECTED_PROVENANCE_OBJECTS = 5_174
HCED_EXPECTED_QUARANTINE_UNION = 449
HCED_EXPECTED_QUARANTINE_OVERLAP = 46
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
    "hced-Abu Ageila1967-1",
    "hced-Aclea851-1",
    "hced-Afabet1988-1",
    "hced-Aghdash Awkh1831-1",
    "hced-Akhsikath1503-1",
    "hced-Akhulgo1839-1",
    "hced-Akroinos739-1",
    "hced-Alegria1834-1",
    "hced-Aleutians1942-1",
    "hced-Alexandria1365-1",
    "hced-Amida359-1",
    "hced-Amida502-503-1",
    "hced-Amritsar1634-1",
    "hced-Anandpur (2nd)1704-1",
    "hced-Andriba1895-1",
    "hced-Andros-245-1",
    "hced-Anil1886-1",
    "hced-Ansi-song645-1",
    "hced-Antelope Hills1858-1",
    "hced-Ap Bac1963-1",
    "hced-Apacheta1814-1",
    "hced-Arcadiopolis970-1",
    "hced-Arcot1780-1",
    "hced-Argos-272-1",
    "hced-Arnay-le-Duc1570-1",
    "hced-Arquijas1834-1",
    "hced-Arquijas1835-1",
    "hced-Ascalon1247-1",
    "hced-Asculum, Apulia-279-1",
    "hced-Ashdown871-1",
    "hced-Assab1991-1",
    "hced-Athens, Greece-264-1",
    "hced-Ati1978-1",
    "hced-Attu1943-1",
    "hced-Auneau1587-1",
    "hced-Aussa1875-1",
    "hced-Aussig1426-1",
    "hced-Avarayr451-1",
    "hced-Axholme1265-1",
    "hced-Ayacucho1824-1",
    "hced-Azua1844-1",
    "hced-Bach Dang1288-1",
    "hced-Bacolod1903-1",
    "hced-Bad Axe1832-1",
    "hced-Baddowal1846-1",
    "hced-Bagh Dera1788-1",
    "hced-Bagh1919-1",
    "hced-Baguashan1895-1",
    "hced-Balapur1720-1",
    "hced-Balkans1941-1",
    "hced-Balkans1944-1",
    "hced-Barentu1985-1",
    "hced-Battle Creek, Texas1838-1",
    "hced-Bayan1902-1",
    "hced-Bear Paw Mountains1877-1",
    "hced-Beaver Creek1868-1",
    "hced-Bedford1224-1",
    "hced-Belfast1900-1",
    "hced-Belfast1901-1",
    "hced-Beneventum-275-1",
    "hced-Bir Gafgafa1967-1",
    "hced-Birch Creek1878-1",
    "hced-Blackwater1598-1",
    "hced-Bobe1906-1",
    "hced-Bokhara1220-1",
    "hced-Bor Pansky1420-1",
    "hced-Bridge634-1",
    "hced-Brushy Creek1839-1",
    "hced-Buatachive1886-1",
    "hced-Bud Bagsak1913-1",
    "hced-Buffalo Wallow1874-1",
    "hced-Burtinah1839-1",
    "hced-Bytham1221-1",
    "hced-Callicinus-171-1",
    "hced-Calpulalpam1860-1",
    "hced-Campi Cannini457-1",
    "hced-Canyon Creek1877-1",
    "hced-Cao-Bang1950-1",
    "hced-Cape St Vincent1797-1",
    "hced-Carthage, Tunisia697-1",
    "hced-Cassel1328-1",
    "hced-Chacaltaya1814-1",
    "hced-Chalons366-1",
    "hced-Chesterfield1266-1",
    "hced-Chi Lang Pass1427-1",
    "hced-Chinese Farm1973-1",
    "hced-Clastidium-222-1",
    "hced-Clearwater1877-1",
    "hced-Clontarf1014-1",
    "hced-Clontibret1595-1",
    "hced-Coronea-447-1",
    "hced-Courtrai1302-1",
    "hced-Coutras1587-1",
    "hced-Craibstane1571-1",
    "hced-Crazy Woman Creek1876-1",
    "hced-Cremera-477-1",
    "hced-Crooked Creek1859-1",
    "hced-Ctesiphon363-1",
    "hced-Cumae-474-1",
    "hced-Cuzco1537-1",
    "hced-Damalcherry Pass1740-1",
    "hced-Damascus1925-1",
    "hced-Damghan1528-1",
    "hced-Darghiyya1842-1",
    "hced-Darghiyya1845-1",
    "hced-Day River1951-1",
    "hced-Dekemhare1990-1991-1",
    "hced-Delium-424-1",
    "hced-Derna1805-1",
    "hced-Dien Bien Phu1953-1",
    "hced-Dilam1902-1",
    "hced-Dong-Khe1950-1",
    "hced-Dong-do1426-1427-1",
    "hced-Dormans1575-1",
    "hced-Dorostalon971-1",
    "hced-Dove Creek1865-1",
    "hced-Dreux1562-1",
    "hced-Dublin (2nd)1171-1",
    "hced-Dufile1888-1",
    "hced-Dyle891-1",
    "hced-Dysert ODea1318-1",
    "hced-Edessa1144-1",
    "hced-Edessa1146-1",
    "hced-El Herri1914-1",
    "hced-El Numero1849-1",
    "hced-ElKsiba1913-1",
    "hced-Empress Augusta Bay1943-1",
    "hced-Etchoe1760-1",
    "hced-Etchoe1761-1",
    "hced-Fano271-1",
    "hced-Farnham893-1",
    "hced-Fatehpur1799-1",
    "hced-Focchies1649-1",
    "hced-Ford of the Biscuits1594-1",
    "hced-Freeman's Farm1776-1",
    "hced-Gaza1967-1",
    "hced-Gefrees1809-1",
    "hced-Gilbert Islands1943-1",
    "hced-Gimrah1832-1",
    "hced-Girgil1847-1",
    "hced-Gogra1529-1",
    "hced-Groenkloof1901-1",
    "hced-Guadalete711-1",
    "hced-Gujrat, Pakistan1797-1",
    "hced-Gulina1834-1",
    "hced-Gumburu1903-1",
    "hced-Gunib1859-1",
    "hced-Gurdas Nangal1715-1",
    "hced-Habry1422-1",
    "hced-Hanwella1803-1",
    "hced-Harenc1098-1",
    "hced-Hayfield Fight1867-1",
    "hced-Heraclea, Lucania-280-1",
    "hced-Herat1507-1",
    "hced-Herat1528-1",
    "hced-Herat1588-1",
    "hced-Hlophekhulu1888-1",
    "hced-Hofuf1913-1",
    "hced-Horice1423-1",
    "hced-Huayna Pucara1572-1",
    "hced-Huon Peninsula1943-1",
    "hced-Hyderabad, Pakistan1843-1",
    "hced-In Rhar1900-1",
    "hced-In Salah1900-1",
    "hced-Indus1221-1",
    "hced-Ingosten1899-1",
    "hced-Inverlochy1431-1",
    "hced-Issus-333-1",
    "hced-Ivuna1888-1",
    "hced-Iwo Jima1945-1",
    "hced-Jarnac1569-1",
    "hced-Jebel Libni1967-1",
    "hced-Junin1824-1",
    "hced-Kafr1925-1",
    "hced-Kagoshima1863-1",
    "hced-Kagul Lagoon1574-1",
    "hced-Kandy1803-1",
    "hced-Keelung1895-1",
    "hced-Keren1977-1978-1",
    "hced-Khenifra1914-1",
    "hced-Khiva1740-1",
    "hced-Khojend1220-1",
    "hced-Kickapoo Town1838-1",
    "hced-Kinzan1915-1",
    "hced-Komandorski Islands1943-1",
    "hced-Kota Bharu1941-1",
    "hced-Krak de Chevaliers1271-1",
    "hced-Kressenbrunn1260-1",
    "hced-Krusi1796-1",
    "hced-Kudarangan1904-1",
    "hced-Kumamoto1877-1",
    "hced-Kunduz2001-1",
    "hced-La Forbie1244-1",
    "hced-La Roche-LAbeille1569-1",
    "hced-La Rochelle1625-1",
    "hced-La Virgen1855-1",
    "hced-Ladoceia-227-1",
    "hced-Lake Benacus268-1",
    "hced-Lake Como-196-1",
    "hced-Lake Regillus-496-1",
    "hced-Lake Seit1903-1",
    "hced-Lake Smolino1502-1",
    "hced-Latrun (1st)1948-1",
    "hced-Latrun (2nd)1948-1",
    "hced-Lava Beds (1st)1873-1",
    "hced-Lava Beds (2nd)1873-1",
    "hced-Leuctra-371-1",
    "hced-Limerick1651-1",
    "hced-Limerick1922-1",
    "hced-Little Concho1862-1",
    "hced-Little Rock1870-1",
    "hced-Lizard1707-1",
    "hced-Lochaber1429-1",
    "hced-Lymans Wagon Train1874-1",
    "hced-Malala1905-1",
    "hced-Malta1798-1",
    "hced-Mantinea-207-1",
    "hced-Mantinea-362-1",
    "hced-Mao Khe1951-1",
    "hced-Marchfeld1278-1",
    "hced-Marqab1285-1",
    "hced-Martinici1796-1",
    "hced-Massawa1977-1",
    "hced-Massawa1990-1",
    "hced-Mazar-i-Sharif2001-1",
    "hced-Mazraa1925-1",
    "hced-Medina, Saudi Arabia1925-1",
    "hced-Megiddo-609-1",
    "hced-Merta1790-1",
    "hced-Merton871-1",
    "hced-Merv1510-1",
    "hced-Miani1843-1",
    "hced-Mincio-197-1",
    "hced-Mitla Pass1956-1",
    "hced-Mitla Pass1967-1",
    "hced-Mombasa1696-1698-1",
    "hced-Mome1906-1",
    "hced-Moncontour1569-1",
    "hced-Mons-en-Pevele1304-1",
    "hced-Montauban1621-1",
    "hced-Monte Suella1866-1",
    "hced-Montgisard1177-1",
    "hced-Montserrat1811-1",
    "hced-Monzon1809-1",
    "hced-Mopsuestia1152-1",
    "hced-Mount Barbosthene-192-1",
    "hced-Mount Tambor1740-1",
    "hced-Mpukonyoni1906-1",
    "hced-Mulaydah1891-1",
    "hced-Muong-Khoua1953-1",
    "hced-Muscat1650-1",
    "hced-N'Djamena1979-1",
    "hced-N'Djamena1980-1",
    "hced-Nakfa1977-1988-1",
    "hced-Nebovidy1422-1",
    "hced-Nemecky Brod1422-1",
    "hced-Neumarkt-St-Viet1809-1",
    "hced-Nghia Lo1951-1",
    "hced-Nghia Lo1952-1",
    "hced-Nile-47-1",
    "hced-Ningyuan1626-1",
    "hced-Nish1809-1",
    "hced-Niumaozhai1619-1",
    "hced-O'Connell Street1922-1",
    "hced-Ollantaytambo1537-1",
    "hced-Oomuli1560-1",
    "hced-Orthez1569-1",
    "hced-Otrar1219-1",
    "hced-Palo Duro1874-1",
    "hced-Pandosia-331-1",
    "hced-Parwan Durrah1221-1",
    "hced-Patan1790-1",
    "hced-Pavia271-1",
    "hced-Pearl Harbour1941-1",
    "hced-Perimeter (2nd)1950-1",
    "hced-Placentia271-1",
    "hced-Plum Creek, Nebraska1867-1",
    "hced-Plum Creek, Texas1840-1",
    "hced-Poitiers1569-1",
    "hced-Polotsk (2nd)1812-1",
    "hced-Poncha Pass1855-1",
    "hced-Porici1420-1",
    "hced-Port-au-Prince1803-1",
    "hced-Porto Praya1781-1",
    "hced-Pyongyang668-1",
    "hced-Qala-i-Jangi2001-1",
    "hced-Raab1044-1",
    "hced-Rabat-i-Pariyan1598-1",
    "hced-Rafa1967-1",
    "hced-Rahmaniyya1786-1",
    "hced-Raichur1520-1",
    "hced-Raor712-1",
    "hced-Rashaya1925-1",
    "hced-Ratanpur1720-1",
    "hced-Rawdhat al Muhanna1906-1",
    "hced-Red River1759-1",
    "hced-Rennell Island1943-1",
    "hced-Rhodes1310-1",
    "hced-Rhodes1480-1",
    "hced-Rhodes1522-1",
    "hced-Riade933-1",
    "hced-Riviera1944-1",
    "hced-Riyadh1902-1",
    "hced-Rochester1215-1",
    "hced-Rochester1264-1",
    "hced-Rock River1832-1",
    "hced-Rouen1562-1",
    "hced-Rush Springs1858-1",
    "hced-Sabalah1929-1",
    "hced-Sabana Larga1856-1",
    "hced-Sablat1619-1",
    "hced-Salaita1916-1",
    "hced-Salsu612-1",
    "hced-Samarkand1220-1",
    "hced-Samhud1799-1",
    "hced-Sampford Courtenay1549-1",
    "hced-San Saba1839-1",
    "hced-Sandfontein1914-1",
    "hced-Santa Rosa Island1861-1",
    "hced-Santa Rosa de Copan1856-1",
    "hced-Santo Domingo1805-1",
    "hced-Sarsa1704-1",
    "hced-Sas van Gent1644-1",
    "hced-Schonchin Flow1873-1",
    "hced-Sediman1798-1",
    "hced-Sellasia-222-1",
    "hced-Sendaigawa1587-1",
    "hced-Sens356-1",
    "hced-Shahdadpur1843-1",
    "hced-Shubra Khit1798-1",
    "hced-Sinkat1884-1",
    "hced-Skalice1424-1",
    "hced-Slaak1631-1",
    "hced-Smyrna1402-1",
    "hced-Solicinium368-1",
    "hced-Solomon Forks1857-1",
    "hced-Souk-Ahras1958-1",
    "hced-St Denis, France1567-1",
    "hced-St Jean dAngely1621-1",
    "hced-St Marys Clyst1549-1",
    "hced-St Pierre and Miquelon1793-1",
    "hced-St Thome1746-1",
    "hced-Strathfleet1453-1",
    "hced-Tabaruzaka1877-1",
    "hced-Takashiro1587-1",
    "hced-Tamatave1845-1",
    "hced-Tamatave1883-1",
    "hced-Tananarive1895-1",
    "hced-Tapae101-1",
    "hced-Tapae88-1",
    "hced-Tara980-1",
    "hced-Taraori1191-1",
    "hced-Taraori1192-1",
    "hced-Tatishchevo1774-1",
    "hced-Tegyra-375-1",
    "hced-Telamon-225-1",
    "hced-Teutoburgwald9-1",
    "hced-Thang Long1258-1",
    "hced-Thang Long1789-1",
    "hced-Thebes-335-1",
    "hced-Thessalonica1224-1",
    "hced-Tigranocerta-69-1",
    "hced-Toppenish1855-1",
    "hced-Tora Bora2001-1",
    "hced-Torata1823-1",
    "hced-Torbat-i-Jam1528-1",
    "hced-Toshimitsu1587-1",
    "hced-Tot-dong1426-1",
    "hced-Tripoli, Libya1551-1",
    "hced-Tristan de Cunha1815-1",
    "hced-Tsarasoatra1895-1",
    "hced-Turabah1919-1",
    "hced-Udayagiri1513-1514-1",
    "hced-Umm Urdhumah1929-1",
    "hced-Unayzah1904-1",
    "hced-Union Gap1855-1",
    "hced-Vaal Kranz1900-1",
    "hced-Veii-405-1",
    "hced-Vergt1562-1",
    "hced-Vertieres1803-1",
    "hced-Vijaya1471-1",
    "hced-Villa Glori1867-1",
    "hced-Vinegar Hill, Idaho1879-1",
    "hced-Vinh Yen1951-1",
    "hced-Vitkov Hill1420-1",
    "hced-Vladar1421-1",
    "hced-Vysehrad1420-1",
    "hced-Wake1941-1",
    "hced-Walkers Creek1844-1",
    "hced-Waterford1922-1",
    "hced-Waynesborough, Georgia1864-1",
    "hced-White Bird Canyon1877-1",
    "hced-White Mountain1620-1",
    "hced-White River1879-1",
    "hced-Whitehaven1778-1",
    "hced-Wisconsin Heights1832-1",
    "hced-Xiaoling1631-1",
    "hced-Zatec1421-1",
    "hced-Zhovnyne1638-1",
    "hced-Zieriksee1304-1",
    "hced-al, Damietta1218-1219-1",
)
HCED_COUNTRY_QUARANTINE_CANDIDATE_IDS = (
    "hced-Aghdash Awkh1831-1",
    "hced-Aleutians1942-1",
    "hced-Ap Bac1963-1",
    "hced-Argos-272-1",
    "hced-Atlantic1915-1917-1",
    "hced-Atlantic1939-1945-1",
    "hced-Attu1943-1",
    "hced-Augusta, Sicily1676-1",
    "hced-Aussa1875-1",
    "hced-Bagh Dera1788-1",
    "hced-Bagh1919-1",
    "hced-Balkans1941-1",
    "hced-Balkans1944-1",
    "hced-Belfast1900-1",
    "hced-Belfast1901-1",
    "hced-Bismarck1941-1",
    "hced-Burtinah1839-1",
    "hced-Campi Cannini457-1",
    "hced-Cape Engano1944-1",
    "hced-Cape St Vincent1797-1",
    "hced-Chieveley1899-1",
    "hced-Czernowitz1914-1",
    "hced-Czernowitz1916-1",
    "hced-Dogger Bank1781-1",
    "hced-Dogger Bank1915-1",
    "hced-Dufile1888-1",
    "hced-Empress Augusta Bay1943-1",
    "hced-Es Salt (1st)1918-1",
    "hced-Es Salt (2nd)1918-1",
    "hced-Fort Erie (2nd)1814-1",
    "hced-Fort Erie1812-1",
    "hced-Fort Erie1814-1",
    "hced-Freeman's Farm1776-1",
    "hced-Gilbert Islands1943-1",
    "hced-Glowworm1940-1",
    "hced-Gujrat, Pakistan1797-1",
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
    "hced-Mazraa1925-1",
    "hced-Mitla Pass1956-1",
    "hced-Montserrat1811-1",
    "hced-Monzon1809-1",
    "hced-Nemecky Brod1422-1",
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
    "hced-Rabat-i-Pariyan1598-1",
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
