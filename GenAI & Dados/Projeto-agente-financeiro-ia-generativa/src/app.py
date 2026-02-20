import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicialização do motor Groq (sem Gemini!)
agente = AgenteNegociador()

# CSS moderno para o portal que você definiu
meu_css = """
.gradio-container { background-color: #f7fafc; }
.main-header { text-align: center; color: #2c5282; font-weight: bold; margin-bottom: 10px; }
"""

def formatar_historico_groq(historico_gradio):
    """Converte o histórico do Gradio para o padrão Role/Content da Groq."""
    novo_historico = []
    if historico_gradio:
        for msg in historico_gradio:
            # Gradio usa 'user' e 'assistant' (ou o formato antigo de lista)
            role = "user" if msg['role'] == 'user' else "assistant"
            novo_historico.append({"role": role, "content": msg['content']})
    return novo_historico

def responder_chat(mensagem, historico, cpf_com_mascara):
    """Lógica de atendimento RenovaIA."""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # 1. Converte histórico para o formato Groq
    historico_ia = formatar_historico_groq(historico)

    # 2. Lógica de Ações Rápidas vs Inteligência Artificial
    if "🔍 Verificar Ofertas" in mensagem:
        # Removido menção ao Art. 52 a pedido seu, mantendo foco em quitação/parcelamento
        comando = "Gere uma proposta de quitação com desconto máximo e uma de parcelamento com taxa de 1.99% a.m."
        res = agente.responder(comando, str(cliente), historico_ia)
    
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso de pagamento registrado!** O prazo para baixa bancária é de até 72h úteis. Guarde seu comprovante."
    
    elif "🚪 Encerrar" in mensagem:
        res = "A RenovaIA agradece seu contato. Sua sessão foi encerrada. Até breve! 👋"
    
    else:
        # Resposta fluida da IA via Groq
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # 3. Atualiza o histórico para o componente Chatbot
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    """Valida o cliente e faz a transição de telas."""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor virtual RenovaIA. Como posso ajudar com sua saúde financeira hoje?"}]
        # Oculta login, mostra chat, limpa status
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não identificado. Tente novamente."

# Interface Blocks (Estrutura visual preservada)
with gr.Blocks(title="RenovaIA", css=meu_css) as demo:
    
    # TELA DE LOGIN
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
        cpf_input = gr.Textbox(label="Informe seu CPF", placeholder="000.000.000-00")
        btn_entrar = gr.Button("ACESSAR MEU PAINEL", variant="primary")
        status = gr.Markdown("")

    # TELA DE CHAT
    with gr.Column(visible=False) as tela_chat:
        gr.Markdown("## 💬 Atendimento Digital")
        chatbot = gr.Chatbot(label="RenovaIA", height=550, type="messages")
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua mensagem...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        gr.Examples(
            examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar"], 
            inputs=txt_msg,
            label="Ações Rápidas"
        )

    # EVENTOS
    btn_entrar.click(
        validar_e_entrar, 
        [cpf_input], 
        [tela_login, tela_chat, chatbot, status]
    )
    
    btn_send.click(
        responder_chat, 
        [txt_msg, chatbot, cpf_input], 
        [chatbot, txt_msg]
    )
    
    txt_msg.submit(
        responder_chat, 
        [txt_msg, chatbot, cpf_input], 
        [chatbot, txt_msg]
    )

if __name__ == "__main__":
    gr.close_all()
    # Launch sem Warnings desnecessários
    demo.launch(share=True, debug=True)
