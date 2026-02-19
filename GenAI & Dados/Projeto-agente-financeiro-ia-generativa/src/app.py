import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types 

# Inicializa o motor
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    nome_cliente = cliente['nome'].split()[0] if cliente else "Cliente"

    # 1. SANITIZAÇÃO DO HISTÓRICO (Para evitar erro de Schema)
    historico_ia = []
    for turno in historico:
        role_ia = "user" if turno['role'] == 'user' else "model"
        conteudo = turno['content']
        
        # Extração segura de texto para o Gemini
        if isinstance(conteudo, list):
            texto = conteudo[0].get('text', str(conteudo[0])) if isinstance(conteudo[0], dict) else str(conteudo[0])
        else:
            texto = str(conteudo)
            
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto)]))

    # 2. LÓGICA DE NPS (Só após o encerramento)
    if historico:
        ultima_msg = str(historico[-1]['content']).lower()
        if "digite uma nota de 1 a 10" in ultima_msg:
            if mensagem.isdigit() and 1 <= int(mensagem) <= 10:
                res = f"🌟 **Nota {mensagem} registrada!** Obrigado, {nome_cliente}. A RenovaIA agradece seu feedback! ✨"
                historico.append({"role": "user", "content": f"Nota: {mensagem}"})
                historico.append({"role": "assistant", "content": res})
                return historico, ""

    # 3. TRATAMENTO DE COMANDOS E BOTÕES
    if "🔍 Verificar Ofertas" in mensagem:
        res = agente.responder("Quais são minhas ofertas?", str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso registrado!** O prazo de compensação é de até 3 dias úteis. Parabéns pelo foco! 🙌"
    elif "🚪 Encerrar Atendimento" in mensagem:
        res = f"Foi um prazer ajudar, {nome_cliente}! ✅ **Por favor, digite uma nota de 1 a 10** para meu atendimento. 👇"
    elif "❓ Ajuda" in mensagem:
        res = "🆘 **Suporte:**\n- 'Verificar Ofertas' para ver dívidas.\n- Aceite uma proposta para gerar o boleto.\n- SAC: 0800 777 0000."
    else:
        # Resposta da IA via motor
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor RenovaIA. Vamos regularizar sua saúde financeira com transparência total? 🤝"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado."

# Interface Visual
with gr.Blocks(title="RenovaIA") as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🏦 RenovaIA</h1>")
        cpf_input = gr.Textbox(label="Acesse com seu CPF", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR MINHAS OFERTAS", elem_classes="btn-banco")
        status_msg = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Chat", height=550, show_label=False)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite aqui...", scale=8, show_label=False)
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
    code { background-color: #f7fafc !important; color: #2d3748 !important; padding: 6px !important; border-radius: 6px; border: 1px solid #e2e8f0 !important; }
    footer { visibility: hidden !important; }
    """
    demo.launch(share=True, css=meu_css)
