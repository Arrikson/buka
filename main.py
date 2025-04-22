from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from hashlib import sha256
import shutil, os, json

app = FastAPI()
UPLOAD_DIR = "comprovativos"
DB_FILE = "comprovantes.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Carregar comprovantes já usados
def carregar_comprovantes():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

# Salvar novo comprovante
def salvar_comprovante(hash_comprovativo):
    dados = carregar_comprovantes()
    dados.append(hash_comprovativo)
    with open(DB_FILE, "w") as f:
        json.dump(dados, f)

@app.post("/upload")
async def upload_comprovativo(comprovativo: UploadFile = File(...)):
    content = await comprovativo.read()

    if comprovativo.content_type != "application/pdf":
        return HTMLResponse("<h3>❌ Apenas arquivos PDF são permitidos.</h3>")

    if len(content) > 32 * 1024:
        return HTMLResponse("<h3>❌ O comprovativo excede 32 KB.</h3>")

    # Verificar se já foi enviado (com base no hash SHA-256)
    hash_do_arquivo = sha256(content).hexdigest()
    comprovantes = carregar_comprovantes()

    if hash_do_arquivo in comprovantes:
        return HTMLResponse("<h3>⚠️ Este comprovativo já foi utilizado.</h3>")

    # Salvar comprovativo e registrar hash
    caminho = os.path.join(UPLOAD_DIR, comprovativo.filename)
    with open(caminho, "wb") as f:
        f.write(content)

    salvar_comprovante(hash_do_arquivo)

    return HTMLResponse("<h3>✅ Comprovativo enviado com sucesso! Aguarde a confirmação.</h3>")
