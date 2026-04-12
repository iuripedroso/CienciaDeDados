import sqlalchemy as sqla

engine = sqla.create_engine("sqlite:///novo_banco.sqllite")

with engine.connect() as conn:
    conn.execute(sqla.text("""
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """))   