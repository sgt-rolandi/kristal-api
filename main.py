from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import sqlite3
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security

# =========================
# CONFIG
# =========================

SECRET_KEY = os.getenv("SECRET_KEY", "KRISTAL_SECRET_2026")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="KRISTAL API")
security = HTTPBearer()

# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect("kristal.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # PACIENTES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        preccp TEXT,
        prontuario TEXT,
        nome TEXT,
        graduacao TEXT,
        posto TEXT
    )
    """)

    # ATENDIMENTOS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        descricao TEXT,
        militar_nome TEXT,
        militar_posto TEXT,
        militar_graduacao TEXT,
        data TEXT
    )
    """)

    # LOGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        acao TEXT,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# MODELOS
# =========================

class Usuario(BaseModel):
    username: str
    password: str
    role: str = "medico"

class Paciente(BaseModel):
    preccp: str
    prontuario: str
    nome: str
    graduacao: str
    posto: str

class Atendimento(BaseModel):
    paciente_id: int
    descricao: str
    militar_nome: str
    militar_posto: str
    militar_graduacao: str

# =========================
# SEGURANÇA
# =========================

def tratar_senha(senha: str):
    return senha.encode("utf-8")[:72].decode("utf-8", "ignore")

def hash_senha(senha: str):
    senha = tratar_senha(senha)
    return pwd_context.hash(senha)

def verificar_senha(senha: str, hash: str):
    senha = tratar_senha(senha)
    return pwd_context.verify(senha, hash)

def criar_token(username, role):
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    return verificar_token(token)

def admin_only(user):
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

# =========================
# LOG
# =========================

def log(usuario, acao):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO logs (usuario, acao, data) VALUES (?, ?, ?)",
        (usuario, acao, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

# =========================
# ROTAS
# =========================

@app.get("/")
def health():
    return {"status": "KRISTAL API ONLINE"}

# =========================
# AUTH
# =========================

@app.post("/register")
def register(user: Usuario):
    if user.role not in ["medico", "admin"]:
        raise HTTPException(status_code=400, detail="Role inválida")

    conn = get_db()
    cur = conn.cursor()

    senha_hash = hash_senha(user.password)

    try:
        cur.execute(
            "INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)",
            (user.username, senha_hash, user.role)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    conn.close()

    return {"msg": "Usuário criado"}

@app.post("/login")
def login(user: Usuario):
    conn = get_db()
    cur = conn.cursor()

    db_user = cur.execute(
        "SELECT * FROM usuarios WHERE username=?",
        (user.username,)
    ).fetchone()

    conn.close()

    if not db_user:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    if not verificar_senha(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Senha inválida")

    token = criar_token(user.username, db_user["role"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# =========================
# PACIENTES
# =========================

@app.post("/paciente")
def criar_paciente(p: Paciente, user=Depends(get_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO pacientes (preccp, prontuario, nome, graduacao, posto)
    VALUES (?, ?, ?, ?, ?)
    """, (p.preccp, p.prontuario, p.nome, p.graduacao, p.posto))

    conn.commit()
    conn.close()

    log(user["sub"], f"CRIAR PACIENTE {p.nome}")

    return {"msg": "Paciente criado"}

@app.get("/pacientes")
def listar_pacientes(user=Depends(get_user)):
    conn = get_db()
    cur = conn.cursor()

    dados = cur.execute("SELECT * FROM pacientes").fetchall()

    conn.close()

    log(user["sub"], "LISTAR PACIENTES")

    return [dict(d) for d in dados]

# =========================
# ATENDIMENTO
# =========================

@app.post("/atendimento")
def atendimento(a: Atendimento, user=Depends(get_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO atendimentos (
        paciente_id, descricao, militar_nome,
        militar_posto, militar_graduacao, data
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        a.paciente_id,
        a.descricao,
        a.militar_nome,
        a.militar_posto,
        a.militar_graduacao,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    log(user["sub"], f"ATENDIMENTO PACIENTE {a.paciente_id}")

    return {"msg": "Atendimento registrado"}

# =========================
# LOGS (ADMIN)
# =========================

@app.get("/logs")
def ver_logs(user=Depends(get_user)):
    admin_only(user)

    conn = get_db()
    cur = conn.cursor()

    dados = cur.execute(
        "SELECT * FROM logs ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return [dict(d) for d in dados]