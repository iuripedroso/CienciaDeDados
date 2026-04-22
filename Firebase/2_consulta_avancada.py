import firebase_admin
from firebase_admin import credentials, firestore
import firebase_admin.exceptions

# Inicializa o Firebase (evita inicialização dupla)
if not firebase_admin._apps:
    cred = credentials.Certificate("ccdados-firebase-adminsdk-fbsvc-e5d375e4d1.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def buscar_produtos_acima_do_preco(preco_minimo: float):
    """
    Consulta todos os produtos na coleção 'produtos_mysql' com preço
    superior ao valor informado e imprime seus nomes e preços.

    Args:
        preco_minimo: Valor de referência para filtrar os produtos.
    """
    try:
        print(f"Buscando produtos com preço acima de R$ {preco_minimo:.2f}...\n")

        query = (
            db.collection("produtos_mysql")
            .where("preco", ">", preco_minimo)
            .order_by("preco")
        )

        docs = query.stream()
        encontrados = 0

        for doc in docs:
            dados = doc.to_dict()
            nome  = dados.get("nome", "Sem nome")
            preco = dados.get("preco", 0)
            print(f"  - {nome}: R$ {preco:.2f}")
            encontrados += 1

        if encontrados == 0:
            print("Nenhum produto encontrado acima desse preço.")
        else:
            print(f"\nTotal encontrado: {encontrados} produto(s).")

    except firebase_admin.exceptions.FirebaseError as e:
        print(f"Erro do Firebase na consulta: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    buscar_produtos_acima_do_preco(15.00)
