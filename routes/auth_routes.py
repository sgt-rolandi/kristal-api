from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from auth import verificar_senha, criar_token

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM usuarios WHERE username=?",
        (form_data.username,)
    ).fetchone()

    conn.close()

    if not user:
        raise HTTPException(401, "Usuário inválido")

    if not verificar_senha(form_data.password, user["password"]):
        raise HTTPException(401, "Senha inválida")

    token = criar_token(user["username"], user["role"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }