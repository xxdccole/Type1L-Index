# Type 1L Cement & Concrete Index

Static site for GitHub Pages: https://xxdccole.github.io/type1l-index/

`index.html` loads `data/site-data.json` in the browser and renders the page from that file. There is no build step and no dependencies. Edit the JSON, then commit and push to `main`.

## Data file

`data/site-data.json` is the only source of page content. The page prints these fields as written.

- `title` (string) — document title
- `summary` (string) — short summary in the header
- `summaryText` (string) — longer overview under the summary
- `lastUpdated` (string, `YYYY-MM-DD`) — header and footer date
- `whatsNew` (array) — objects with `date`, `title`, and `detail`. `date` is display text, not necessarily ISO.
- `topics` (array) — objects with:
  - `id` (string) — anchor (`#topic-<id>`) and topic-filter value
  - `name` (string)
  - `takeaways` (array of strings; may be empty)
  - `resourceIds` (array of resource ids, shown in this order)
- `keyIssues` (array of strings)
- `resources` (array) — objects with:
  - `id` (string), such as `R1`
  - `title`, `publisher`, `type` (strings)
  - `date` (string or `null`) — `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`. `null` is shown as undated and sorts last.
  - `url` (absolute `http` or `https` URL)
  - `topics` (array of topic ids)
- `gaps` (array of strings) — research gaps section
- `changeLog` (array) — objects with `date` (`YYYY-MM-DD`) and `entry`, listed in file order

Topic ids on a resource should match a topic `id`. A resource id in `resourceIds` should match a resource `id`.

Full dates (`YYYY-MM-DD`) in the header and change log are shown as a long English date. Resource dates and What's new dates are shown exactly as stored. Partial dates sort as the start of that year or month. Undated resources stay at the bottom of a date sort.

## Local preview

Opening `index.html` as a file will not load the JSON. From the repository root:

```bash
python3 -m http.server 8080
```

Then open http://127.0.0.1:8080/

## GitHub Pages

The site is the repository root. `.nojekyll` is present so Pages does not run Jekyll.

In the repository: **Settings → Pages → Build and deployment → Deploy from a branch → Branch `main`, folder `/ (root)` → Save.**

The public URL is https://xxdccole.github.io/type1l-index/
