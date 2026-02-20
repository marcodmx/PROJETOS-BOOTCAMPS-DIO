from core.state_manager import atualizar_cliente

MAX_TENTATIVAS = 3

def gerar_proposta(cliente):
    valor_parcela = cliente["divida"] / cliente["parcelas_max"]
    return round(valor_parcela, 2)

def registrar_tentativa(cliente):
    cliente["tentativas"] += 1
    atualizar_cliente(cliente)

def pode_negociar(cliente):
    return cliente["tentativas"] < MAX_TENTATIVAS

def aceitar_proposta(cliente):
    cliente["status"] = "acordo_fechado"
    atualizar_cliente(cliente)
