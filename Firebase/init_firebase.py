import firebase_admin
from firebase_admin import credentials

def inicializar_firebase():
    try:
        caminho_credenciais = "ccdados-firebase-adminsdk-fbsvc-e5d375e4d1.json"
        cred = credentials.Certificate(caminho_credenciais)
        app = firebase_admin.initialize_app(cred)
        
        print("Firebase inicializado com sucesso!")
        print("Nome do app:", app.name)
        
    except Exception as e:
        print("Erro ao inicializar Firebase:", e)

if __name__ == "__main__":
    inicializar_firebase()