# Branchlane Page

Public landing, guide, developer docs, pricing, privacy, and EULA reference pages for Branchlane.

- Landing Page: `https://bbdyno.github.io/Branchlane-Page/`
- Korean Landing Page: `https://bbdyno.github.io/Branchlane-Page/ko/`
- Pricing: `https://bbdyno.github.io/Branchlane-Page/pricing/`
- Korean Pricing: `https://bbdyno.github.io/Branchlane-Page/ko/pricing/`
- Guide and help: `https://bbdyno.github.io/Branchlane-Page/guide/` (Korean: `/ko/guide/`)
- Notes (Korean): `https://bbdyno.github.io/Branchlane-Page/ko/notes/`
- Developer docs: `https://bbdyno.github.io/Branchlane-Page/developers/` (Korean: `/ko/developers/`)
- App Store: `https://apps.apple.com/app/id6785129372`
- Privacy Policy: `https://bbdyno.github.io/Branchlane-Page/privacy/`
- Terms of Use (EULA): `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`
- EULA Reference Page: `https://bbdyno.github.io/Branchlane-Page/terms/`
- Sitemap: `https://bbdyno.github.io/Branchlane-Page/sitemap.xml` (submit it in Google Search Console under the `https://bbdyno.github.io/` property)

The guide, developer docs and notes are built from `_docs/`. Edit a file there, then:

```bash
python3 _tools/build_docs.py
python3 _tools/build_docs.py --check
```

The builder also writes `sitemap.xml` and the search index. GitHub Pages leaves out folders that start with `_`. Pages it builds must not be edited by hand.

GitHub Pages is served from the `main` branch root.

The App Store download badge is loaded unchanged from Apple's official Marketing Tools endpoint. Do not recreate, translate, crop, animate, or recolor it.
