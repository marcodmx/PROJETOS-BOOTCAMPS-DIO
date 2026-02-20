import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

TITULOS_IA = [
    "✨ Sua Nova Jornada Financeira",
    "🚀 Rumo à sua Liberdade Financeira",
    "🤝 Vamos transformar seu futuro?",
    "🌱 Semeando sua Saúde Financeira"
]

MEU_CSS = """
.gradio-container { background-color: #f8fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #1e293b; font-weight: 800; font-size: 28px; padding: 20px; }
.action-btn { font-weight: 600 !important; }
.footer-info { text-align: center; color: #64748b; font-size: 12px; margin-top: 20px; }
"""

def limpar_historico_para_ia(historico_gradio):
    if not historico_gradio: return []
    return [{"role": m["role"], "content": m["content"]} for m in historico_gradio if "role" in m]

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem: return historico, ""
    
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if historico is None: historico = []
    historico_ia = limpar_historico_para_ia(historico)

    try:
        res = agente.responder(mensagem, str(cliente), historico_ia)
        if "```" in res and "📧" not in res:
            res += "\n\n📧 **Boleto enviado para seu e-mail.** Vai dar tudo certo! 😊 🙌"
    except Exception as e:
        res = f"🤔 Tive um probleminha. Pode repetir? (Erro: {str(e)})"
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg = [{"role": "assistant", "content": f"👋 Olá, {nome}! Como posso facilitar seu dia hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado."

def encerrar_sessao():
    return gr.update(visible=True), gr.update(visible=False), None, ""

def criar_interface():
    titulo_sessao = random.choice(TITULOS_IA)
    
    with gr.Blocks(title="RenovaIA", css=MEU_CSS) as demo:
        # TELA DE LOGIN
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            with gr.Row():
                with gr.Column(scale=1):
                    cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
                    btn_entrar = gr.Button("ACESSAR PAINEL", variant="primary")
                    status = gr.Markdown("")

        # TELA DE CHAT (DASHBOARD)
        with gr.Column(visible=False) as tela_chat:
            with gr.Row():
                gr.Markdown(f"## {titulo_sessao}")
                btn_sair = gr.Button("🚪 Sair", variant="stop", size="sm", scale=0)

            with gr.Row():
                # Coluna do Chat (Esquerda)
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(label="Consultor RenovaIA", height=450)
                    with gr.Row():
                        txt_msg = gr.Textbox(placeholder="Fale comigo...", scale=8, show_label=False)
                        btn_send = gr.Button("Enviar", variant="primary", scale=2)
                
                # Coluna de Ações Rápidas (Direita - O "Profissional")
                with gr.Column(scale=1):
                    gr.Markdown("### ⚡ Ações Rápidas")
                    btn_ofertas = gr.Button("🔍 Ver Ofertas", elem_classes="action-btn")
                    btn_boleto = gr.Button("📄 2ª Via Boleto", elem_classes="action-btn")
                    btn_ajuda = gr.Button("🆘 Preciso de Ajuda", elem_classes="action-btn")
                    gr.Markdown("---")
                    gr.Markdown("🔒 **Conexão Segura**\nCriptografia de ponta a ponta.")

            gr.Examples(
                examples=["Aceito a quitação à vista", "✅ Já paguei"], 
                inputs=txt_msg, label="Dúvidas comuns"
            )
            gr.Markdown("RenovaIA S.A. © 2024 - Todos os direitos reservados.", elem_classes="footer-info")

        # EVENTOS
        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_sair.click(encerrar_sessao, None, [tela_login, tela_chat, chatbot, status])
        
        # Fazendo os botões de ação rápida funcionarem (eles mandam texto pro chat)
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        
        btn_ofertas.click(lambda: "🔍 Quais são minhas ofertas?", None, txt_msg).then(
            responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        
        btn_boleto.click(lambda: "📄 Gostaria de solicitar a segunda via do meu boleto.", None, txt_msg).then(
            responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
            
        btn_ajuda.click(lambda: "🆘 Preciso de ajuda humana ou suporte.", None, txt_msg).then(
            responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

    return demo
