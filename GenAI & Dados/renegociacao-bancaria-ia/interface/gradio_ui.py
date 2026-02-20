import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

agente = AgenteNegociador()

TITULOS_IA = ["✨ Sua Jornada Financeira", "🚀 Rumo ao Azul", "🤝 Vamos resolver?"]

# Mantemos a variável de CSS, mas não a passamos no Blocks
MEU_CSS = """
.gradio-container { background-color: #f1f5f9 !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #1e3a8a; font-weight: 800; padding: 20px; font-size: 28px; }

/* Bloco de Código (Boleto) Estilizado */
.prose pre {
    background-color: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    color: #0f172a !important;
    padding: 15px !important;
    border-radius: 10px !important;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
}
.prose code {
    font-family: 'Courier New', monospace !important;
    font-weight: bold !important;
    font-size: 1.1em !important;
}

/* Destaque para valores financeiros */
span[style*="color: #1e40af"] {
    background-color: #dbeafe;
    padding: 2px 8px;
    border-radius: 6px;
    border: 1px solid #bfdbfe;
    font-weight: bold;
}
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
        
        # Formato de lista de dicionários para compatibilidade
        msg_inicial = [{"role": "assistant", "content": f"👋 Olá, {nome}! Identificamos uma oportunidade de liquidação para seu **{produto}**. Como podemos avançar hoje?"}]
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
    
    # Adiciona ao histórico garantindo que seja string
    historico.append({"role": "user", "content": str(mensagem)})
    historico.append({"role": "assistant", "content": str(resposta_ia)})
    
    return historico, ""

def criar_interface():
    # Removido parâmetro css daqui para evitar UserWarning
    with gr.Blocks(title="RenovaIA v2") as demo:
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal de Negociação", elem_classes="main-header")
            cpf_input = gr.Textbox(label="Digite seu CPF para consultar ofertas", placeholder="000.000.000-00")
            btn_entrar = gr.Button("CONSULTAR OFERTAS", variant="primary")
            status_login = gr.Markdown("")

        with gr.Column(visible=False) as tela_chat:
            gr.Markdown("### 🤝 Negociação em Tempo Real")
            # Removido type="messages" para evitar TypeError
            chatbot = gr.Chatbot(label="Atendimento", height=500)
            
            with gr.Row():
                txt_msg = gr.Textbox(placeholder="Digite sua proposta ou dúvida...", scale=7, show_label=False)
                btn_send = gr.Button("Enviar", variant="primary", scale=1)

            with gr.Row():
                btn_oferta = gr.Button("🔍 Ver Detalhes", size="sm")
                btn_boleto = gr.Button("📄 Gerar Boleto", size="sm")
                btn_sair = gr.Button("Sair 🚪", size="sm", variant="secondary")

        btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_login])
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        
        btn_oferta.click(lambda h, c: responder_chat("Pode me dar os detalhes da oferta?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_boleto.click(lambda h, c: responder_chat("Gere o boleto para mim agora, por favor.", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_sair.click(lambda: (gr.update(visible=True), gr.update(visible=False), None, ""), None, [tela_login, tela_chat, chatbot, status_login])

    return demo
