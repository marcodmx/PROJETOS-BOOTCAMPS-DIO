import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

TITULOS_IA = ["✨ Sua Jornada Financeira", "🚀 Rumo ao Azul", "🤝 Vamos resolver?", "💎 Oportunidade Exclusiva"]

MEU_CSS = """
.gradio-container { background-color: #f1f5f9 !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #1e3a8a; font-weight: 800; padding: 20px; font-size: 28px; }
.prose pre { background-color: #ffffff !important; border: 2px dashed #cbd5e1 !important; padding: 15px !important; border-radius: 10px; }
span[style*="color: #1e40af"] { background-color: #dbeafe; padding: 2px 8px; border-radius: 6px; font-weight: bold; }
"""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ CPF Inválido."

    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente.get('nome', 'Cliente').split()[0]
        dividas = cliente.get('dividas', [])
        produto = dividas[0].get('produto', 'crédito') if dividas else "crédito"
        
        msg_inicial = [{"role": "assistant", "content": f"👋 Olá, {nome}! Encontrei uma proposta de liquidação para seu **{produto}**. Vamos conversar sobre as condições?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não encontrado."

def responder_chat(mensagem, historico, cpf_com_mascara):
    if not mensagem: return historico, ""
    
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    divida = cliente.get('dividas', [{}])[0] if cliente else {}
    
    contexto = {
        "produto": divida.get("produto"),
        "total": divida.get("valor_total_atualizado"),
        "avista": divida.get("oferta_minima_avista"),
        "linha_digitavel": divida.get("codigo_boleto_atual")
    }

    historico = historico or []
    resposta_ia = agente.responder(mensagem, str(contexto), historico)
    
    if isinstance(resposta_ia, dict): resposta_ia = resposta_ia.get('text', str(resposta_ia))

    historico.append({"role": "user", "content": str(mensagem)})
    historico.append({"role": "assistant", "content": str(resposta_ia)})
    
    return historico, ""

def criar_interface():
    titulo_sessao = random.choice(TITULOS_IA)
    
    with gr.Blocks(title="RenovaIA Pro") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal de Negociação", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
            btn_entrar = gr.Button("CONSULTAR OFERTAS", variant="primary")
            status_login = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            gr.Markdown(f"### {titulo_sessao}")
            chatbot = gr.Chatbot(label="Atendimento", height=500)
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Digite sua mensagem...", scale=7, show_label=False)
                btn_send = gr.Button("Enviar", variant="primary", scale=1)

            with gr.Row():
                btn_oferta = gr.Button("🔍 Ver Detalhes", size="sm")
                # MUDANÇA AQUI: O botão agora provoca o fechamento
                btn_boleto = gr.Button("📄 Gerar Boleto", size="sm")
                btn_sair = gr.Button("Sair 🚪", size="sm", variant="secondary")

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_login])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        
        btn_oferta.click(lambda h, c: responder_chat("Quais os detalhes da oferta?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        
        # LÓGICA DO BOTÃO: Solicita fechamento antes de emitir
        btn_boleto.click(lambda h, c: responder_chat("Eu aceito a proposta. Pode gerar o boleto para mim?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        
        btn_sair.click(lambda: (gr.update(visible=True), gr.update(visible=False), None, ""), None, [tela_login, tela_chat, chatbot, status_login])

    return demo
