import json

DATA_PATH = "data/clientes_mock.json"

def carregar_clientes():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_clientes(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def buscar_cliente(cpf):
    data = carregar_clientes()
    for cliente in data["clientes"]:
        if cliente["cpf"] == cpf:
            return cliente
    return None

def atualizar_cliente(cliente_atualizado):
    data = carregar_clientes()
    for i, cliente in enumerate(data["clientes"]):
        if cliente["cpf"] == cliente_atualizado["cpf"]:
            data["clientes"][i] = cliente_atualizado
    salvar_clientes(data)
