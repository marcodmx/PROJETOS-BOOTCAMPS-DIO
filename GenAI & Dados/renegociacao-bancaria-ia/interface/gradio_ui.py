import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

TITULOS_IA = ["✨ Sua Jornada Financeira", "🚀 Rumo ao Azul", "🤝 Vamos resolver?"]

MEU_CSS = """
.gradio-container { background-color: #f8fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #0f172a; font-weight: 800; font-size: 32px; padding: 20px; }
.action-btn { font-weight: 700 !important; margin-bottom: 12px !important; }
.error-msg { color: #dc2626 !important; font-weight: 600 !important; text-align: center; margin-top: 10px; }
span[style*="font-size: 20px"] { background-color: #eff6ff; padding: 2px 6px; border-radius: 4px; }
.prose pre { background-color: #f1f5f9 !important; border: 2px solid #e2e8f0 !important; border-radius: 8px !important; padding: 12px !important; }
.prose code { font-size: 18px !important; color: #1e293b !important; }
"""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ Atenção: Digite os 11 números do seu CPF."
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente.get('nome', 'Cliente').split()[0]
        dividas = cliente.get('dividas', [])
        produto = dividas[0].get('produto', 'crédito') if dividas else "crédito"
        msg = [[None, f"👋 Olá, {nome}! Que bom ter você aqui. Encontrei uma excelente oportunidade para seu {produto}. Vamos conferir?"]]
        return gr.update(visible=False), gr.update(visible=True), msg, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ Erro: CPF não localizado em nossa base."

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem: return historico, ""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Formato padrão para versões anteriores do Gradio (lista de listas)
    historico_ia = []
    if historico:
        for user_msg, ai_msg in historico:
            if user_msg: historico_ia.append({"role": "user", "content": user_msg})
            if ai_msg: historico_ia.append({"role": "assistant", "content": ai_msg})

    res = agente.responder(mensagem, str(cliente), historico_ia)
    historico.append([mensagem, res])
    return historico, ""

def criar_interface():
    titulo_sessao = random.choice(TITULOS_IA)
    # Removido o parâmetro CSS daqui para evitar o UserWarning
    with gr.Blocks(title="RenovaIA Pro") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="00000000000")
            btn_entrar = gr.Button("ACESSAR", variant="primary")
            status_login = gr.Markdown("", elem_classes="error-msg")

        with gr.Column(visible=False) as tela_chat:
            with gr.Row():
                with gr.Column(scale=8):
                    gr.Markdown(f"## {titulo_sessao}")
                with gr.Column(scale=1, min_width=100):
                    btn_sair = gr.Button("Sair 🚪", variant="secondary")

            with gr.Row():
                with gr.Column(scale=4):
                    # Removido type="messages" para evitar o TypeError
                    chatbot = gr.Chatbot(label="Consultor Virtual", height=550, sanitize_html=False)
                    with gr.Row():
                        txt_msg = gr.Textbox(placeholder="Fale com nosso consultor...", scale=8, show_label=False)
                        btn_send = gr.Button("Enviar", variant="primary", scale=2)
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚡ Ações Rápidas")
                    btn_ofertas = gr.Button("🔍 Minha Solução", elem_classes="action-btn")
                    btn_desc = gr.Button("📉 Propor Valor", elem_classes="action-btn")
                    btn_boleto = gr.Button("📄 Gerar Boleto", elem_classes="action-btn")

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_login])
        btn_sair.click(lambda: (gr.update(visible=True), gr.update(visible=False), None, ""), None, [tela_login, tela_chat, chatbot, status_login])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

        btn_ofertas.click(lambda h, c: responder_chat("Quais são as condições para meu caso?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_desc.click(lambda h, c: responder_chat("Gostaria de propor um valor diferente.", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_boleto.click(lambda h, c: responder_chat("Pode me enviar o código do boleto?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])

    return demo
