import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types 

# Inicializa o motor (agora com busca automática)
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    nome_cliente = cliente['nome'].split()[0] if cliente else "Cliente"

    # 1. Limpeza de histórico para a IA
    historico_ia = []
    for turno in historico:
        role_ia = "user" if turno['role'] == 'user' else "model"
        conteudo = turno['content']
        texto = conteudo[0].get('text', str(conteudo[0])) if isinstance(conteudo, list) else str(conteudo)
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto)]))

    # 2. Lógica de NPS (Avaliação)
    if historico:
        ultima_msg = str(historico[-1]['content']).lower()
        if "digite uma nota de 1 a 10" in ultima_msg:
            if mensagem.isdigit() and 1 <= int(mensagem) <= 10:
                res = f"🌟 **Nota {mensagem} registrada!** Valeu pelo feedback, {nome_cliente}! ✨"
                historico.append({"role": "user", "content": f"Nota: {mensagem}"})
                historico.append({"role": "assistant", "content": res})
                return historico, ""

    # 3. Comandos Rápidos
    if "🔍 Verificar Ofertas" in mensagem:
        res = agente.responder("Quais minhas ofertas?", str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso recebido!** Compensação em até 3 dias úteis. Parabéns pela organização! 🙌"
    elif "🚪 Encerrar Atendimento" in mensagem:
        res = f"Até logo, {nome_cliente}! ✅ **Por favor, digite uma nota de 1 a 10** para meu atendimento. 👇"
    elif "❓ Ajuda" in mensagem:
        res = "🆘 **Ajuda:**\n- Clique em 'Verificar Ofertas' para ver sua dívida.\n- SAC: 0800 777 0000."
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
        msg = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor RenovaIA. Vamos regularizar sua situação hoje? 🤝"}]
        return gr.update(visible=False), gr.update(visible=True), msg, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado."

# Interface Visual
with gr.Blocks(title="RenovaIA") as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🏦 RenovaIA</h1>")
        cpf_input = gr.Textbox(label="Seu CPF", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR MINHAS OFERTAS", elem_classes="btn-banco")
        status_msg = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Chat", height=550, show_label=False)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite ou escolha uma opção...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        gr.Examples(
            label="Escolha uma opção:",
            examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar Atendimento", "❓ Ajuda"], 
            inputs=txt_msg
        )

    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    meu_css = """
    .btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }
    code { background-color: #f7fafc !important; padding: 6px !important; border-radius: 6px; border: 1px solid #e2e8f0 !important; }
    footer { visibility: hidden !important; }
    """
    demo.launch(share=True, css=meu_css)
