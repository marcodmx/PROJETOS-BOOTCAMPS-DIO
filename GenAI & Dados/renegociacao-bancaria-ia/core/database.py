import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# Caminho para o seu JSON na pasta 'data'
DB_PATH = os.path.join(BASE_PATH, os.pardir, "data", "clientes_mock.json")

def carregar_base():
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Retorno de segurança caso o arquivo suma
        return {"clientes": []}

def buscar_cliente_por_cpf(cpf):
    # Garante que estamos comparando apenas números
    cpf_busca = "".join(filter(str.isdigit, str(cpf)))
    dados = carregar_base()
    
    for cliente in dados.get("clientes", []):
        cpf_cliente = "".join(filter(str.isdigit, cliente.get("cpf", "")))
        if cpf_cliente == cpf_busca:
            return cliente
    return None
