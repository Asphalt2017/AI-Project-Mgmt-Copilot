# Configuring the web app

The first web version is a read-only MVP preview with Overview, Requirements,
Implementation, and Decisions pages. Navigation, page content, and sample records
come from [`tests/settings/settings.yaml`](../tests/settings/settings.yaml).
Search, status filters, and expandable details work without a database or API keys.
The supplied data is illustrative; external ingestion and approval workflows are
not implemented yet.

## Run locally

From the repository root:

```bash
uv sync --locked
APP_SETTINGS=tests/settings/config.yaml uv run uvicorn ai_copilot.main:create_app_from_settings_file --factory --reload --host 127.0.0.1
```

Open <http://127.0.0.1:8000/>. Restart the server after changing YAML; the default
Uvicorn reload configuration watches Python files, not YAML.

An explicit settings path overrides the default:

```bash
APP_SETTINGS=tests/settings/config.yaml uv run uvicorn ai_copilot.main:create_app_from_settings_file --factory --host 127.0.0.1
```

Set `web_settings_file` in the selected settings YAML to point at another page
configuration file. Relative paths resolve against the directory containing that
settings YAML.

## YAML format

```yaml
version: 1
name: AI Delivery Copilot
workspace: Product engineering
notice: "Demo workspace · Sample content only."
home: overview
pages:
  - slug: overview
    label: Overview
    title: Our delivery workspace
    description: Follow intent through delivery.
    kind: overview
  - slug: requirements
    label: Requirements
    title: Shared intent
    description: Review the work and its boundaries.
    kind: collection
    empty_message: No requirements yet.
    records:
      - key: DEMO-101
        title: An illustrative requirement
        summary: A short description shown in the list.
        status: Draft
        owner: Product team
        detail: Additional context shown when the item is expanded.
```

- `version` must be `1`. `name`, `workspace`, and `notice` are required plain text.
- `home` identifies a page slug. `/` redirects to that page.
- `pages` controls navigation order and supports 1–30 pages. Add or remove entries
  to change the app without editing Python.
- `slug` becomes `/<slug>`. It must start with a lowercase letter and contain only
  lowercase letters, digits, or hyphens, up to 64 characters. Slugs must be unique;
  `health`, `docs`, `redoc`, and `static` are reserved.
- `label`, `title`, and `description` are required for every page.
- `kind: overview` displays counts and links for all collection pages. Overview
  pages cannot contain records.
- `kind: collection` is the default. `records` defaults to an empty list, with an
  optional `empty_message`. Record keys must be unique within a page.
- Each record requires `key`, `title`, `summary`, `status`, `owner`, and `detail`.
  Text fields are 1–2,000 characters. Status filter options are derived from records.
- Search matches key, title, summary, owner, and detail without case sensitivity.
  Search and status filters combine and use GET parameters, so filtered URLs can
  be bookmarked. They do not change the YAML or underlying records.

YAML is parsed with `safe_load` and validated at startup. Missing files, malformed
YAML, unknown fields, invalid slugs, and inconsistent home pages stop startup.
HTML in configuration and search input is escaped. Page entries cannot select
Python modules, templates, scripts, or arbitrary file paths. Keep credentials in
the local environment, not in page configuration.

## Implementation

`ai_copilot/web/config.py` owns the typed schema and loader. `pages.py` creates
per-application routes. Shared Jinja templates render the navigation, overview,
collections, and a page-not-found screen. CSS and templates are packaged assets;
the UI makes no CDN requests and needs no JavaScript for its current interactions.

The preview supports no write operations. Baseline acceptance and decision
recording must be added with authentication, durable persistence, and provenance.
