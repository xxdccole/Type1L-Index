# Type IL Cement & Concrete Index

A curated index of standards, research, DOT specifications, field guidance and news on Type IL portland-limestone cement (ASTM C595 / AASHTO M 240).

Live site: https://xxdccole.github.io/Type1L-Index/

GitHub Pages paths are case-sensitive. The address above is the working one. The same address in lowercase returns 404.

## How it works

`data/site-data.json` is the only source of content. `scripts/build.py` validates it and writes static HTML, so the pages work without JavaScript and search engines can read them.

| Generated file | Purpose |
| --- | --- |
| `index.html` | Home page with every resource in a searchable table |
| `topics/<id>/index.html` | One page per topic |
| `sitemap.xml`, `llms.txt` | Crawler and AI-assistant discovery |
| `feed-daily.xml`, `feed-weekly.xml` | One digest entry per finished day or week, for email services and feed readers |
| `feed.xml` | The 100 newest resources, one entry each |

Do not edit the generated files by hand. Edit the JSON, then:

```bash
python3 scripts/build.py          # validate, then build
python3 scripts/build.py --validate   # validate only
python3 scripts/check_site.py     # links, anchors, ids, canonicals, JSON-LD, feeds
python3 -m http.server 8080       # preview at http://127.0.0.1:8080/
```

On GitHub, `.github/workflows/build.yml` runs the same steps on every push that touches `data/`, `scripts/`, `css/` or `js/`, and once a day. It commits the generated files back to `main`. Pages serves `main` from the repository root, as before.

## Data file

`data/site-data.json` fields:

- `title`, `summary`, `summaryText` (strings)
- `lastUpdated` (`YYYY-MM-DD`). Must equal the date of the last `changeLog` entry.
- `whatsNew` (array): `date` (display text), `title`, `detail`
- `topics` (array): `id` (lowercase slug), `name`, `takeaways` (strings, may be empty), `resourceIds` (display order)
- `resources` (array): `id`, `title`, `publisher`, `type`, `date`, `added`, `url`, `topics`
  - `type` starts with a capital letter. Two labels that differ only by case fail validation.
  - `date` is the publication date: `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or `null` when no source date is known. Never use placeholders such as `"-"`.
  - `added` is the day the resource was added to the index (`YYYY-MM-DD`). The digest feeds are built from it.
  - `url` is an absolute `http(s)` URL.
- `keyIssues`, `gaps` (arrays of strings)
- `changeLog` (array): `date` (`YYYY-MM-DD`), `entry`, in date order

Validation fails the build when a resource is tagged with a topic that does not list it (or the reverse), when ids, URLs or titles repeat, or when a date does not fit the formats above.

## Site settings

`data/site-config.json`:

- `baseUrl`: the public address, with a trailing slash. Change it here, and only here, if the site moves.
- `verification.google`, `verification.bing`: the codes from Search Console and Bing Webmaster Tools.
- `indexNowKey`: matches the key file `<key>.txt` in the repository root. Do not delete that file.
- `newsletter`: see below.

## Getting found

Done in the site itself: static HTML for every page, one canonical address per page, titles and descriptions, Open Graph and Twitter tags, structured data (schema.org JSON-LD), `sitemap.xml`, `llms.txt`, Atom feeds, and an IndexNow ping for Bing, Yandex and similar engines after each data change.

Steps that need your accounts:

1. Add the site as a URL-prefix property in Google Search Console, copy the HTML-tag verification code into `verification.google`, push, then verify.
2. Submit `https://xxdccole.github.io/Type1L-Index/sitemap.xml` in Search Console. Then import the property into Bing Webmaster Tools.
3. Link to the site from places that already rank for these topics. Backlinks matter more than any setting here.

Limits you should know about:

- Search engines read `robots.txt` only at the root of a host. A project page cannot set one, so there is none.
- Nobody can guarantee that "everyone in the world" finds a site, and ranking depends on other sites linking to it.
- A custom domain would give a permanent address that survives a repository rename. It is a decision for you, because it costs money.

## Email newsletter

A static site cannot send email, so the signup form posts to an email service. The form is built and tested. It stays hidden until you point it at a service:

1. Create an account with an email service that offers a hosted signup endpoint. Buttondown's embed form is documented to accept a POST to `https://buttondown.com/api/emails/embed-subscribe/<your-username>` with an `email` field and a hidden `tag` field. MailerLite's RSS campaigns offer daily and weekly digests, listed as a premium feature with a 14-day trial.
2. In `data/site-config.json` set `newsletter.enabled` to `true` and `newsletter.formAction` to the service's endpoint. Add any fixed fields the service needs to `hiddenFields` (for Buttondown, `{"embed": "1"}`). The radio buttons send `weekly` or `daily` in the field named by `frequencyField`.
3. In the service, create two RSS-to-email automations: one on `feed-daily.xml` for people tagged `daily`, one on `feed-weekly.xml` for people tagged `weekly`. Set sends for the morning, after the 06:20 UTC build. Whether a given service can limit an RSS automation to one tag or group is not confirmed. Check this first when you create the automations.
4. Set the sender name and the postal address the service puts in every email footer. Use an address you are willing to publish.

Until then the page shows links to the daily, weekly and newest-resources feeds.

## Local checks

`scripts/check_site.py` needs no packages. A headless-browser test of search, filters, sorting, shareable links, no-JavaScript rendering and the signup form was run against this version. It is not in the repository because it needs Playwright.
