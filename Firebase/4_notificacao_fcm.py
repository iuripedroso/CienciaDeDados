import firebase_admin
from firebase_admin import credentials, messaging
import firebase_admin.exceptions

# Inicializa o Firebase (evita inicialização dupla)
if not firebase_admin._apps:
    cred = credentials.Certificate("ccdados-firebase-adminsdk-fbsvc-e5d375e4d1.json")
    firebase_admin.initialize_app(cred)


def enviar_para_topico(topico: str, titulo: str, corpo: str):
    """
    Envia uma notificação para todos os dispositivos inscritos em um tópico.

    Args:
        topico : Nome do tópico FCM (sem barra inicial).
        titulo : Título da notificação.
        corpo  : Texto do corpo da notificação.
    """
    try:
        mensagem = messaging.Message(
            notification=messaging.Notification(title=titulo, body=corpo),
            topic=topico,
        )
        resposta = messaging.send(mensagem)
        print("Notificação enviada para tópico com sucesso!")
        print(f"  Tópico   : {topico}")
        print(f"  Título   : {titulo}")
        print(f"  Corpo    : {corpo}")
        print(f"  Resposta : {resposta}")

    except firebase_admin.exceptions.FirebaseError as e:
        print(f"Erro do Firebase ao enviar para tópico: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


def enviar_para_token(token: str, titulo: str, corpo: str):
    """
    Envia uma notificação diretamente para um dispositivo pelo token FCM.

    Args:
        token  : Token de registro do dispositivo.
        titulo : Título da notificação.
        corpo  : Texto do corpo da notificação.
    """
    try:
        mensagem = messaging.Message(
            notification=messaging.Notification(title=titulo, body=corpo),
            token=token,
        )
        resposta = messaging.send(mensagem)
        print("Notificação enviada para dispositivo com sucesso!")
        print(f"  Token    : {token[:20]}...")
        print(f"  Título   : {titulo}")
        print(f"  Corpo    : {corpo}")
        print(f"  Resposta : {resposta}")

    except firebase_admin.exceptions.FirebaseError as e:
        print(f"Erro do Firebase ao enviar para token: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    # --- Envio para tópico ---
    enviar_para_topico(
        topico="noticias",
        titulo="Nova atualização disponível!",
        corpo="Confira as novidades do sistema.",
    )

    print()

    # --- Envio para token (substitua pelo token real do dispositivo) ---
    TOKEN_TESTE = "SEU_TOKEN_DE_DISPOSITIVO_AQUI"
    enviar_para_token(
        token=TOKEN_TESTE,
        titulo="Olá, usuário!",
        corpo="Esta é uma notificação de teste.",
    )
