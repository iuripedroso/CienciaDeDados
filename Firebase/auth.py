import firebase_admin
from firebase_admin import credentials, auth

def inicializar_firebase():
    cred = credentials.Certificate("ccdados-firebase-adminsdk-fbsvc-e5d375e4d1.json")
    firebase_admin.initialize_app(cred)

def criar_usuario():
    try:
        user = auth.create_user(
            email="testeeeee@email.com",
            password="123456",
            display_name="Usuário Teste"
        )

        print("Usuário criado com sucesso!")
        print("UID:", user.uid)
        
        return user.uid

    except Exception as e:
        print("Erro ao criar usuário:", e)
        return None

def buscar_usuario(uid):
    try:
        user = auth.get_user(uid)

        print("\nDados do usuário:")
        print("UID:", user.uid)
        print("Email:", user.email)
        print("Nome:", user.display_name)
        print("Ativo:", not user.disabled)

    except Exception as e:
        print("Erro ao buscar usuário:", e)

if __name__ == "__main__":
    inicializar_firebase()
    
    uid = criar_usuario()
    
    if uid:
        buscar_usuario(uid)