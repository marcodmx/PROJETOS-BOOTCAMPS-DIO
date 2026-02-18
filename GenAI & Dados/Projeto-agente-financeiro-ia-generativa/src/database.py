import json
import os

def carregar_dados():
    """Lê o arquivo JSON da base de conhecimento."""
    # Localiza o arquivo voltando uma pasta (de src para a raiz) e entrando em data
    caminho_base = os.path.join(os.path.dirname(__file__), '..', 'data', 'base_conhecimento.json')
    
    try:
        with open(caminho_base, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback para caso o arquivo não seja encontrado
        return {"clientes": []}

def buscar_cliente_por_cpf(cpf):
    """Busca um cliente específico ignorando formatação de pontos e traços."""
    if not cpf:
        return None
        
    dados = carregar_dados()
    # Limpa o CPF digitado (remove . e -)
    cpf_limpo = str(cpf).replace(".", "").replace("-", "").strip()
    
    for cliente in dados.get("clientes", []):
        # Limpa o CPF do banco para comparar
        cpf_banco = str(cliente["cpf"]).replace(".", "").replace("-", "").strip()
        if cpf_banco == cpf_limpo:
            return cliente
    return None
