import os
import firebase_admin
from firebase_admin import credentials, storage
import firebase_admin.exceptions

# Inicializa o Firebase (evita inicialização dupla)
if not firebase_admin._apps:
    cred = credentials.Certificate("ccdados-firebase-adminsdk-fbsvc-e5d375e4d1.json")
    firebase_admin.initialize_app(cred, {
        # Substitua pelo nome real do seu bucket (sem "gs://")
        # Encontre em: Firebase Console > Storage > aba Files
        "storageBucket": "ccdados.appspot.com"
    })

def fazer_upload(caminho_local: str, destino_no_bucket: str):
    """
    Faz upload de um arquivo local para o Cloud Storage do Firebase.

    Args:
        caminho_local: Caminho do arquivo no computador.
        destino_no_bucket: Caminho de destino dentro do bucket.
    """
    try:
        bucket = storage.bucket()
        blob   = bucket.blob(destino_no_bucket)

        blob.upload_from_filename(caminho_local)

        # Torna o arquivo publicamente acessível (opcional)
        blob.make_public()

        print("Upload realizado com sucesso!")
        print(f"  Arquivo local : {caminho_local}")
        print(f"  Destino       : {destino_no_bucket}")
        print(f"  URL pública   : {blob.public_url}")

    except FileNotFoundError:
        print(f"Arquivo '{caminho_local}' não encontrado.")
    except firebase_admin.exceptions.FirebaseError as e:
        print(f"Erro do Firebase no upload: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def criar_arquivo_exemplo(nome: str = "meu_arquivo.txt"):
    """Cria um arquivo de texto simples para teste."""
    with open(nome, "w", encoding="utf-8") as f:
        f.write("Olá, Firebase Storage!")
    print(f"Arquivo '{nome}' criado localmente.")
    return nome


if __name__ == "__main__":
    arquivo = criar_arquivo_exemplo("meu_arquivo.txt")
    fazer_upload(arquivo, f"uploads/{arquivo}")
