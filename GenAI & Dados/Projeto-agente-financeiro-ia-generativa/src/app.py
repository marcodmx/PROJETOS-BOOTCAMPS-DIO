import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types 

# Inicializa o motor de negociação
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    """
    Gerencia a lógica de conversa, botões de atalho e avaliação NPS.
    """
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    nome_cliente = cliente['nome'].split()[0] if cliente else "Cliente"

    # 1. SANITIZAÇÃO DO HISTÓRICO (Essencial para evitar Erro Técnico na API)
    historico_ia = []
    for turno in historico:
        role_ia = "user" if turno['role'] == 'user' else "model"
        conteudo = turno['content']
        
        # Garante extração de texto puro independente da versão do Gradio
        if isinstance(conteudo, list):
            texto_puro = conteudo[0].get('text', str(conteudo[0])) if isinstance(conteudo[0], dict) else str(conteudo[0])
        else:
            texto_puro = str(conteudo)
            
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto_puro)]))

    # 2. LÓGICA DE NPS (Avaliação de 1 a 10)
    # Só processa se a última mensagem da IA foi o pedido de nota
    if historico:
        ultima_msg_ia = str(historico[-1]['content']).lower()
        if "digite uma nota de 1 a 10" in ultima_msg_ia:
            if mensagem.isdigit() and 1 <= int(mensagem) <= 10:
                res = f"🌟 **Nota {mensagem} registrada!** Muito obrigado pelo feedback, {nome_cliente}. A RenovaIA deseja muito sucesso na sua jornada! ✨"
                historico.append({"role": "user", "content": f"Nota: {mensagem}"})
                historico.append({"role": "assistant", "content": res})
                return historico, ""

    # 3. TRATAMENTO DE BOTÕES E COMANDOS ESPECÍFICOS
    if "🔍 Verificar Ofertas" in mensagem:
        res = agente.responder("Quais são minhas ofertas atuais?", str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso de pagamento recebido!** Em até 3 dias úteis o sistema processará a baixa e seu limite será restabelecido. Parabéns pelo foco! 🙌"
    elif "🚪 Encerrar Atendimento" in mensagem:
        res = f"Foi um prazer te ajudar hoje, {nome_cliente}! ✅ Para encerrarmos, **por favor, digite uma nota de 1 a 10** para o meu atendimento. 👇"
    elif "❓ Ajuda" in mensagem:
        res = "🆘 **Central de Ajuda RenovaIA:**\n- Para ver propostas: Clique em 'Verificar Ofertas'.\n- Para pagar: Aceite uma proposta para gerar o boleto.\n- Suporte Humano: 0800 777 0000."
    else:
        # Envio normal para o Cérebro da IA
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # Atualiza a interface
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    """
    Valida o CPF na base e libera o acesso ao chat.
    """
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ Digite o CPF completo."
        
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor RenovaIA. Vamos regularizar sua situação com transparência total hoje? 🤝"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado em nossa base."

# --- INTERFACE VISUAL (GRADIO BLOCKS) ---
with gr.Blocks(title="RenovaIA") as demo:
    # Tela de Login
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🏦 RenovaIA</h1>")
        gr.Markdown("<p style='text-align: center;'>Portal de Negociação Segura e Transparente</p>")
        cpf_input = gr.Textbox(label="Digite seu CPF para começar", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR MINHAS OFERTAS", elem_classes="btn-banco")
        status_msg = gr.Markdown("")

    # Tela do Chat (Invisível até o login)
    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Atendimento RenovaIA", height=550, show_label=False)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Escolha uma opção abaixo ou digite aqui...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        # Menu de Ações Rápidas (Ex-Examples)
        gr.Examples(
            label="Escolha uma opção:",
            examples=[
                "🔍 Verificar Ofertas",
                "✅ Já efetuei o pagamento", 
                "🚪 Encerrar Atendimento",
                "❓ Ajuda"
            ], 
            inputs=txt_msg
        )

    # Eventos de clique e submissão
    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

# EXECUÇÃO E ESTILIZAÇÃO
if __name__ == "__main__":
    meu_css = """
    .btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }
    code { background-color: #f7fafc !important; color: #2d3748 !important; padding: 6px !important; border-radius: 6px; border: 1px solid #e2e8f0 !important; font-family: monospace !important; }
    footer { visibility: hidden !important; }
    .gradio-container { background-color: #fcfcfc !important; }
    """
    # launch() recebe o CSS no Gradio 6.0
    demo.launch(share=True, css=meu_css)
