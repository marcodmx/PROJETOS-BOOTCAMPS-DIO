import gradio as gr
from core.cpf_validator import validar_cpf
from core.state_manager import buscar_cliente
from core.negotiation_engine import gerar_proposta, registrar_tentativa, pode_negociar, aceitar_proposta
from services.llm_adapter import gerar_resposta

def fluxo_negociacao(cpf, mensagem):
    if not validar_cpf(cpf):
        return "CPF inválido."

    cliente = buscar_cliente(cpf)
    if not cliente:
        return "Cliente não encontrado."

    if cliente["status"] == "acordo_fechado":
        return "Acordo já foi realizado anteriormente."

    if not pode_negociar(cliente):
        return "Limite de tentativas atingido. Procure a central de atendimento."

    proposta = gerar_proposta(cliente)
    registrar_tentativa(cliente)

    resposta_llm = gerar_resposta(
        f"Cliente deseja negociar dívida de R${cliente['divida']}. "
        f"Sistema permite {cliente['parcelas_max']} parcelas de R${proposta}."
        f"Mensagem do cliente: {mensagem}"
    )

    return f"Proposta: {cliente['parcelas_max']}x de R${proposta}\n\n{resposta_llm}"

def fechar_acordo(cpf):
    cliente = buscar_cliente(cpf)
    if cliente:
        aceitar_proposta(cliente)
        return "Acordo fechado com sucesso."
    return "Cliente não encontrado."

def criar_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Agente Inteligente de Renegociação Bancária")

        cpf = gr.Textbox(label="CPF")
        mensagem = gr.Textbox(label="Mensagem do Cliente")

        output = gr.Textbox(label="Resposta")

        btn_negociar = gr.Button("Negociar")
        btn_fechar = gr.Button("Fechar Acordo")

        btn_negociar.click(fluxo_negociacao, inputs=[cpf, mensagem], outputs=output)
        btn_fechar.click(fechar_acordo, inputs=cpf, outputs=output)

    return demo
