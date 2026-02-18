import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o motor da IA (que está no engine.py)
agente = AgenteNegociador()

def responder_negociacao(mensagem, historico, cpf):
    """Função que conecta a interface ao cérebro da IA."""
    # 1. Tenta localizar o cliente
    cliente = buscar_cliente_por_cpf(cpf)
    
    if not cliente:
        return "Para começarmos, por favor, insira um CPF cadastrado no campo acima para que eu possa localizar sua conta."

    # 2. Se achou o cliente, envia a dúvida + dados do cliente para o Gemini
    # Passamos o dicionário do cliente como string para o prompt
    resposta = agente.responder(mensagem, str(cliente))
    return resposta

# Configuração da Interface Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 RenovaIA: Sistema de Renegociação Inteligente")
    gr.Markdown("Olá! Sou o assistente virtual do Banco Renova. Informe seu CPF e vamos regularizar sua situação.")
    
    with gr.Row():
        cpf_field = gr.Textbox(
            label="Identificação (CPF)", 
            placeholder="Ex: 123.456.789-00",
            scale=1
        )
    
    # O ChatInterface gerencia o histórico e a caixa de mensagem automaticamente
    chat = gr.ChatInterface(
        fn=responder_negociacao,
        additional_inputs=[cpf_field],
        examples=[["Quais são minhas dívidas?"], ["Quais as opções de parcelamento?"]],
        retry_btn="Tentar Novamente",
        clear_btn="Limpar Conversa"
    )

if __name__ == "__main__":
    # share=True gera o link público temporário (ótimo para o Colab)
    demo.launch(share=True)
