from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from enums import TipoMovimentacao  # Importando o Enum
from database import init_db, conn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/agendar", response_class=HTMLResponse)
def agendar_form(request: Request):
    return templates.TemplateResponse("agendar.html", {"request": request})

@app.post("/agendar", response_class=HTMLResponse)
def agendar(
    request: Request,
    nome: str = Form(...),
    especialidade: str = Form(...),
    data: str = Form(...),
    horario: str = Form(...)
):
    cursor = conn.cursor()

    # Verifica se já existe consulta no mesmo dia e horário
    cursor.execute("SELECT * FROM agendamentos WHERE data = ? AND horario = ?", (data, horario))
    existente = cursor.fetchone()

    if existente:
        return RedirectResponse("/erro", status_code=303)

    # valores fixos por especialidade
    valores = {
        "Nutricionista": 100.0,
        "Fisioterapia": 120.0,
        "Psicólogo": 150.0
    }

    cursor.execute("INSERT INTO agendamentos (nome, especialidade, data, horario) VALUES (?, ?, ?, ?)",
                   (nome, especialidade, data, horario))
    cursor.execute("INSERT INTO caixa (tipo, descricao, valor) VALUES (?, ?, ?)",
                   (TipoMovimentacao.ENTRADA.value, f"Consulta com {especialidade}", valores.get(especialidade, 0)))
    conn.commit()

    return RedirectResponse("/confirmacao", status_code=303)

@app.get("/confirmacao", response_class=HTMLResponse)
def confirmacao(request: Request):
    return templates.TemplateResponse("confirmacao.html", {"request": request})

@app.get("/erro", response_class=HTMLResponse)
def erro(request: Request):
    return templates.TemplateResponse("erro.html", {"request": request})

@app.get("/caixa", response_class=HTMLResponse)
def mostrar_caixa(request: Request):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caixa")
    caixa = cursor.fetchall()
    return templates.TemplateResponse("caixa.html", {"request": request, "caixa": caixa})

@app.post("/caixa", response_class=HTMLResponse)
def adicionar_ao_caixa(
    request: Request,
    tipo: TipoMovimentacao = Form(...),
    descricao: str = Form(...),
    valor: float = Form(...)
):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO caixa (tipo, descricao, valor) VALUES (?, ?, ?)", (tipo.value, descricao, valor))
    conn.commit()
    return RedirectResponse("/caixa", status_code=303)

@app.get("/listar", response_class=HTMLResponse)
def mostrar_relatorio(request: Request):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agendamentos")
    agendamentos = cursor.fetchall()
    return templates.TemplateResponse("listar.html", {"request": request, "agendamentos": agendamentos})

@app.get("/receita", response_class=HTMLResponse)
def mostrar_receita(request: Request):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caixa")
    caixa = cursor.fetchall()

    total_entrada = 0.0
    total_saida = 0.0

    for item in caixa:
        try:
            valor = float(item[3])
            tipo = item[1].lower()
            if tipo == TipoMovimentacao.ENTRADA.value:
                total_entrada += valor
            elif tipo == TipoMovimentacao.SAIDA.value:
                total_saida += valor
        except (ValueError, TypeError):
            continue

    saldo_final = total_entrada - total_saida

    return templates.TemplateResponse("receita.html", {
        "request": request,
        "caixa": caixa,
        "total_entrada": total_entrada,
        "total_saida": total_saida,
        "saldo_final": saldo_final
    })

@app.get("/limpar", response_class=HTMLResponse)
def limpar_dados(request: Request):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos")
    cursor.execute("DELETE FROM caixa")
    conn.commit()
    return templates.TemplateResponse("index.html", {"request": request})

