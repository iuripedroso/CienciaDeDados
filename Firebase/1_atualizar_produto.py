import firebase_admin
from firebase_admin import credentials, firestore
import firebase_admin.exceptions

# Inicializa o Firebase (evita inicialização dupla)
if not firebase_admin._apps:
    cred = credentials.Certificate("ccdados-firebase-adminsdk-fbsvc-e5d375e4d1.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def atualizar_preco_produto(produto_id: str, novo_preco: float):
    """
    Atualiza o preço de um produto na coleção 'produtos_mysql' pelo ID do documento.

    Args:
        produto_id: ID do documento no Firestore.
        novo_preco: Novo valor do preço a ser definido.
    """
    try:
        ref = db.collection("produtos_mysql").document(produto_id)
        doc = ref.get()

        if not doc.exists:
            print(f"Produto com ID '{produto_id}' não encontrado.")
            return

        ref.update({"preco": novo_preco})
        print(f"Produto '{produto_id}' atualizado com sucesso!")
        print(f"  Novo preço: R$ {novo_preco:.2f}")

    except firebase_admin.exceptions.FirebaseError as e:
        print(f"Erro do Firebase ao atualizar produto: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    # Substitua pelo ID real do documento e o novo preço desejado
    atualizar_preco_produto("ID_DO_PRODUTO_AQUI", 29.90)
