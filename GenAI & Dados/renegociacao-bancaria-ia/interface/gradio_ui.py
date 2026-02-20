import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

# Títulos aleatórios para dar a "vibe" dinâmica de fintech
TITULOS_IA = [
    "✨ Sua Nova Jornada Financeira",
    "🚀 Rumo à sua Liberdade Financeira",
    "🤝 Vamos transformar seu futuro?",
    "🌱 Semeando sua Saúde Financeira"
]

# CSS que será passado no .launch() para evitar avisos
MEU_CSS = """
.gradio-container { background-color: #f8fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #1e293b; font-weight: 800; font-size: 28px; padding: 20px; }
.action-btn { font-weight: 600 !important; margin-bottom: 10px !important; }
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
        # Adiciona o toque humano de fechamento se houver um boleto no texto
        if "```" in res and "📧" not in res:
            res += "\n\n📧 **Enviamos os detalhes para seu e-mail.** Vai dar tudo certo! 😊 🙌"
    except Exception as e:
        res = f"🤔 Ops, algo travou. Pode tentar de novo? (Erro: {str(e)})"
    
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
    
    # REMOVIDO o parâmetro css=MEU_CSS daqui para evitar o UserWarning
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR PAINEL", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            with gr.Row():
                gr.Markdown(f"## {titulo_sessao}")
                btn_sair = gr.Button("🚪 Sair", variant="stop", size="sm", scale=0)

            with gr.Row():
                with gr.Column(scale=4):
                    # CORREÇÃO PRINCIPAL: Removido o type="messages" que causava o TypeError
                    chatbot = gr.Chatbot(label="Consultor RenovaIA", height=450)
                    with gr.Row():
                        txt_msg = gr.Textbox(placeholder="Fale comigo...", scale=8, show_label=False)
                        btn_send = gr.Button("Enviar", variant="primary", scale=2)
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚡ Ações Rápidas")
                    btn_ofertas = gr.Button("🔍 Ver Ofertas", elem_classes="action-btn")
                    btn_boleto = gr.Button("📄 2ª Via Boleto", elem_classes="action-btn")
                    btn_ajuda = gr.Button("🆘 Ajuda", elem_classes="action-btn")

        # Eventos
        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_sair.click(encerrar_sessao, None, [tela_login, tela_chat, chatbot, status])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        
        # Lógica dos botões laterais
        btn_ofertas.click(lambda: "🔍 Quais são minhas ofertas?", None, txt_msg).then(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        btn_boleto.click(lambda: "📄 Segunda via do boleto, por favor.", None, txt_msg).then(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        btn_ajuda.click(lambda: "🆘 Preciso de suporte.", None, txt_msg).then(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

    return demo
