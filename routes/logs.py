from fastapi import APIRouter, Depends
from database import get_db
from auth import get_user, admin_only

router = APIRouter()

@router.get("/logs")
def ver_logs(user=Depends(get_user)):
    admin_only(user)

    conn = get_db()
    cur = conn.cursor()

    dados = cur.execute("SELECT * FROM logs ORDER BY id DESC").fetchall()

    conn.close()

    return [dict(d) for d in dados]