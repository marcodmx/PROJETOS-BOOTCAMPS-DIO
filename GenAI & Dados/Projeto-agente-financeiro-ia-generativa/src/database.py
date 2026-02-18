import json
import os

def buscar_cliente_por_cpf(cpf_digitado):
    # Pega o caminho de onde este arquivo (database.py) está
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Monta o caminho para o JSON que está na pasta '../data/'
    # Isso sobe um nível (..) e entra na pasta data
    caminho_json = os.path.join(diretorio_atual, "..", "data", "base_conhecimento.json")
    
    try:
        if not os.path.exists(caminho_json):
            print(f"⚠️ Erro: Arquivo não encontrado em {caminho_json}")
            return None

        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Limpeza para evitar erros de digitação (remove pontos e traços)
        cpf_limpo = str(cpf_digitado).strip().replace(".", "").replace("-", "")
        
        for cliente in dados.get('clientes', []):
            cpf_banco = str(cliente.get('cpf', "")).strip().replace(".", "").replace("-", "")
            
            if cpf_banco == cpf_limpo:
                return cliente
                
    except Exception as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
    
    return None
