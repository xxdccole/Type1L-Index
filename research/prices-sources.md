# Price sources

Accessed 2026-11-27. This is the method note for `data/prices.json` and the `/prices/` page. It is not a claim that every public price series was found.

`scripts/fetch_prices.py` refreshes the API and workbook series and keeps ids stable. Hand-read figures live in `research/prices-curated.json` and are merged on each run. Sources that looked real but could not be read are in `research/prices-review.md`.

## What a row is

- **Unit value.** Dollars per ton at the mine or mill, as printed by USGS, unless the note says the figure was calculated from a printed quantity and value.
- **Bid price.** A state DOT awarded or average bid. The item includes placement, haul, and the rest of the specification. It is not a material-only price. Oklahoma splits pavement concrete from pavement placement; those rows say so.
- **List price.** An ENR city or 20-city quote. ENR says city quotes are single-source and may be list or transaction prices. Cement, block, and ready-mix quotes are delivered. Stone and sand quotes are FOB plant.
- **Index.** A BLS producer price index or the FHWA National Highway Construction Cost Index. The base period is on the row. An index is not a dollar price.

## U.S. Geological Survey

Mineral Commodity Summaries 2026, chapters opened as PDF:

- Cement, average mill unit value, 2021–2025. 2024 and 2025 are estimated. https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-cement.pdf
- Crushed stone, average unit value, 2021–2025. 2024 and 2025 are estimated. https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-stone-crushed.pdf
- Construction sand and gravel, average unit value, 2021–2025. 2024 and 2025 are estimated. https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-sand-gravel.pdf
- Iron and steel slag, average unit value of all types, free on board plant, 2021–2025. 2025 is estimated. The chapter says some ground granulated blast-furnace slag was about $140 per ton or more in 2025. That is a range statement, not a statistical average, so it is not its own row. https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-iron-steel-slag.pdf

Minerals Yearbook workbooks, downloaded and read as tables by the fetch script:

- Cement 2023, Table 1, national average shipment value for 2019 and 2020 (later years are the MCS rows). Table 11, portland and blended cement average value by shipping district, 2022 and 2023. Districts follow the reporting mills, not necessarily where the cement was sold. https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2023-cemen-ERT.xlsx
- Crushed stone 2023, Table 4, printed unit value by state, 2022 and 2023. https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2023-stonec-ert.xlsx
- Construction sand and gravel 2023, Table 3, printed unit value by state, 2022 and 2023. https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2023-sandc-ert.xlsx
- Iron and steel slag 2021, Table 1. The table prints quantity and value, not a unit value. Air-cooled, granulated, and steel-furnace rows are value divided by quantity. USGS marks those sales estimated. https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/myb1-2021-fesla-ert.xlsx

States withheld in the yearbook (`W`) are omitted. A source label of Other is kept as Other. Links to the yearbook files were taken from the USGS statistics pages for cement, crushed stone, construction sand and gravel, and iron and steel slag. On 2026-11-27 the cement statistics page still linked the 2023 yearbook workbook and did not link a 2024 workbook.

The August 2026 cement Mineral Industry Survey was opened (workbook `mis-202608-cemen.xlsx`, linked from the cement statistics page). Its tables are shipments by district and import customs values. It does not print a domestic mill unit value, so no row was added from it. September and October 2026 surveys were not on that page.

## Bureau of Labor Statistics

Monthly producer price indexes, not seasonally adjusted, from the public API `https://api.bls.gov/publicAPI/v2/timeseries/data/` for 2017 through 2026. No registration key. Preliminary months are flagged. The base date was read from the BLS series page.

Commodity indexes include hydraulic cement (WPU1322), construction sand, gravel and crushed stone (WPU1321), construction sand and gravel (WPU13210120) and its Northeast, Midwest, and West series, crushed and broken limestone (WPU13210122), concrete products (WPU133), concrete block and brick (WPU1331), ready-mix concrete (WPU1333) and the four Census regions, precast (WPU1334), prestressed (WPU1335), treated lightweight aggregate and crushed slag (WPU139902094), and dry-mixed concrete materials (WPU13990312).

Industry indexes include cement manufacturing (PCU327310327310), ready-mix concrete manufacturing (PCU327320327320), concrete block and brick manufacturing (PCU327331327331), other concrete product manufacturing (PCU327390327390), construction sand and gravel mining (PCU212321212321), and crushed and broken limestone mining (PCU212312212312).

The South construction-sand series WPU132101203 returned no observations for 2024–2026 and is not stored. The public API was asked again on 2026-11-27 and again returned no observations for 2024, 2025, or 2026. No commodity series was found for chemical admixtures, fly ash, or slag cement. PCU325998, other miscellaneous chemical product manufacturing, was looked up and not used, because it is not an admixture index. The 2026-11-27 refresh did not add a month past 2026-10, and it did not change a stored index value. The Midwest construction-sand series WPU132101202 still ends at 2026-09.

## Federal Reserve (FRED)

FRED republishes BLS producer price indexes and serves them as CSV without an API key, for example `https://fred.stlouisfed.org/graph/fredgraph.csv?id=WPU1322`. For 1990–2016, before the monthly BLS pull, the file stores the unweighted mean of the monthly values FRED published. The row says that. It is not a second measurement.

## FHWA NHCCI

Quarterly National Highway Construction Cost Index from `https://data.transportation.gov/api/views/r94d-n4f9/rows.csv?accessType=DOWNLOAD`. In that file, 2003 Q1 equals 1. Component columns are contributions to the index change, not material prices, and are not stored. The dataset page points to https://www.fhwa.dot.gov/policy/otps/nhcci/.

## State DOT bid prices

Files that were opened:

- Iowa DOT, Price Trend Index for Iowa Highway Construction, 2026 Q3 edition. Annual average awarded prices, 2000–2025, plus 2026 through the third quarter. PCC pavement is normalized to 9 inches. Structural concrete is a separate item. The composite index is 1987=100. https://iowadot.gov/media/2494/download?inline=
- Colorado DOT, Construction Cost Index report for the second quarter of 2025. Trailing-year weighted averages for concrete pavement (normalized to 9 inches) and structural concrete, from 2018. The report says outliers outside the 5th and 95th percentiles are removed. https://spl.cde.state.co.us/artemis/traserials/tra52010internet/tra520102025q2internet.pdf
- Oklahoma DOT item price history, 1 June 2021 through 30 November 2022. Statewide roll-ups for aggregate base, portland cement, fly ash, cement kiln dust, pavement concrete, and pavement placement. Thin items keep their occurrence counts in the description. https://www.odot.org/contracts/avgprices/eng221215.pdf
- Missouri DOT 2022 unit bid prices, Northwest District only, for 8-inch and 9-inch concrete pavement. https://modotweb.modot.mo.gov/BidLettingPlansRoom/Letting/ViewStream/3320?type=general_info

TxDOT, KDOT, and several other bid-price sites are listed in the review file because a number could not be read.

Files opened on 2026-11-27:

- Florida DOT, statewide 12-month historical item average cost, report run 2026-11-23, lettings from 2025-11-01 through 2026-10-31. Weighted average of awarded prices. Stored rows are plain cement concrete pavement at thicknesses with at least 1,000 square yards, optional base groups with at least 10 contracts, and concrete classes used for culverts, approach slabs, superstructure, or substructure with at least 5 contracts. The workbook has no portland-cement, fly-ash, or chemical-admixture pay item. https://www.fdot.gov/fpo/fpc/reports/historicalitemaveragecost
- Nebraska DOT, English average unit price for lettings from 2025-07-01 through 2026-06-30, printed 2026-06-18. Stored rows are the cement and fly-ash pay items, Class 47B-3500 concrete pavement at 8 through 13 inches where the quantity is at least 1,000 square yards (plain and doweled), box-culvert concrete, and bridge concrete. No chemical-admixture line was in the table. https://dot.nebraska.gov/media/53hgujhu/aup-july-2025-june-2026.pdf
- Colorado DOT, Construction Cost Index report for the third quarter of 2025, annual tabulation. The new rows are the 2025 Q3 trailing-year concrete pavement and structural concrete figures. Earlier trailing-year figures in that table match the rows already stored from the second-quarter 2025 report. The 2026 quarter reports are listed on the CDOT index page as OnBase document links. Those viewers did not yield a table, and the state-library PDF names for 2025 Q4 and 2026 Q1–Q3 returned 404. https://spl.cde.state.co.us/artemis/traserials/tra52010internet/tra520102025q3internet.pdf
- Missouri DOT, 2025 unit bid prices. The file has a section for each district and a statewide section. Stored rows are the statewide concrete-pavement items with at least 3,000 square yards and statewide Class B substructure concrete. The 2022 Northwest District rows already in the file were left as they were. https://modotweb.modot.mo.gov/BidLettingPlansRoom/Letting/ViewStream/3799?type=general_info

## ENR

Engineering News-Record, Construction Economics, the public PDF for the week of 3 August 2026. Opened and extracted with pdftotext. Stored figures are the 20-city averages, the August 2026 Construction Cost Index on the 1913 and 1967 bases, and the city quotes for portland cement, Type IL cement, masonry cement, crushed-stone base, concrete sand, and ready-mix at 3,000, 4,000, and 5,000 psi. A leading plus or minus in the city table means the quote rose or fell. The stored number is the price. The masonry-cement row is labeled both "70-lb bag" and "TON"; the printed unit is kept. https://www.enr.com/ext/resources/static_pages/Economics/2026/0803_CE_WK1_combined.pdf

The third-quarter 2026 cost-report PDF was opened. Its opening pages are a narrative and were not used for numbers. https://www.enr.com/ext/resources/Issues/National_Issues/2026/28-Sep/ENR09282026_3QCR_compressed.pdf

On 2026-11-27 the public economics topic page linked the November 9, November 16, and November 23 weekly PDFs. Those weeks are pipe, lumber, and steel, not cement. The November 2 week, which is the cement week, and the October 5 cement-week file both redirect to an ENR login. The November 2 article says the PDF requires a subscription. No price from those files was stored.

## Not in the file

NRMCA's performance benchmarking survey is for participating producers. The surveys page was opened again on 2026-11-27. No public ready-mix price table was on it. Home Depot and Lowe's product pages returned HTTP 403 again, so no bagged-cement shelf price is stored. No public chemical-admixture price list was opened. The Nebraska fly-ash pay item above is a state bid, not a national fly-ash price. Kansas DOT pages on ksdot.gov still returned HTTP 403, and the letting board at kdotapp.ksdot.org is proposal documents, not a weighted-average price table. The FHWA NHCCI download still ends at 2026 Q1.
