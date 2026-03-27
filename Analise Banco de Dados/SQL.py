import sqlite3 
import pandas as pd

con = sqlite3.connect('mydata.sqllite')

# Criar uma tabela
con.execute("""
            CREATE TABLE IF NOT EXISTS test (
            id INTEGER,
            nome TEXT
)""")

con.execute("INSERT INTO test (id, nome) VALUES (1, 'Ana')")
con.execute("INSERT INTO test (id, nome) VALUES (2, 'Bruno')")
