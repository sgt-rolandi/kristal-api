from pyngrok import ngrok
import uvicorn

# abre o túnel
public_url = ngrok.connect(8000)
print("🔥 URL pública:", public_url)

# inicia o backend
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)