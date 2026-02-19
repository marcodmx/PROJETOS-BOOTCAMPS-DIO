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
    
    # 🎯 FORMATO COMPATÍVEL: Convertendo o histórico do Gradio para o GenAI
    # O histórico do Gradio vem como uma lista de listas [[user, bot], [user, bot]]
    historico_ia = []
    for user_msg, bot_msg in historico:
        historico_ia.append(types.Content(role="user", parts=[types.Part(text=user_msg)]))
        historico_ia.append(types.Content(role="model", parts=[types.Part(text=bot_msg)]))

    # Chamada ao motor
    res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # O Gradio espera que você retorne o histórico atualizado
    historico.append((mensagem, res))
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = f"Olá {nome}, sou o consultor RenovaIA. Como posso ajudar?"
        # Retornamos uma tupla (user, bot) para o formato padrão do chatbot
        return gr.update(visible=False), gr.update(visible=True), [(None, msg_inicial)], ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não encontrado."

with gr.Blocks() as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 RenovaIA")
        cpf_input = gr.Textbox(label="Digite seu CPF", placeholder="00000000000")
        btn_entrar = gr.Button("VERIFICAR OFERTAS")
        status = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        # 🚀 REMOVIDO O 'type="messages"' QUE CAUSOU O ERRO
        chatbot = gr.Chatbot(label="Chat de Negociação", height=500)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Sua mensagem...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", scale=2)

    btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    import os
    
    # 1. Garante limpeza total de portas
    gr.close_all()
    
    print("🚀 Servidor subindo...")
    
    # 2. Configurações otimizadas para o Colab
    demo.launch(
        share=True,      # Gera o link público (obrigatório no Colab)
        inline=True,     # Tenta mostrar o chat DENTRO do Colab (Plano B)
        debug=True,      # Mostra erros se o chat travar
        show_error=True  # Exibe erros da API na tela do chat
    )
