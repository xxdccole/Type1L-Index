# Price leads that could not be read

Checked 2026-11-26. Same idea as `research/review-retry.md`: these look like real price sources, but this pass could not read a figure from them. They are not observations.

- **Home Depot, Quikrete 94-lb portland cement.** Product page returned HTTP 403 to this client. https://www.homedepot.com/p/Quikrete-94-lb-Portland-Cement-112494/100318511
- **Lowe's, Quikrete 94-lb portland cement.** Product page returned HTTP 403. https://www.lowes.com/pd/Quikrete-94-lb-Gray-Portland-Cement/3004735
- **NRMCA Performance Benchmarking Survey.** The association says the report is available only to producers that participate. No public price table was opened. https://www.nrmca.org/association-resources/nrmca-surveys-benchmarking/
- **TxDOT bid item averages.** The public page describes a Tableau dashboard of average bid prices for the past 24 months. The dashboard did not yield a readable table of concrete or aggregate unit prices in this pass. https://www.txdot.gov/business/road-bridge-maintenance/contract-letting/bid-items-and-index.html
- **Kansas DOT weighted average bid prices and the prequalified-materials page.** Requests to ksdot.gov returned HTTP 403, including the prequalified materials page stored on the DOT list page. No bid price was read. https://www.ksdot.gov/doing-business/highway-contractors/contractor-resources/prequalified-materials-and-new-product-approval/prequalified-materials-and-material-sources
- **PCA / American Cement Association price or economic reports.** No open price table was found. Member and paid reports were not bypassed.
- **BLS South construction sand and gravel, WPU132101203.** The public API returned no observations for 2024–2026. The Northeast, Midwest, and West series are in the dataset.
- **Chemical admixtures.** No BLS commodity series for water reducers, air entrainers, retarders, or accelerators was identified. The industry index for miscellaneous chemical products was not used, because it is not an admixture price.
- **Fly ash and slag cement, national dollars.** USGS prices slag types, not fly ash. The only fly-ash dollar figure stored is one small Oklahoma DOT bid. No open national fly-ash or slag-cement price list was read.
- **Ready-mix supplier price sheets.** No supplier sheet was found that was both public and readable without an account.
- **ENR weekly history before August 2026.** The economics archive says earlier weeks are public PDFs. Only the 3 August 2026 weekly file was extracted. https://www.enr.com/economics/current_costs
- **Nebraska and Nevada bid-price averages.** NDOT in the task could be either state. Nebraska and Nevada qualified-product pages were found. A current weighted-average bid table for concrete pavement was not opened for either state in this pass.
- **KDOT, MoDOT statewide, and ODOT (Oklahoma) files newer than the ones stored.** Missouri is in the dataset only for the 2022 Northwest District table that was opened. Oklahoma is the 2021–2022 item-price history that was opened. A newer statewide file was not read.
