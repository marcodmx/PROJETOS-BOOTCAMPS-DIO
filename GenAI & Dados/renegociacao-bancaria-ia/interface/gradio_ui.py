import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

# Lista de títulos modernos e condizentes com o programa
TITULOS_IA = [
    "✨ Sua Nova Jornada Financeira",
    "🚀 Rumo à sua Liberdade Financeira",
    "🤝 Vamos transformar seu futuro?",
    "✨ Soluções Inteligentes para você",
    "🌱 Semeando sua Saúde Financeira"
]

MEU_CSS = """
.gradio-container { background-color: #f7fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #2c5282; font-weight: 800; font-size: 24px; padding: 20px; }
"""

def limpar_historico_para_ia(historico_gradio):
    if not historico_gradio: return []
    return [{"role": m["role"], "content": m["content"]} for m in historico_gradio if "role" in m and "content" in m]

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem:
        return historico, ""

    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if historico is None: historico = []
    historico_ia = limpar_historico_para_ia(historico)

    try:
        res = agente.responder(mensagem, str(cliente), historico_ia)
        
        if "```" in res:
            if "📧" not in res:
                res += "\n\n📧 **Acabei de enviar o boleto completo para o seu e-mail.**\n\nFique tranquilo, vai dar tudo certo! 😊 🙌"

    except Exception as e:
        res = f"🤔 Algo deu errado. Vamos tentar de novo? (Erro: {str(e)})"
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"👋 Oi, {nome}! Sou seu consultor RenovaIA.\n\nEstou aqui para te ajudar a resolver suas pendências de um jeito simples. Vamos ver o que conseguimos hoje? ✨"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado."

def criar_interface():
    # Escolhe um título aleatório toda vez que a função for chamada (no boot da app)
    titulo_sessao = random.choice(TITULOS_IA)
    
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="Digite seu CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("CONFERIR MINHAS OPÇÕES", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            # Título aleatório aplicado aqui
            gr.Markdown(f"## {titulo_sessao}") 
            chatbot = gr.Chatbot(label="Consultor Digital", height=500)
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Fale comigo ou escolha uma opção...", scale=8, show_label=False)
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
