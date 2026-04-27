from sqlalchemy import inspect, text

from app.database import engine


SQLITE_COLUMNS = {
    "customers": {
        "points_balance": "INTEGER DEFAULT 0",
        "lifetime_points": "INTEGER DEFAULT 0",
    },
    "sales": {
        "total_crc": "NUMERIC(12, 2) DEFAULT 0",
        "paid_total_crc": "NUMERIC(12, 2) DEFAULT 0",
        "change_amount_crc": "NUMERIC(12, 2) DEFAULT 0",
        "points_earned": "INTEGER DEFAULT 0",
        "points_redeemed": "INTEGER DEFAULT 0",
    },
    "payments": {
        "currency": "VARCHAR(3) DEFAULT 'CRC'",
        "exchange_rate": "NUMERIC(12, 4) DEFAULT 1",
        "amount_crc": "NUMERIC(12, 2) DEFAULT 0",
    },
    "business_settings": {
        "dark_mode": "BOOLEAN DEFAULT 0",
        "printer_name": "VARCHAR(120)",
        "ticket_size": "VARCHAR(10) DEFAULT '80mm'",
        "bccr_email": "VARCHAR(160)",
        "bccr_token": "VARCHAR(120)",
        "fallback_usd_crc_rate": "NUMERIC(12, 4) DEFAULT 520",
        "loyalty_crc_per_point": "NUMERIC(12, 2) DEFAULT 1000",
    },
}


def ensure_sqlite_columns() -> None:
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table, columns in SQLITE_COLUMNS.items():
            if table not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table)}
            for name, definition in columns.items():
                if name not in existing_columns:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))
