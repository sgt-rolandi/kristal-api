from fastapi import APIRouter, Depends
from database import get_db
from models import Paciente
from auth import get_user

router = APIRouter()

@router.post("/paciente")
def criar_paciente(p: Paciente, user=Depends(get_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO pacientes (precpc, prontuario, nome, graduacao, posto)
        VALUES (?, ?, ?, ?, ?)
    """, (p.precpc, p.prontuario, p.nome, p.graduacao, p.posto))

    conn.commit()
    conn.close()

    return {"msg": "Paciente criado"}


@router.get("/pacientes")
def listar_pacientes(user=Depends(get_user)):
    conn = get_db()
    cur = conn.cursor()

    dados = cur.execute("SELECT * FROM pacientes").fetchall()

    conn.close()

    return [dict(d) for d in dados]