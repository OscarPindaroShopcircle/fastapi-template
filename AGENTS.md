# Project Guidelines

## Frontend

See `docs/jinjax.md` for JinjaX usage and component conventions (argument passing, folder layout, CSS rules, layout shells, the showcase, and the M3 design system).

Key points:
- Components live in `src/frontend/components/<category>/<Name>.jinja` with colocated `<Name>.css`.
- All CSS values must reference design tokens from `src/frontend/static/css/main.css`.
- The showcase at `/components` (`pages.showcase.Showcase`) is the living style guide — add new components there when created.
- `docs/jinjax.md` documents the rules for creating components and passing arguments.
