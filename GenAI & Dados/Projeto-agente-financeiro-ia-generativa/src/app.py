import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o motor de IA
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    """Lógica de resposta do chat com suporte a botões rápidos e motor de IA."""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if "Já efetuei o pagamento" in mensagem:
        res = "✨ **Recebemos sua informação!** Agora é só aguardar a compensação bancária (até 3 dias úteis). Guarde seu comprovante com carinho. 🙏"
    elif "Encerrar Atendimento" in mensagem:
        res = "Ficamos felizes em te atender. A **RenovaIA** está sempre aqui para apoiar sua saúde financeira. Até logo! ✨"
    else:
        # Chama a inteligência do motor (engine.py)
        res = agente.responder(mensagem, str(cliente))
    
    # Formato de histórico padrão para compatibilidade
    historico.append([mensagem, res])
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    """Valida o CPF e troca a tela de login para a tela de chat."""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ CPF incompleto."
    
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        # Saudação inicial humanizada (sem falar de pendência)
        hist_inicial = [[None, f"✨ **Olá, {nome}!** Que bom te ver por aqui. Encontrei ótimas oportunidades para cuidarmos da sua saúde financeira hoje. Vamos dar uma olhada?"]]
        return gr.update(visible=False), gr.update(visible=True), hist_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado."

# Estilização via CSS
css = r"""
.btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; height: 50px !important; }
.btn-encerrar { background: #f7fafc !important; color: #4a5568 !important; border: 1px solid #cbd5e0 !important; }
"""

with gr.Blocks(title="RenovaIA - Consultoria Financeira") as demo:
    # --- TELA DE LOGIN / CONSULTA ---
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🏦 RenovaIA</h1>")
        gr.Markdown("<p style='text-align: center;'>Sua jornada para a tranquilidade financeira começa aqui.</p>")
        
        with gr.Row():
            with gr.Column(scale=1): pass
            with gr.Column(scale=2):
                cpf_input = gr.Textbox(label="Informe seu CPF para começar", placeholder="000.000.000-00")
                btn_verificar = gr.Button("VERIFICAR OFERTAS", variant="primary", elem_classes="btn-banco")
                status_msg = gr.Markdown("")
            with gr.Column(scale=1): pass

    # --- TELA DO CHAT (SÓ FICA VISÍVEL APÓS O LOGIN) ---
    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Consultor RenovaIA", height=500)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Como posso te ajudar?", show_label=False, scale=8)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
            
        gr.Examples(
            examples=["✅ Já efetuei o pagamento", "🚪 Encerrar Atendimento"],
            inputs=txt_msg,
            label="Ações rápidas"
        )

    # --- MAPEAMENTO DE EVENTOS ---
    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

# Lançamento do Aplicativo
if __name__ == "__main__":
    # share=True é essencial no Google Colab para gerar o link público
    # debug=True ajuda a ver se a cota da API estourar novamente
    demo.launch(css=css, share=True, debug=True)
