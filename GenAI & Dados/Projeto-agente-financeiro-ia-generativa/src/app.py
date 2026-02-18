import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o motor da IA
agente = AgenteNegociador()

def responder_negociacao(mensagem, historico, cpf):
    """Função que conecta a interface ao cérebro da IA."""
    cliente = buscar_cliente_por_cpf(cpf)
    
    if not cliente:
        return "Para começarmos, por favor, insira um CPF cadastrado no campo acima."

    # Se achou o cliente, envia para o Gemini
    resposta = agente.responder(mensagem, str(cliente))
    return resposta

# Configuração da Interface Gradio (Versão Atualizada)
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 RenovaIA: Sistema de Renegociação Inteligente")
    
    cpf_field = gr.Textbox(
        label="Identificação (CPF)", 
        placeholder="Ex: 123.456.789-00"
    )
    
    # Removido 'retry_btn' para evitar o TypeError nas versões novas do Gradio
    chat = gr.ChatInterface(
        fn=responder_negociacao,
        additional_inputs=[cpf_field],
        examples=[["Quais são minhas dívidas?"], ["Quais as opções de parcelamento?"]]
    )

if __name__ == "__main__":
    # O tema 'Soft' agora é passado aqui ou deixado como padrão
    demo.launch(share=True)
