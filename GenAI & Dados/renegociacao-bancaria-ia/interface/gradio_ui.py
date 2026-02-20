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
.btn-sair { max-width: 100px !important; min-width: 100px !important; height: 40px !important; }

/* Estilo para valores destacados via SPAN */
span[style*="font-size: 20px"] {
    background-color: #eff6ff;
    padding: 2px 6px;
    border-radius: 4px;
}

/* Bloco de Código (Boleto) Acessível */
code { 
    font-size: 18px !important; 
    color: #1e293b !important;
    background-color: #f1f5f9 !important;
    border: 1px solid #e2e8f0 !important;
    padding: 12px !important;
    display: block !important;
}
"""

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem: return historico, ""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    historico = historico or []
    historico_ia = [{"role": m["role"], "content": m["content"]} for m in historico]

    res = agente.responder(mensagem, str(cliente), historico_ia)
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg = [{"role": "assistant", "content": f"👋 Oi, {nome}! Vamos colocar suas contas em dia?"}]
        return gr.update(visible=False), gr.update(visible=True), msg, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado."

def criar_interface():
    titulo_sessao = random.choice(TITULOS_IA)
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR", variant="primary")

        with gr.Column(visible=False) as tela_chat:
            with gr.Row():
                with gr.Column(scale=8):
                    gr.Markdown(f"## {titulo_sessao}")
                with gr.Column(scale=1, min_width=100):
                    btn_sair = gr.Button("Sair 🚪", variant="secondary", elem_classes="btn-sair")

            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(label="Chat Seguro", height=550, sanitize_html=False)
                    with gr.Row():
                        txt_msg = gr.Textbox(placeholder="Fale com nossa IA...", scale=8, show_label=False)
                        btn_send = gr.Button("Enviar", variant="primary", scale=2)
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚡ Ações")
                    btn_ofertas = gr.Button("🔍 Ofertas e CET", elem_classes="action-btn")
                    btn_desc = gr.Button("📉 Pedir Desconto", elem_classes="action-btn")
                    btn_boleto = gr.Button("📄 Gerar Boleto", elem_classes="action-btn")
                    btn_ajuda = gr.Button("🆘 Suporte", elem_classes="action-btn")

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot])
        btn_sair.click(lambda: (gr.update(visible=True), gr.update(visible=False), None), None, [tela_login, tela_chat, chatbot])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

        # Cliques Rápidos
        btn_ofertas.click(lambda h, c: responder_chat("Quais são minhas ofertas e o CET?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_desc.click(lambda h, c: responder_chat("Quero um desconto maior!", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_boleto.click(lambda h, c: responder_chat("Me mande o código do boleto para pagar.", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_ajuda.click(lambda h, c: responder_chat("Preciso de suporte.", h, c), [chatbot, cpf_input], [chatbot, txt_msg])

    return demo
