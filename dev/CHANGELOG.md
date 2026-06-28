# TagMatch — Change Log

Tracks bug fixes, cleanups, and corrections to existing functionality.

---

## [2026-06-28]

### Fixed
- **Profile.save() dedented out of class** — The `save()` method in `profiles/models.py` was accidentally defined at module level instead of inside the `Profile` class. This meant profile image auto-crop and resize (EXIF correction → square crop → 500×500) silently never ran. Re-indented into class body.

- **Home dashboard "latest matches" always empty** — `home()` in `tagmatch/views.py` was querying the `Match` table, which is never populated. Replaced with a live tag-overlap query (same logic as `matches_view`), limited to 5 results. Matches now actually appear on the dashboard.

- **Duplicate register views / broken registration** — Two `register()` views existed: one in `tagmatch/views.py` (broken — used wrong `height=` field, skipped first/last name) and one in `profiles/views.py` (correct). The active `/register/` URL pointed to the broken version. Removed the broken view, pointed `/register/` to the correct `profiles.views.register`, and removed the redundant `/profiles/register/` URL entry.

- **TimezoneMiddleware referencing nonexistent field** — `TimezoneMiddleware` in `tagmatch/middleware.py` referenced `profile.timezone`, which was never added to the Profile model. Removed the middleware from `MIDDLEWARE` in `settings.py`. Middleware file left in place for future use.

- **SECRET_KEY hardcoded in settings** — Moved `SECRET_KEY` and `DEBUG` to a `.env` file. `settings.py` now reads them via `os.environ.get()`. `.env` is already listed in `.gitignore`.

- **No pagination on matches and search** — `/matches/` and `/search/` loaded all results with no limit. Added Django `Paginator` at 20 results per page to both views and added prev/next pagination controls to both templates.

- **`home()` missing `@login_required`** — The home dashboard was accessible to unauthenticated users. Added decorator.

### Cleaned Up
- Removed duplicate `from messaging.models import Message` import in `tagmatch/views.py`
- Removed duplicate `path("edit/", views.edit_profile, name="edit_profile")` entry in `profiles/urls.py`
