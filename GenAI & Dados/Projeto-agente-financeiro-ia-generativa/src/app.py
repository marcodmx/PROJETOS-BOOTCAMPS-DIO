import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types

agente = AgenteNegociador()
meu_css = ".gradio-container { background-color: #f7fafc; } .main-header { text-align: center; color: #2c5282; font-weight: bold; }"

def extrair_texto(conteudo):
    if isinstance(conteudo, str): return conteudo
    if isinstance(conteudo, list) and len(conteudo) > 0:
        if isinstance(conteudo[0], dict): return conteudo[0].get('text', '')
        return str(conteudo[0])
    return str(conteudo)

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Prepara histórico para a IA
    historico_ia = []
    if historico:
        for msg in historico:
            role_ia = "user" if msg['role'] == 'user' else "model"
            texto_limpo = extrair_texto(msg['content'])
            historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto_limpo)]))

    # Lógica de decisão: IA ou Resposta Fixa
    if "🔍 Verificar Ofertas" in mensagem:
        # Aqui ele chama a IA e pode cair na 'fila de processamento' se não houver cota
        res = agente.responder("Gere proposta de quitação Art. 52 CDC e parcelamento 1.99% CET.", str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        # Aqui a resposta é imediata, por isso funcionou para você!
        res = "✍️ **Aviso de pagamento registrado!** O prazo de compensação e baixa no sistema é de até 72h úteis. Por favor, guarde seu comprovante."
    elif "🚪 Encerrar" in mensagem:
        res = "Obrigado por utilizar o Portal RenovaIA. Sua sessão será encerrada com segurança. Até breve!"
    else:
        # Qualquer outra conversa vai para a IA
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor virtual RenovaIA. Como posso ajudar com sua saúde financeira hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado. Tente novamente."

with gr.Blocks(title="RenovaIA", css=meu_css) as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 RenovaIA", elem_classes="main-header")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
        btn_entrar = gr.Button("ACESSAR PAINEL", variant="primary")
        status = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Atendimento", height=550)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Fale comigo ou use as ações rápidas...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        gr.Examples(examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar"], inputs=txt_msg)

    btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    gr.close_all()
    demo.launch(share=True, inline=False, debug=True)
