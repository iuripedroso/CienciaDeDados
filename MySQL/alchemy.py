import sqlalchemy as sqla
import pandas as pd

engine = sqla.create_engine("sqlite:///alquimia.sqlite")
with engine.connect() as conn:
    conn.execute(
        sqla.text(
            """CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nome TEXT, idade INTEGER)"""
        )
    )
with engine.connect() as conn:
    conn.execute(
        sqla.text("""INSERT INTO usuarios ( nome, idade) VALUES ( 'Herich Gabriel', 25), ('Antonio Biava', 30)""")
    )
    conn.commit()

df = pd.read_sql_query("SELECT * FROM usuarios", engine)
print(df)