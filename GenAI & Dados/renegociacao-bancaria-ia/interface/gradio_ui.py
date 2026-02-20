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

    # --- MAPEAMENTO DE OPÇÕES NUMÉRICAS ---
    # Isso evita que a IA responda "não entendi" quando o usuário digita apenas o número
    opcoes = {
        "1": "Eu aceito a proposta de quitação à vista. Como procedo?",
        "2": "Eu aceito a proposta de parcelamento. Como procedo?",
        "3": "Não concordo com os valores. Gostaria de rejeitar as propostas e buscar outras opções.",
        "4": "Gostaria de tirar dúvidas ou saber mais detalhes antes de decidir."
    }
    
    # Se for um número mapeado, usamos o texto longo, senão usamos a mensagem original
    mensagem_para_ia = opcoes.get(mensagem.strip(), mensagem)

    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if not cliente:
        return historico, ""
    
    if historico is None:
        historico = []
    
    # 1. Prepara o histórico limpo para a API
    historico_ia = limpar_historico_para_ia(historico)

    try:
        # 2. Lógica de resposta baseada na mensagem processada
        if "🔍 Verificar Ofertas" in mensagem:
            comando = "Gere uma proposta de quitação à vista e uma de parcelamento"
            res = agente.responder(comando, str(cliente), historico_ia)
        elif "✅ Já efetuei o pagamento" in mensagem:
            res = "✍️ **Aviso de pagamento registrado!** O prazo para baixa bancária é de até 72h úteis. Guarde seu comprovante."
        elif "🚪 Encerrar" in mensagem:
            res = "A RenovaIA agradece seu contato. Sua sessão foi encerrada. Até breve! 👋"
        else:
            # Envia a mensagem (ou a opção mapeada) para a IA
            res = agente.responder(mensagem_para_ia, str(cliente), historico_ia)
            
        if not res:
            res = "Desculpe, não consegui processar sua solicitação agora. Pode repetir de outra forma?"

    except Exception as e:
        res = f"⚠️ Erro ao processar resposta: {str(e)}"
    
    # 3. Atualiza o histórico visual do Gradio
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
        # Tela de login
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="Informe seu CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR MEU PAINEL", variant="primary")
            status = gr.Markdown("")

        # Tela de chat
        with gr.Column(visible=False) as tela_chat:
            gr.Markdown("## 💬 Atendimento Digital")
            chatbot = gr.Chatbot(label="RenovaIA", height=550)
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Digite sua mensagem ou o número da opção...", scale=8, show_label=False)
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
