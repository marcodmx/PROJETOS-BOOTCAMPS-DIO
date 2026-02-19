import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types

# Inicializa o motor
agente = AgenteNegociador()

# CSS Customizado para o Portal
meu_css = """
.gradio-container { background-color: #f0f2f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.main-header { text-align: center; color: #1a365d; }
.login-area { max-width: 400px; margin: 0 auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
"""

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Converte histórico para o formato do SDK Gemini
    historico_ia = []
    for msg in historico:
        role_ia = "user" if msg['role'] == 'user' else "model"
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=msg['content'])]))

    # Lógica de Botões/Ações Rápidas
    if "🔍 Verificar Ofertas" in mensagem:
        res = agente.responder("O cliente solicitou ver as ofertas disponíveis. Liste as opções conforme as regras de CET.", str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Aviso recebido!** Por favor, guarde seu comprovante. O prazo de compensação bancária é de até 72h úteis. Assim que compensado, seu nome será removido dos cadastros restritivos em até 5 dias úteis."
    elif "🚪 Encerrar Atendimento" in mensagem:
        res = "A RenovaIA agradece seu contato. Esperamos ter ajudado na sua jornada financeira. Até logo! 👋"
    elif "❓ Ajuda" in mensagem:
        res = "🆘 **Central de Ajuda:** Se você tiver dúvidas técnicas, ligue para 0800-RENOVA. Para propostas, pode falar diretamente comigo aqui!"
    else:
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # Atualiza o histórico no formato exigido pelo Gradio (Dicionários)
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Sou seu consultor RenovaIA. Analisei seu perfil e tenho propostas com base no Art. 52 do CDC. Como posso te ajudar hoje?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não cadastrado ou inválido."

with gr.Blocks(title="RenovaIA - Portal de Negociação") as demo:
    with gr.Column(visible=True, elem_id="login-area") as tela_login:
        gr.Markdown("# 🏦 RenovaIA", elem_classes="main-header")
        gr.Markdown("### Identifique-se para acessar suas ofertas exclusivas")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00")
        btn_entrar = gr.Button("ACESSAR MINHAS OFERTAS", variant="primary")
        status = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        gr.Markdown("## 🤝 Mesa de Negociação Digital")
        chatbot = gr.Chatbot(label="Atendente RenovaIA", height=500)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua mensagem...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        gr.Examples(
            examples=["🔍 Verificar Ofertas", "✅ Já efetuei o pagamento", "🚪 Encerrar Atendimento", "❓ Ajuda"], 
            inputs=txt_msg,
            label="Ações Rápidas"
        )

    btn_entrar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    gr.close_all()
    # No Gradio 6.0, o CSS deve ser passado aqui para evitar Warnings
    demo.launch(share=True, inline=False, debug=True, css=meu_css)
