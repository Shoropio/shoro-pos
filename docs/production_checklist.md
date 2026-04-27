# Shoro POS Production Checklist

## Before Launch

- Set a strong `SECRET_KEY` and do not reuse development values.
- Configure backups for `database/shoro_pos.db` or use PostgreSQL for multi-terminal deployments.
- Run `pytest -q` and `npm run build` before each release.
- Run migrations with Alembic when schema changes are introduced.
- Use `docker compose up --build` for a reproducible local production-like run.
- CI is configured in `.github/workflows/ci.yml` for backend tests and frontend builds.
- Configure BCCR credentials or set a reviewed fallback USD/CRC rate.
- Validate Hacienda CR sandbox with real certificates before enabling production fiscal mode.
- Verify ticket printing on the target 58mm/80mm printer.

## Operational Controls

- Create named users for each cashier.
- Review role permissions in `/users/roles`.
- Restrict `pos.apply_discount_50`, `products.import`, and `users.manage`.
- Close each cash shift and reconcile differences daily.
- Export/import tests should be performed on a backup before bulk changes.
- Generate a SQLite backup with `.\scripts\backup_sqlite.ps1` before deployments and mass imports.

## Fiscal Controls

- Keep `fiscal_cr` isolated from the sale flow so sales remain offline-capable.
- Queue fiscal documents as pending when Hacienda is unavailable.
- Keep signed XML, generated XML, Hacienda responses, and fiscal logs.
