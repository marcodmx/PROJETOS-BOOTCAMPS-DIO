import gradio as gr
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

# Inicializa o motor de negociação
agente = AgenteNegociador()

# CSS moderno para o portal
MEU_CSS = """
.gradio-container { background-color: #f7fafc !important; }
.main-header { text-align: center; color: #2c5282; font-weight: bold; margin-bottom: 10px; }
"""

# ==========================================================
# Funções auxiliares
# ==========================================================
def formatar_historico(historico_gradio):
    """
    O historico_gradio agora já vem como uma lista de dicionários.
    Esta função garante que o AgenteNegociador receba o formato que ele espera.
    """
    return historico_gradio

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Gradio moderno: o 'historico' já é uma lista de dicts [{'role': '...', 'content': '...'}]
    if not cliente:
        return historico, ""
    
    # 1. Adiciona a mensagem do usuário ao histórico
    historico.append({"role": "user", "content": mensagem})

    # 2. Lógica de resposta
    if "🔍 Verificar Ofertas" in mensagem:
        comando = "Gere uma proposta de quitação à vista e uma de parcelamento"
        res = agente.responder(comando, str(cliente), historico)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso de pagamento registrado!** O prazo para baixa bancária é de até 72h úteis. Guarde seu comprovante."
    elif "🚪 Encerrar" in mensagem:
        res = "A RenovaIA agradece seu contato. Sua sessão foi encerrada. Até breve! 👋"
    else:
        res = agente.responder(mensagem, str(cliente), historico)
    
    # 3. Adiciona a resposta da IA ao histórico
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        # FORMATO CORRETO: Lista de dicionários
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor virtual RenovaIA. Como posso ajudar com sua saúde financeira hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado. Tente novamente."

# ==========================================================
# Função principal de criação da interface
# ==========================================================
def criar_interface():
    with gr.Blocks(title="RenovaIA", css=MEU_CSS) as demo:
        # Tela de login
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="Informe seu CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR MEU PAINEL", variant="primary")
            status = gr.Markdown("")

        # Tela de chat
        with gr.Column(visible=False) as tela_chat:
            gr.Markdown("## 💬 Atendimento Digital")
            # type="messages" é o segredo para usar o formato novo de dicts
            chatbot = gr.Chatbot(label="RenovaIA", height=550, type="messages")
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Digite sua mensagem...", scale=8, show_label=False)
                btn_send = gr.Button("Enviar", variant="primary", scale=2)
            
            gr.Examples(
                examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar"], 
                inputs=txt_msg,
                label="Ações Rápidas"
            )

        # Ações dos botões
        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

    return demo
