import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types 

agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    nome_cliente = cliente['nome'].split()[0] if cliente else "Cliente"

    # 1. Lógica Contextual de NPS (Só aceita nota se a IA pediu anteriormente)
    if historico:
        ultima_resposta = historico[-1]['content']
        if "digite uma nota de 1 a 10" in str(ultima_resposta).lower():
            if mensagem.isdigit() and 1 <= int(mensagem) <= 10:
                res = f"🌟 **Nota {mensagem} registrada!** Muito obrigado, {nome_cliente}. Seu feedback ajuda a RenovaIA a ser cada vez melhor para sua saúde financeira. Até logo! ✨"
                historico.append({"role": "user", "content": f"Nota: {mensagem}"})
                historico.append({"role": "assistant", "content": res})
                return historico, ""

    # 2. Gatilhos de Botões
    if "Já efetuei o pagamento" in mensagem:
        res = "✍️ **Confirmado!** Registrei aqui sua informação. Em até 3 dias úteis o pagamento será compensado e seu limite restabelecido. Parabéns! 🙌"
    elif "Encerrar Atendimento" in mensagem:
        res = f"Foi um prazer te ajudar hoje, {nome_cliente}! ✅ Para encerrarmos com chave de ouro, **por favor, digite uma nota de 1 a 10** para o meu atendimento. 👇"
    else:
        # 3. Preparação do Histórico para IA (Sanitizado)
        historico_ia = []
        for turno in historico:
            role_ia = "user" if turno['role'] == 'user' else "model"
            conteudo = turno['content']
            texto = conteudo[0].get('text') if isinstance(conteudo, list) else str(conteudo)
            historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto)]))
        
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg = f"✨ **Olá, {nome}!** Sou seu consultor RenovaIA. Analisei seu perfil e preparei condições com transparência total de CET e juros. Vamos regularizar isso hoje? 🤝"
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
        chatbot = gr.Chatbot(label="Atendimento RenovaIA", height=500)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Escolha uma opção ou tire dúvidas...", scale=8)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        gr.Examples(examples=["✅ Já efetuei o pagamento", "🚪 Encerrar Atendimento"], inputs=txt_msg)

    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    demo.launch(share=True, css=meu_css)
