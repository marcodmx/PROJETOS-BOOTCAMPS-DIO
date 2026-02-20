import gradio as gr
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

MEU_CSS = """
.gradio-container { background-color: #f7fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #2c5282; font-weight: 800; }
"""

def limpar_historico_para_ia(historico_gradio):
    if not historico_gradio: return []
    # Mantém apenas a conversa pura para a IA não se confundir com metadados
    return [{"role": m["role"], "content": m["content"]} for m in historico_gradio]

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem:
        return historico, ""

    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if historico is None: historico = []
    
    # 1. Preparação: A IA recebe o histórico completo para ter contexto
    historico_ia = limpar_historico_para_ia(historico)

    # 2. Processamento: A IA interpreta a intenção (seja "1", "quero pagar" ou "tá caro")
    try:
        # Passamos a mensagem bruta. O "cérebro" da IA no engine.py decide o que fazer.
        res = agente.responder(mensagem, str(cliente), historico_ia)
        
        if not res:
            res = "🤔 Notei um silêncio por aqui... Pode me contar melhor o que você achou das opções?"
            
    except Exception as e:
        res = f"🤔 Tive um pequeno descompasso técnico. Vamos tentar de novo? (Erro: {str(e)})"
    
    # 3. Atualização visual
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        # A primeira mensagem já dita o tom "Nubank + Bradesco"
        msg_inicial = [{"role": "assistant", "content": f"👋 Olá, {nome}! Sou seu consultor RenovaIA.\n\nVi que você tem uma pendência conosco. Meu papel é facilitar sua vida e encontrar um caminho que caiba no seu bolso, com total segurança. Como você prefere começar?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado."

def criar_interface():
    with gr.Blocks(title="RenovaIA") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("ACESSAR PAINEL", variant="primary")
            status = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            gr.Markdown("## ✨ Negociação Consciente")
            chatbot = gr.Chatbot(label="Atendimento RenovaIA", height=500)
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Sua resposta aqui...", scale=8, show_label=False)
                btn_send = gr.Button("Enviar", variant="primary", scale=2)

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

    return demo
