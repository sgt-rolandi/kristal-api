from fastapi import FastAPI

from app.api.routes_auth import router as auth_router
from app.api.routes_health import router as health_router
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User

app = FastAPI(
    title="KRISTAL API",
    version="1.0.0",
    description="API do sistema KRISTAL - Assistente Médico Militar",
)


Base.metadata.create_all(bind=engine)


def seed_admin() -> None:
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.username == "Kristal").first()
        if exists:
            return

        admin = User(
            username="Kristal",
            full_name="Administrador KRISTAL",
            password_hash=get_password_hash("@MasterKristal220416"),
            is_admin=True,
            is_active=True,
            posto="3º",
            graduacao="Sargento",
            especialidade="Administração do Sistema",
        )

        db.add(admin)
        db.commit()
    finally:
        db.close()


seed_admin()

app.include_router(health_router)
app.include_router(auth_router)