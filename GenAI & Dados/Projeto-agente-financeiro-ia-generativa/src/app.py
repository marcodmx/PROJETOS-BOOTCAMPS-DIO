import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Lógica de respostas rápidas para não sobrecarregar a IA
    if "Já efetuei o pagamento" in mensagem:
        res = "🌟 **Parabéns pela iniciativa!** Recebemos sua informação. Agora é só aguardar a compensação bancária (até 3 dias úteis). Guarde seu comprovante!"
    elif "Encerrar Atendimento" in mensagem:
        res = "Obrigado por utilizar a **RenovaIA**. Sua jornada para a saúde financeira continua. Até logo! 👋"
    else:
        res = agente.responder(mensagem, str(cliente))
    
    # Formato de DICIONÁRIO que o seu Gradio exigiu da última vez
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ CPF incompleto."
    
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        hist_inicial = [{"role": "assistant", "content": f"🏦 **Olá, {nome}!** Localizei seu cadastro. Como podemos resolver sua pendência hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), hist_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado."

css = r"""
.btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; }
.btn-whatsapp { background: #25D366 !important; color: white !important; }
"""

with gr.Blocks() as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center;'>🏦 RenovaIA</h1>")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR OFERTAS", variant="primary", elem_classes="btn-banco")
        status_msg = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        # REMOVIDO O 'TYPE' PARA EVITAR O ERRO QUE DEU AGORA
        chatbot = gr.Chatbot(label="Atendimento", height=450)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite aqui...", show_label=False, scale=7)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
            
        gr.Examples(
            examples=["✅ Já efetuei o pagamento", "📱 Receber no WhatsApp", "🚪 Encerrar Atendimento"],
            inputs=txt_msg
        )

    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

# CSS NO LAUNCH PARA RESPEITAR O AVISO DO GRADIO
if __name__ == "__main__":
    demo.launch(share=True, css=css)
