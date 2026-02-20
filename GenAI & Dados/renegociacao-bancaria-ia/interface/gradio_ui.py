import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

TITULOS_IA = ["✨ Sua Jornada Financeira", "🚀 Rumo ao Azul", "🤝 Vamos resolver?", "🌱 Saúde Financeira"]

MEU_CSS = """
.gradio-container { background-color: #f8fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #1e293b; font-weight: 800; font-size: 28px; padding: 20px; }
.action-btn { font-weight: 600 !important; margin-bottom: 12px !important; }
.btn-sair { max-width: 100px !important; min-width: 100px !important; height: 40px !important; }
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
        msg = [{"role": "assistant", "content": f"👋 Oi, {nome}! Vamos colocar suas contas em dia hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado."

def criar_interface():
    titulo_sessao = random.choice(TITULOS_IA)
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ENTRAR", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            with gr.Row():
                gr.Markdown(f"## {titulo_sessao}", scale=8)
                btn_sair = gr.Button("Sair 🚪", variant="secondary", elem_classes="btn-sair")

            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(label="Chat Seguro", height=450)
                    with gr.Row():
                        txt_msg = gr.Textbox(placeholder="Digite sua dúvida...", scale=8, show_label=False)
                        btn_send = gr.Button("Enviar", variant="primary", scale=2)
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚡ Ações")
                    btn_ofertas = gr.Button("🔍 Ver Ofertas", elem_classes="action-btn")
                    btn_desc = gr.Button("📉 Pedir Desconto", elem_classes="action-btn")
                    btn_boleto = gr.Button("📄 2ª Via", elem_classes="action-btn")
                    btn_ajuda = gr.Button("🆘 Suporte", elem_classes="action-btn")

        # EVENTOS
        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_sair.click(lambda: (gr.update(visible=True), gr.update(visible=False), None, ""), None, [tela_login, tela_chat, chatbot, status])
        
        # O pulo do gato: Conectar os botões para escrever no chat e enviar automaticamente
        def acao_rapida(texto, hist, cpf):
            return responder_chat(texto, hist, cpf)

        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

        btn_ofertas.click(lambda h, c: acao_rapida("Quais são minhas ofertas?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_desc.click(lambda h, c: acao_rapida("Quero um desconto maior!", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_boleto.click(lambda h, c: acao_rapida("Preciso do boleto.", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_ajuda.click(lambda h, c: acao_rapida("Como funciona o desconto de juros?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])

    return demo
