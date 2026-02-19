import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types

# Inicializa o motor com a técnica de consulta
agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Formatação de histórico compatível com o SDK GenAI
    historico_ia = []
    for turno in historico:
        role_ia = "user" if turno['role'] == 'user' else "model"
        # Garante que o conteúdo seja extraído corretamente como string
        conteudo = turno['content']
        texto = conteudo[0].get('text', str(conteudo)) if isinstance(conteudo, list) else str(conteudo)
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto)]))

    # Chamada ao motor
    res = agente.responder(mensagem, str(cliente), historico_ia)
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"Olá {nome}, sou o consultor RenovaIA. Como posso ajudar na sua negociação hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não encontrado."

with gr.Blocks() as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 RenovaIA")
        cpf_input = gr.Textbox(label="Digite seu CPF", placeholder="00000000000")
        btn_entrar = gr.Button("VERIFICAR OFERTAS")
        status = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Chat de Negociação", height=500, type="messages")
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Sua mensagem...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", scale=2)

    btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    gr.close_all()
    demo.launch(share=True, debug=True)
