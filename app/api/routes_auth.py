from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, decode_token
from app.models.user import User
from app.services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str
    is_admin: bool
    posto: str | None = None
    graduacao: str | None = None
    especialidade: str | None = None


class MeResponse(BaseModel):
    username: str
    full_name: str
    is_admin: bool
    posto: str | None = None
    graduacao: str | None = None
    especialidade: str | None = None


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(
        db,
        payload.username.strip(),
        payload.password.strip(),
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
        )

    token = create_access_token(
        {
            "sub": user.username,
            "is_admin": user.is_admin,
            "full_name": user.full_name,
        }
    )

    return TokenResponse(
        access_token=token,
        username=user.username,
        full_name=user.full_name,
        is_admin=user.is_admin,
        posto=user.posto,
        graduacao=user.graduacao,
        especialidade=user.especialidade,
    )


@router.get("/me", response_model=MeResponse)
def me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    return MeResponse(
        username=user.username,
        full_name=user.full_name,
        is_admin=user.is_admin,
        posto=user.posto,
        graduacao=user.graduacao,
        especialidade=user.especialidade,
    )