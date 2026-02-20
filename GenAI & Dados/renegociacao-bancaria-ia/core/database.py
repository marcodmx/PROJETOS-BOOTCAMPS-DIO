import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, os.pardir, "data", "clientes_mock.json")

def carregar_base():
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"clientes": [], "configuracoes_gerais": {}}

def buscar_cliente_por_cpf(cpf):
    cpf_busca = "".join(filter(str.isdigit, str(cpf)))
    dados = carregar_base()
    
    for cliente in dados.get("clientes", []):
        cpf_json = "".join(filter(str.isdigit, cliente.get("cpf", "")))
        if cpf_json == cpf_busca:
            return cliente
    return None
