import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o motor
agente = AgenteNegociador()

def responder_negociacao(mensagem, historico, cpf):
    # Busca os dados no banco de dados JSON
    cliente = buscar_cliente_por_cpf(cpf)
    
    if not cliente:
        return "Olá! Por favor, insira um CPF válido para começarmos nossa conversa."

    # Envia a pergunta do usuário e os dados do cliente para a IA
    resposta = agente.responder(mensagem, str(cliente))
    return resposta

# Interface Gradio Moderna
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 RenovaIA: Sistema de Negociação com IA")
    
    with gr.Row():
        cpf_input = gr.Textbox(
            label="Digite seu CPF para consulta", 
            placeholder="Ex: 123.456.789-00"
        )
    
    # type="messages" é o padrão atual que evita o UserWarning
    chat = gr.ChatInterface(
        fn=responder_negociacao,
        additional_inputs=[cpf_input],
        type="messages",
        title="Chat de Negociação",
        examples=[["Quais dívidas eu tenho?"], ["Posso parcelar no boleto?"]]
    )

if __name__ == "__main__":
    demo.launch(share=True)
