import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types

agente = AgenteNegociador()

# Definindo o estilo para o launch
meu_css = ".gradio-container { background-color: #f7fafc; } .main-header { text-align: center; color: #2c5282; font-weight: bold; }"

def extrair_texto(conteudo):
    """Trata formatos de mensagem do Gradio 5/6 para o Gemini."""
    if isinstance(conteudo, str): return conteudo
    if isinstance(conteudo, list) and len(conteudo) > 0:
        if isinstance(conteudo[0], dict): return conteudo[0].get('text', '')
        return str(conteudo[0])
    return str(conteudo)

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    historico_ia = []
    for msg in historico:
        role_ia = "user" if msg['role'] == 'user' else "model"
        texto_limpo = extrair_texto(msg['content'])
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto_limpo)]))

    if "🔍 Verificar Ofertas" in mensagem:
        res = agente.responder("Calcule agora minha quitação à vista com Art. 52 CDC e parcelamento 1.99% CET.", str(cliente), historico_ia)
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
        # Saudação Humanizada sem spam de lei
        msg_inicial = [{"role": "assistant", "content": f"✨ Olá, {nome}! Sou o consultor da RenovaIA. Como posso ajudar com sua situação hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não encontrado."

with gr.Blocks(title="RenovaIA") as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 RenovaIA", elem_classes="main-header")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
        btn_entrar = gr.Button("ENTRAR", variant="primary")
        status = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Atendimento", height=500)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Sua mensagem...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        gr.Examples(
            examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar"], 
            inputs=txt_msg,
            label="Ações Rápidas"
        )

    btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    gr.close_all()
    # CSS movido para cá para matar o UserWarning do Gradio 6
    demo.launch(share=True, inline=False, debug=True, css=meu_css)
