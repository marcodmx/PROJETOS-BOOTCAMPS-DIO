import gradio as gr
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

MEU_CSS = """
.gradio-container { background-color: #f7fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #2c5282; font-weight: 800; font-size: 24px; padding: 20px; }
"""

def limpar_historico_para_ia(historico_gradio):
    if not historico_gradio: return []
    # Filtra apenas o conteúdo essencial para a API
    return [{"role": m["role"], "content": m["content"]} for m in historico_gradio if "role" in m and "content" in m]

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem:
        return historico, ""

    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if historico is None: historico = []
    historico_ia = limpar_historico_para_ia(historico)

    try:
        # A IA interpreta a intenção e decide sobre o boleto
        res = agente.responder(mensagem, str(cliente), historico_ia)
        
        # Reforço visual de empatia se houver fechamento/boleto (identificado pelas crases ```)
        if "```" in res:
            if "📧" not in res:
                res += "\n\n📧 **Acabei de enviar o boleto completo e o comprovante para o seu e-mail.**\n\nFique tranquilo, agora é com a gente. Vai dar tudo certo! 😊 🙌"

    except Exception as e:
        res = f"🤔 Algo deu errado por aqui. Vamos tentar de novo? (Erro: {str(e)})"
    
    # No Gradio 5.x, o histórico já funciona como lista de dicts por padrão, 
    # basta não usar o argumento 'type' no componente.
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"👋 Oi, {nome}! Sou seu consultor RenovaIA.\n\nEstou aqui para te ajudar a resolver suas pendências de um jeito simples e sem burocracia. Vamos ver o que conseguimos hoje? ✨"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado. Tente novamente, por favor."

def criar_interface():
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="Digite seu CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("CONFERIR MINHAS OPÇÕES", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            gr.Markdown("## ✨ Atendimento Personalizado")
            # REMOVIDO o type="messages" para evitar o TypeError
            chatbot = gr.Chatbot(label="Consultor Digital", height=500)
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Digite sua mensagem ou escolha uma opção...", scale=8, show_label=False)
                btn_send = gr.Button("Enviar", variant="primary", scale=2)
            
            gr.Examples(
                examples=["🔍 Quais são minhas ofertas?", "Aceito a quitação à vista", "✅ Já paguei"], 
                inputs=txt_msg,
                label="Sugestões"
            )

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

    return demo
