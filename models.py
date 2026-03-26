from fastapi import FastAPI
from database import init_db
from routes import auth_routes, pacientes, logs

app = FastAPI(title="KRISTAL API")

init_db()

app.include_router(auth_routes.router)
app.include_router(pacientes.router)
app.include_router(logs.router)


@app.get("/")
def home():
    return {"status": "KRISTAL API ONLINE"}