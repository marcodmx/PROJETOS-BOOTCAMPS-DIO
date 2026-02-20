import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicialização do motor Groq
agente = AgenteNegociador()

# CSS moderno para o portal
meu_css = """
.gradio-container { background-color: #f7fafc; }
.main-header { text-align: center; color: #2c5282; font-weight: bold; margin-bottom: 10px; }
"""

def formatar_historico_groq(historico_gradio):
    """Converte o histórico do Gradio para o padrão Role/Content da Groq."""
    novo_historico = []
    if historico_gradio:
        for user_msg, bot_msg in historico_gradio:
            if user_msg:
                novo_historico.append({"role": "user", "content": user_msg})
            if bot_msg:
                novo_historico.append({"role": "assistant", "content": bot_msg})
    return novo_historico

def responder_chat(mensagem, historico, cpf_com_mascara):
    """Lógica de atendimento RenovaIA."""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # 1. Converte histórico (formato lista de listas do Gradio antigo/padrão)
    historico_ia = formatar_historico_groq(historico)

    # 2. Lógica de Ações Rápidas vs IA
    if "🔍 Verificar Ofertas" in mensagem:
        comando = "Gere uma proposta de quitação com desconto máximo e uma de parcelamento com taxa de 1.99% a.m."
        res = agente.responder(comando, str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso de pagamento registrado!** O prazo para baixa bancária é de até 72h úteis. Guarde seu comprovante."
    elif "🚪 Encerrar" in mensagem:
        res = "A RenovaIA agradece seu contato. Sua sessão foi encerrada. Até breve! 👋"
    else:
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # 3. Atualiza o histórico
    historico.append((mensagem, res))
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    """Valida o cliente e faz a transição de telas."""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        # Mensagem inicial formatada para o Chatbot padrão (lista de listas)
        msg_inicial = [[None, f"✨ **Olá, {nome}!** Sou seu consultor virtual RenovaIA. Como posso ajudar com sua saúde financeira hoje?"]]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado. Tente novamente."

# Interface Blocks
with gr.Blocks(title="RenovaIA") as demo:
    
    # TELA DE LOGIN
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
        cpf_input = gr.Textbox(label="Informe seu CPF", placeholder="000.000.000-00")
        btn_entrar = gr.Button("ACESSAR MEU PAINEL", variant="primary")
        status = gr.Markdown("")

    # TELA DE CHAT
    with gr.Column(visible=False) as tela_chat:
        gr.Markdown("## 💬 Atendimento Digital")
        # REMOVIDO type="messages" para evitar o TypeError
        chatbot = gr.Chatbot(label="RenovaIA", height=550)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua mensagem...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        gr.Examples(
            examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar"], 
            inputs=txt_msg,
            label="Ações Rápidas"
        )

    # EVENTOS
    btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    gr.close_all()
    # CSS movido para o launch() conforme aviso do Gradio 6
    demo.launch(share=True, debug=True, css=meu_css)
