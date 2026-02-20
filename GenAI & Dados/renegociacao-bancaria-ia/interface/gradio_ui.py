import gradio as gr
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

# Inicializa o motor de negociação
agente = AgenteNegociador()

# CSS moderno
MEU_CSS = """
.gradio-container { background-color: #f7fafc !important; }
.main-header { text-align: center; color: #2c5282; font-weight: bold; margin-bottom: 10px; }
"""

# ==========================================================
# Funções auxiliares
# ==========================================================
def limpar_historico_para_ia(historico_gradio):
    """
    Filtra apenas role e content para evitar erro de metadata na Groq.
    """
    if not historico_gradio:
        return []
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in historico_gradio
        if "role" in msg and "content" in msg
    ]

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem:
        return historico, ""

    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if not cliente:
        return historico, ""
    
    if historico is None:
        historico = []
    
    # 1. Limpa o histórico atual para enviar para a IA
    historico_ia = limpar_historico_para_ia(historico)

    try:
        # 2. Lógica de resposta baseada na mensagem
        if "🔍 Verificar Ofertas" in mensagem:
            comando = "Gere uma proposta de quitação à vista e uma de parcelamento"
            res = agente.responder(comando, str(cliente), historico_ia)
        elif "✅ Já efetuei o pagamento" in mensagem:
            res = "✍️ **Aviso de pagamento registrado!** O prazo para baixa bancária é de até 72h úteis. Guarde seu comprovante."
        elif "🚪 Encerrar" in mensagem:
            res = "A RenovaIA agradece seu contato. Sua sessão foi encerrada. Até breve! 👋"
        else:
            # Resposta genérica da IA (incluindo pedidos de boleto)
            res = agente.responder(mensagem, str(cliente), historico_ia)
            
        if not res:
            res = "Desculpe, não consegui gerar uma resposta. Pode tentar reformular?"

    except Exception as e:
        res = f"⚠️ Erro na IA: {str(e)}"
    
    # 3. Atualiza o histórico para o Gradio exibir (IMPORTANTE: Ordem User -> Assistant)
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor virtual RenovaIA. Como posso ajudar com sua saúde financeira hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado. Tente novamente."

# ==========================================================
# Função principal de criação da interface
# ==========================================================
def criar_interface():
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="Informe seu CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR MEU PAINEL", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            gr.Markdown("## 💬 Atendimento Digital")
            # Sem o parâmetro type="messages" para evitar o TypeError que deu antes
            chatbot = gr.Chatbot(label="RenovaIA", height=550)
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Digite sua mensagem...", scale=8, show_label=False)
                btn_send = gr.Button("Enviar", variant="primary", scale=2)
            
            gr.Examples(
                examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar"], 
                inputs=txt_msg,
                label="Ações Rápidas"
            )

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

    return demo
