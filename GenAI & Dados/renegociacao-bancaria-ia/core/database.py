# core/database.py
import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, os.pardir, "data", "clientes_mock.json")

def carregar_base():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def buscar_cliente_por_cpf(cpf):
    dados = carregar_base()
    for cliente in dados.get("clientes", []):
        if "".join(filter(str.isdigit, cliente["cpf"])) == cpf:
            return cliente
    return None
