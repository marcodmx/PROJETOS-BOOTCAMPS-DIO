import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Tratamento para opções de encerramento rápido
    if "Já efetuei o pagamento" in mensagem:
        res = "🌟 **Excelente notícia!** Ficamos muito felizes. Agora, basta aguardar o prazo de compensação bancária (até 3 dias úteis). Guarde seu comprovante com carinho. Posso ajudar em algo mais?"
    elif "Encerrar Atendimento" in mensagem:
        res = "Obrigado por confiar na **RenovaIA**. Sua jornada para uma vida financeira saudável continua. Tenha um ótimo dia! 👋"
    else:
        res = agente.responder(mensagem, str(cliente))
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

# CSS para botões profissionais
css = r"""
.btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; }
.btn-success { background: #2f855a !important; color: white !important; }
.btn-outline { border: 1px solid #cbd5e0 !important; background: white !important; }
"""

with gr.Blocks(css=css) as demo:
    # (Mantenha a lógica de tela_login e tela_chat que já estabilizamos)
    
    with gr.Column(visible=False) as tela_chat:
        gr.Markdown("## 🏦 Portal de Negociação RenovaIA")
        chatbot = gr.Chatbot(label="Atendimento", height=450, type="messages")
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua mensagem...", show_label=False, scale=7)
            btn_send = gr.Button("Enviar", variant="primary", elem_classes="btn-banco", scale=2)
            
        # Opções Padrão Profissionais (Aparecem como sugestões de clique)
        gr.Examples(
            examples=[
                "✅ Já efetuei o pagamento", 
                "📱 Receber boleto no WhatsApp", 
                "🚪 Encerrar Atendimento"
            ],
            inputs=txt_msg,
            label="Ações Rápidas"
        )
        
        with gr.Row():
            btn_copy = gr.Button("📋 Copiar Código", elem_classes="btn-outline")
            btn_ajuda = gr.Button("❓ Preciso de Ajuda", elem_classes="btn-outline")

    # (Eventos de click/submit mantendo o padrão que deu certo)
