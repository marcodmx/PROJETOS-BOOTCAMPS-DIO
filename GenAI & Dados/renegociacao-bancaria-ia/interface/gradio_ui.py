import gradio as gr
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

# Inicializa o motor de negociação
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if not cliente:
        return historico, ""
    
    # 1. O histórico agora deve ser tratado como lista de dicionários
    # Se o histórico vier vazio, garantimos que seja uma lista
    if historico is None:
        historico = []

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
    
    # 3. ADICIONANDO NO FORMATO OBRIGATÓRIO (Dicionários)
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        # FORMATO OBRIGATÓRIO: Lista de dicionários desde a mensagem inicial
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor virtual RenovaIA. Como posso ajudar?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado."

def criar_interface():
    # Removido o parâmetro 'css' daqui para o launch() no app.py
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA")
            cpf_input = gr.Textbox(label="Informe seu CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR MEU PAINEL", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            gr.Markdown("## 💬 Atendimento Digital")
            # IMPORTANTE: No Gradio atual, ele detecta o formato pelo conteúdo enviado
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
