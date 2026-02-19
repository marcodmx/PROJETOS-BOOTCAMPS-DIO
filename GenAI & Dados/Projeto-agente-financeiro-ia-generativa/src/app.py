import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types 

# Inicializa o motor de negociação
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    """
    Processa a mensagem do usuário, gerencia a memória do chat e retorna a resposta da IA.
    """
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)

    # 🧠 CONSTRUÇÃO DA MEMÓRIA: Converte o histórico do Gradio para o formato Google GenAI
    historico_ia = []
    for turno in historico:
        role_ia = "user" if turno['role'] == 'user' else "model"
        conteudo = turno['content']
        
        # BLINDAGEM: Extrai texto puro caso o Gradio envie objetos complexos/listas
        if isinstance(conteudo, list):
            texto_puro = conteudo[0].get('text', str(conteudo)) if isinstance(conteudo[0], dict) else str(conteudo[0])
        else:
            texto_puro = str(conteudo)
            
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto_puro)]))

    # 🤖 RESPOSTAS RÁPIDAS (Lógica de Botões e Encerramento)
    if "Já efetuei o pagamento" in mensagem:
        res = "✨ **Recebemos sua informação!** Agora é só aguardar a compensação bancária (até 3 dias úteis). Guarde seu comprovante com carinho. 🙏"
    elif "Encerrar Atendimento" in mensagem:
        res = "Ficamos felizes em te atender. A **RenovaIA** está sempre aqui para apoiar sua saúde financeira. Até logo! ✨"
    else:
        # Envia para o motor processar com base no histórico completo
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # Atualiza o componente de chat
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    """
    Valida o CPF e transiciona da tela de login para o chat.
    """
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ Por favor, digite o CPF completo."
        
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        hist_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Que bom te ver por aqui. Encontrei ótimas oportunidades para cuidarmos da sua saúde financeira hoje. Vamos dar uma olhada?"}]
        return gr.update(visible=False), gr.update(visible=True), hist_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado em nossa base."

# 🎨 ESTILIZAÇÃO BANCO AZUL
meu_css = ".btn-banco { background: #2b6cb0 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }"

with gr.Blocks(title="RenovaIA") as demo:
    # --- TELA DE LOGIN ---
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("<h1 style='text-align: center; color: #2b6cb0;'>🏦 RenovaIA</h1>")
        gr.Markdown("<p style='text-align: center;'>Portal de Negociação Segura</p>")
        cpf_input = gr.Textbox(label="Digite seu CPF", placeholder="000.000.000-00")
        btn_verificar = gr.Button("VERIFICAR MINHAS OFERTAS", elem_classes="btn-banco")
        status_msg = gr.Markdown("")

    # --- TELA DE CHAT ---
    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Consultor Financeiro Virtual", height=550)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua resposta aqui...", show_label=False, scale=8)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
            
        # Atalhos de Interação
        gr.Examples(
            examples=["✅ Já efetuei o pagamento", "🚪 Encerrar Atendimento"], 
            inputs=txt_msg
        )

    # MAPEAMENTO DE EVENTOS
    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

# EXECUÇÃO DO SERVIDOR
if __name__ == "__main__":
    # CSS injetado no launch para conformidade com Gradio 6.0+
    demo.launch(share=True, css=meu_css)
