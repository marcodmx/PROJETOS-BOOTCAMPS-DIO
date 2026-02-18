import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o motor
agente = AgenteNegociador()

def responder_negociacao(mensagem, historico, cpf):
    cliente = buscar_cliente_por_cpf(cpf)
    if not cliente:
        return "Olá! Por favor, informe um CPF válido para iniciarmos."
    
    return agente.responder(mensagem, str(cliente))

# Construção da Interface
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 RenovaIA - Agente Financeiro")
    
    with gr.Row():
        cpf_input = gr.Textbox(label="Identificação (CPF)", placeholder="000.000.000-00")
    
    chat = gr.ChatInterface(
        fn=responder_negociacao,
        additional_inputs=[cpf_input],
        type="messages"
    )

if __name__ == "__main__":
    # O tema é passado aqui para evitar o DeprecationWarning do Gradio 6.0
    demo.launch(share=True, theme=gr.themes.Soft())
