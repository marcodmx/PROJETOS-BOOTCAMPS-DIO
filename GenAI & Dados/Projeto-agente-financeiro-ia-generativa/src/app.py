import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types 

agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)

    # 1. Tratamento de Nota/NPS (Intercepção antes da IA)
    if mensagem.isdigit() and 1 <= int(mensagem) <= 10:
        res = f"🌟 **Nota {mensagem} recebida!** Muito obrigado por sua avaliação, {cliente['nome'].split()[0]}. Seu feedback é fundamental para evoluirmos nossa consultoria financeira! ✨"
        historico.append({"role": "user", "content": f"Nota: {mensagem}"})
        historico.append({"role": "assistant", "content": res})
        return historico, ""

    # 2. Preparação de Histórico Sanitizado
    historico_ia = []
    for turno in historico:
        role_ia = "user" if turno['role'] == 'user' else "model"
        texto = turno['content'][0].get('text') if isinstance(turno['content'], list) else str(turno['content'])
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto)]))

    # 3. Gatilhos de Botões
    if "Já efetuei o pagamento" in mensagem:
        res = "✍️ **Registrado!** Em até 3 dias úteis seu limite será restabelecido. Parabéns pelo foco! 🙌"
    elif "Encerrar Atendimento" in mensagem:
        res = "Atendimento finalizado com sucesso. Por favor, **digite uma nota de 1 a 10** para o meu atendimento antes de sair! 👇"
    else:
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg = f"✨ **Olá, {nome}!** Sou seu assistente RenovaIA. Identifiquei uma oportunidade de regularização com condições especiais de juros e CET. Vamos conferir? 🤝"
        return gr.update(visible=False), gr.update(visible=True), [{"role": "assistant", "content": msg}], ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado."

meu_css = ".btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; }"

with gr.Blocks(title="RenovaIA") as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🏦 RenovaIA</h1>")
        cpf_input = gr.Textbox(label="Acesse com seu CPF", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR OFERTAS", elem_classes="btn-banco")
        status_msg = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Consultoria de Crédito", height=500)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Responda ou digite sua dúvida...", scale=8)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        gr.Examples(examples=["✅ Já efetuei o pagamento", "🚪 Encerrar Atendimento"], inputs=txt_msg)

    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    demo.launch(share=True, css=meu_css)
