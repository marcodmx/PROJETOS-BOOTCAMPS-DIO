import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)

    # 1. Construir a memória para a IA (Convertendo o histórico do Gradio)
    memoria_ia = []
    for turno in historico:
        if turno['role'] == 'user':
            memoria_ia.append({"role": "user", "parts": [{"text": turno['content']}]})
        else:
            memoria_ia.append({"role": "model", "parts": [{"text": turno['content']}]})
    
    # Adicionar a mensagem atual à memória
    memoria_ia.append({"role": "user", "parts": [{"text": mensagem}]})

    # 2. Obter resposta da IA com base na memória
    if "Já efetuei o pagamento" in mensagem:
        res = "✨ **Recebemos sua informação!** Aguarde a compensação bancária (até 3 dias úteis). 🙏"
    elif "Encerrar Atendimento" in mensagem:
        res = "Ficamos felizes em te atender. A **RenovaIA** está sempre aqui. Até logo! ✨"
    else:
        res = agente.responder(memoria_ia, str(cliente))
    
    # 3. Atualizar o histórico da interface
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        hist_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Encontrei ótimas oportunidades para sua saúde financeira hoje. Vamos conferir?"}]
        return gr.update(visible=False), gr.update(visible=True), hist_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado."

with gr.Blocks(title="RenovaIA") as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🏦 RenovaIA</h1>")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR OFERTAS")
        status_msg = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Consultor", height=500, type="messages")
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Como posso ajudar?", show_label=False, scale=8)
            btn_send = gr.Button("Enviar", scale=2)

    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    demo.launch(share=True)
