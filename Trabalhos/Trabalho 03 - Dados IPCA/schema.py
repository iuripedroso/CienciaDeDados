import mysql.connector
from mysql.connector import Error


def conectar_mysql():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='NViuripedroso-6631034'
        )

        if conexao.is_connected():
            print("Conectado ao MySQL")
            return conexao

    except Error as e:
        print(f"Erro ao conectar: {e}")
        return None


def criar_database(conexao, nome_db):
    cursor = conexao.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nome_db}")
    print(f"Database '{nome_db}' pronto")


def usar_database(conexao, nome_db):
    cursor = conexao.cursor()
    cursor.execute(f"USE {nome_db}")


def criar_tabelas(conexao):
    cursor = conexao.cursor()

    tabela_usuarios = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100),
        email VARCHAR(100),
        idade INT,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(tabela_usuarios)
    print("Tabela 'usuarios' pronta")

    tabela_logs = """
    CREATE TABLE IF NOT EXISTS logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        acao VARCHAR(255),
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(tabela_logs)
    print("Tabela 'logs' pronta")


def inserir_usuario(conexao, nome, email, idade):
    cursor = conexao.cursor()
    sql = "INSERT INTO usuarios (nome, email, idade) VALUES (%s, %s, %s)"
    valores = (nome, email, idade)
    cursor.execute(sql, valores)
    conexao.commit()
    print("Usuário inserido com sucesso")


def consultar_dados(conexao, query):
    cursor = conexao.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    return resultados


def main():
    conexao = conectar_mysql()

    if conexao:
        nome_db = "meu_sistema"

        # Criar e usar banco
        criar_database(conexao, nome_db)
        usar_database(conexao, nome_db)

        # Criar tabelas
        criar_tabelas(conexao)

        # Inserir dados de teste
        inserir_usuario(conexao, "Iuri", "iuri@email.com", 20)
        inserir_usuario(conexao, "Maria", "maria@email.com", 25)

        # Consultar dados
        resultados = consultar_dados(conexao, "SELECT * FROM usuarios")

        print("\nDados da tabela usuarios:")
        for linha in resultados:
            print(linha)

        # Fechar conexão
        conexao.close()
        print("\nConexão encerrada")


if __name__ == "__main__":
    main()