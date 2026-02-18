import json
import os

def buscar_cliente_por_cpf(cpf_digitado):
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(diretorio_atual, "..", "data", "base_conhecimento.json")
    
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        cpf_limpo = str(cpf_digitado).strip().replace(".", "").replace("-", "")
        
        for cliente in dados.get('clientes', []):
            cpf_banco = str(cliente.get('cpf', "")).strip().replace(".", "").replace("-", "")
            if cpf_banco == cpf_limpo:
                return cliente
    except:
        return None
    return None
