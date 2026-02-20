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
.action-btn { font-weight: 600 !important; margin-bottom: 12px !important; transition: all 0.3s ease; }
.action-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.btn-sair { max-width: 100px !important; min-width: 100px !important; height: 40px !important; }
.footer-info { text-align: center; color: #64748b; font-size: 11px; margin-top: 30px; }
"""

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem: return historico, ""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    historico = historico or []
    # Converte histórico Gradio para formato IA
    historico_ia = [{"role": m["role"], "content": m["content"]} for m in historico]

    try:
        res = agente.responder(mensagem, str(cliente), historico_ia)
        if "```" in res and "📧" not in res:
            res += "\n\n✅ **Acordo formalizado!** O boleto foi enviado para seu e-mail cadastrado. Parabéns por esse passo! 🚀"
    except:
        res = "🤔 Tive um pequeno problema. Pode repetir?"
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg = [{"role": "assistant", "content": f"👋 Olá, {nome}! Sou o Estrategista da RenovaIA. Vamos encontrar a melhor solução para sua saúde financeira hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado."

def criar_interface():
    titulo_sessao = random.choice(TITULOS_IA)
    with gr.Blocks(title="RenovaIA Pro") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR DASHBOARD", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            with gr.Row():
                with gr.Column(scale=9):
                    gr.Markdown(f"## {titulo_sessao}")
                with gr.Column(scale=1, min_width=100):
                    btn_sair = gr.Button("Sair 🚪", variant="secondary", elem_classes="btn-sair")

            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(label="Consultoria Conversacional", height=450)
                    with gr.Row():
                        txt_msg = gr.Textbox(placeholder="Digite sua dúvida ou proposta...", scale=8, show_label=False)
                        btn_send = gr.Button("Enviar", variant="primary", scale=2)
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚡ Ações Rápidas")
                    btn_ofertas = gr.Button("🔍 Ver Ofertas", elem_classes="action-btn")
                    btn_desc = gr.Button("📉 Pedir Desconto", elem_classes="action-btn")
                    btn_boleto = gr.Button("📄 2ª Via Boleto", elem_classes="action-btn")
                    btn_ajuda = gr.Button("🆘 Suporte", elem_classes="action-btn")
                    gr.Markdown("---")
                    gr.Markdown("🔐 **Sistema Auditado**\nConforme normas LGPD e BACEN.")

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_sair.click(lambda: (gr.update(visible=True), gr.update(visible=False), None, ""), None, [tela_login, tela_chat, chatbot, status])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        
        # Conexão dos botões rápidos com a inteligência
        btn_ofertas.click(lambda: "Quais são minhas melhores ofertas?", None, txt_msg).then(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        btn_desc.click(lambda: "Gostaria de um desconto maior para pagamento à vista. O que consegue fazer?", None, txt_msg).then(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        btn_boleto.click(lambda: "Preciso da 2ª via do meu boleto atual.", None, txt_msg).then(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        btn_ajuda.click(lambda: "Como funciona o abatimento de juros em parcelas adiantadas?", None, txt_msg).then(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

        gr.Markdown("RenovaIA S.A. © 2024 - Instituição de Pagamento Autorizada", elem_classes="footer-info")
    return demo
