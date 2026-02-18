import gradio as gr
import datetime
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

agente = AgenteNegociador()

def obter_saudacao():
    hora = datetime.datetime.now().hour
    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def responder_negociacao(mensagem, historico, cpf):
    if not cpf or len(cpf) < 3:
        return "⚠️ Por favor, primeiro digite seu CPF no campo acima para que eu possa te reconhecer."
    
    cliente = buscar_cliente_por_cpf(cpf)
    if not cliente:
        return f"Olá! Não encontrei nenhum cadastro com o CPF informado ({cpf}). Pode conferir os números?"
    
    return agente.responder(mensagem, str(cliente))

# Customização visual com CSS
css = """
.gradio-container { background-color: #f8f9fa; }
#title { text-align: center; color: #2d3748; margin-bottom: 20px; }
"""

with gr.Blocks(css=css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 RenovaIA", elem_id="title")
    gr.Markdown(f"### ✨ {obter_saudacao()}! Sou seu assistente financeiro.")
    
    with gr.Row():
        cpf_input = gr.Textbox(
            label="📌 Digite seu CPF para começar", 
            placeholder="000.000.000-00",
            scale=2
        )
    
    gr.ChatInterface(
        fn=responder_negociacao,
        additional_inputs=[cpf_input],
        examples=[
            ["Quais são minhas dívidas em aberto?"],
            ["Quais as opções de parcelamento?"],
            ["Tenho direito a algum desconto à vista?"]
        ],
        description="Fale comigo sobre suas pendências e vamos encontrar a melhor solução juntos."
    )

if __name__ == "__main__":
    demo.launch(share=True)
