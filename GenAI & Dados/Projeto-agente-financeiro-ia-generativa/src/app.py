import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types

# Inicializa o motor de negociação
agente = AgenteNegociador()

# Estilização do Portal
meu_css = """
.gradio-container { background-color: #f7fafc; font-family: sans-serif; }
.main-header { text-align: center; color: #2c5282; margin-bottom: 20px; }
"""

def extrair_texto(conteudo):
    """Normaliza o input do Gradio para o formato string esperado pelo Gemini."""
    if isinstance(conteudo, str): return conteudo
    if isinstance(conteudo, list) and len(conteudo) > 0:
        if isinstance(conteudo[0], dict): return conteudo[0].get('text', '')
        return str(conteudo[0])
    return str(conteudo)

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Prepara histórico convertendo para o formato do SDK do Gemini
    historico_ia = []
    for msg in historico:
        role_ia = "user" if msg['role'] == 'user' else "model"
        texto_limpo = extrair_texto(msg['content'])
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=texto_limpo)]))

    # Gatilhos para os botões de Ações Rápidas
    if "🔍 Verificar Ofertas" in mensagem:
        prompt_interno = "Gere uma proposta detalhada de quitação via Art. 52 CDC e uma opção de parcelamento com CET 1.99%."
        res = agente.responder(prompt_interno, str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso de pagamento registrado!** O prazo para baixa bancária é de até 72h úteis. Guarde seu comprovante."
    elif "🚪 Encerrar" in mensagem:
        res = "A RenovaIA agradece seu contato. Tenha um excelente dia! 👋"
    else:
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # Atualiza o Chatbot
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        # Saudação Humanizada: Sem citar leis ou burocracia no início
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Bem-vindo ao portal RenovaIA. Sou seu consultor virtual e estou aqui para facilitar sua negociação. Como posso te ajudar?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado. Verifique os dados."

# Construção da Interface
with gr.Blocks(title="RenovaIA - Portal Financeiro") as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 RenovaIA", elem_classes="main-header")
        gr.Markdown("### Identifique-se para acessar seu painel")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
        btn_entrar = gr.Button("ACESSAR PAINEL", variant="primary")
        status = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Consultor RenovaIA", height=550, type="messages")
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua dúvida ou proposta...", scale=8, show_label=False)
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
    # CSS injetado no launch para evitar Warnings no Gradio 6
    demo.launch(share=True, inline=False, debug=True, css=meu_css)
    
