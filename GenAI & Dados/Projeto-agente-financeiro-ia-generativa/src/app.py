import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o cérebro da IA
agente = AgenteNegociador()

def responder_negociacao(mensagem, historico, cpf):
    """
    Função principal que o Gradio chama a cada mensagem.
    """
    # Consulta o banco de dados JSON
    cliente = buscar_cliente_por_cpf(cpf)
    
    if not cliente:
        return "Olá! Para iniciarmos sua consulta, por favor insira um CPF válido acima."

    # Gera a resposta usando a IA
    resposta = agente.responder(mensagem, str(cliente))
    return resposta

# Interface moderna usando Blocks
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 RenovaIA - Agente Financeiro")
    gr.Markdown("Bem-vindo ao portal de renegociação. Identifique-se para começar.")
    
    with gr.Row():
        cpf_input = gr.Textbox(
            label="Seu CPF", 
            placeholder="Ex: 123.456.789-00",
            scale=1
        )
    
    # Interface de chat com padrão de mensagens moderno
    chat = gr.ChatInterface(
        fn=responder_negociacao,
        additional_inputs=[cpf_input],
        type="messages",
        examples=[["Quais são minhas pendências?"], ["Quero um desconto para pagar à vista."]]
    )

if __name__ == "__main__":
    # share=True gera o link público no Colab
    demo.launch(share=True)
