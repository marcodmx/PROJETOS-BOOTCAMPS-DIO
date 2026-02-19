import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o motor
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if "Já efetuei o pagamento" in mensagem:
        res = "✨ **Recebemos sua informação!** Agora é só aguardar a compensação bancária (até 3 dias úteis). Guarde seu comprovante com carinho. 🙏"
    elif "Encerrar Atendimento" in mensagem:
        res = "Ficamos felizes em te atender. A **RenovaIA** está sempre aqui para apoiar sua saúde financeira. Até logo! ✨"
    else:
        res = agente.responder(mensagem, str(cliente))
    
    # Formato de histórico compatível com versões antigas e novas (lista de listas)
    historico.append([mensagem, res])
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ CPF incompleto."
    
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        # Saudação humanizada
        hist_inicial = [[None, f"✨ **Olá, {nome}!** Que bom te ver por aqui. Encontrei ótimas oportunidades para cuidarmos da sua saúde financeira hoje. Vamos dar uma olhada?"]]
        return gr.update(visible=False), gr.update(visible=True), hist_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado."

# CSS simplificado para evitar alertas de sistema
meu_css = ".btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; }"

with gr.Blocks(title="RenovaIA") as demo:
    # TELA DE LOGIN
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center;'>🏦 RenovaIA</h1>")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR OFERTAS", elem_classes="btn-banco")
        status_msg = gr.Markdown("")

    # TELA DO CHAT
    with gr.Column(visible=False) as tela_chat:
        # Sem o argumento 'type', para garantir compatibilidade total
        chatbot = gr.Chatbot(label="Atendimento", height=450)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite aqui...", show_label=False, scale=8)
            btn_send = gr.Button("Enviar", scale=2)
            
        gr.Examples(examples=["✅ Já efetuei o pagamento", "🚪 Encerrar Atendimento"], inputs=txt_msg)

    # EVENTOS
    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    # CSS e Share aqui no launch para não dar erro
    demo.launch(css=meu_css, share=True, debug=True)
