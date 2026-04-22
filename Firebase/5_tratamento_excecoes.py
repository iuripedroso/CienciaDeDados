import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import exceptions as fb_exceptions

# Inicializa o Firebase (evita inicialização dupla)
if not firebase_admin._apps:
    cred = credentials.Certificate("ccdados-firebase-adminsdk-fbsvc-e5d375e4d1.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


def atualizar_preco_com_tratamento(produto_id: str, novo_preco: float):
    """
    Atualiza o preço de um produto com tratamento completo de exceções.

    Exceções tratadas:
        - ValueError          : argumentos inválidos (ID vazio, preço negativo).
        - NotFoundError       : documento inexistente no Firestore.
        - PermissionDeniedError: regras de segurança bloquearam a operação.
        - UnavailableError    : serviço Firebase temporariamente indisponível.
        - FirebaseError       : demais erros do SDK Firebase Admin.
        - Exception           : qualquer outro erro não previsto.
    """

    # --- Validações locais antes de chamar a API ---
    if not produto_id or not produto_id.strip():
        raise ValueError("O ID do produto não pode ser vazio.")
    if novo_preco < 0:
        raise ValueError(f"Preço inválido: {novo_preco}. Deve ser >= 0.")

    try:
        ref = db.collection("produtos_mysql").document(produto_id)
        doc = ref.get()

        if not doc.exists:
            print(f"[AVISO] Documento '{produto_id}' não existe na coleção.")
            return

        ref.update({"preco": novo_preco})
        print(f"[OK] Produto '{produto_id}' atualizado → R$ {novo_preco:.2f}")

    except fb_exceptions.NotFoundError as e:
        # Recurso não encontrado no Firebase (ex.: coleção inexistente)
        print(f"[ERRO - NotFound] Recurso não encontrado: {e}")

    except fb_exceptions.PermissionDeniedError as e:
        # Regras de segurança do Firestore bloquearam a operação
        print(f"[ERRO - PermissionDenied] Sem permissão para esta operação: {e}")
        print("  → Verifique as Firestore Security Rules no console.")

    except fb_exceptions.UnavailableError as e:
        # Serviço Firebase temporariamente fora do ar
        print(f"[ERRO - Unavailable] Serviço indisponível no momento: {e}")
        print("  → Tente novamente em alguns instantes.")

    except fb_exceptions.FirebaseError as e:
        # Captura genérica para qualquer outro erro do SDK
        print(f"[ERRO - Firebase] Código: {e.code} | Mensagem: {e}")

    except Exception as e:
        # Erros não relacionados ao Firebase (rede, I/O, etc.)
        print(f"[ERRO - Inesperado] {type(e).__name__}: {e}")


def buscar_produtos_com_tratamento(preco_minimo: float):
    """
    Consulta produtos acima de um preço com tratamento completo de exceções.
    """
    try:
        print(f"Consultando produtos com preço > R$ {preco_minimo:.2f}...\n")

        docs = (
            db.collection("produtos_mysql")
            .where("preco", ">", preco_minimo)
            .order_by("preco")
            .stream()
        )

        encontrados = 0
        for doc in docs:
            dados = doc.to_dict()
            print(f"  - {dados.get('nome', 'S/N')}: R$ {dados.get('preco', 0):.2f}")
            encontrados += 1

        print(f"\nTotal: {encontrados} produto(s) encontrado(s).")

    except fb_exceptions.FailedPreconditionError as e:
        # Geralmente indica que falta criar um índice composto no Firestore
        print(f"[ERRO - FailedPrecondition] Índice necessário ausente: {e}")
        print("  → Crie o índice indicado no link da mensagem de erro acima.")

    except fb_exceptions.FirebaseError as e:
        print(f"[ERRO - Firebase] Código: {e.code} | Mensagem: {e}")

    except Exception as e:
        print(f"[ERRO - Inesperado] {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("=== Teste de atualização com tratamento de exceções ===")
    atualizar_preco_com_tratamento("ID_DO_PRODUTO_AQUI", 19.90)

    print("\n=== Teste de consulta com tratamento de exceções ===")
    buscar_produtos_com_tratamento(15.00)

    print("\n=== Teste com valor inválido ===")
    try:
        atualizar_preco_com_tratamento("", -5.00)
    except ValueError as e:
        print(f"[CAPTURADO] ValueError: {e}")
