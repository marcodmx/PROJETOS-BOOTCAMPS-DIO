import gradio as gr
import os
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
from google.genai import types

agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    nome_cliente = cliente['nome'].split()[0] if cliente else "Cliente"
    
    # 1. Converte histórico do Gradio (Dicionários) para o Gemini (Parts)
    historico_ia = []
    for msg in historico:
        role_ia = "user" if msg['role'] == 'user' else "model"
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=msg['content'])]))

    # 2. Gatilhos de Ações Rápidas (Os botões que você gosta)
    if "🔍 Verificar Ofertas" in mensagem:
        prompt_especifico = "O cliente clicou em verificar ofertas. Apresente as opções de parcelamento com CET de 1.99% e mencione o Art. 52 do CDC."
        res = agente.responder(prompt_especifico, str(cliente), historico_ia)
    elif "✅ Já efetuei o pagamento" in mensagem:
        res = "✍️ **Confirmado!** Recebemos seu aviso de pagamento. O prazo para baixa no sistema e nos órgãos de proteção ao crédito é de até 3 dias úteis. 🙌"
    elif "🚪 Encerrar Atendimento" in mensagem:
        res = f"Foi um prazer te ajudar, {nome_cliente}! ✅ **Por favor, digite uma nota de 1 a 10** para o meu atendimento. A RenovaIA agradece!"
    elif "❓ Ajuda" in mensagem:
        res = "🆘 **Suporte RenovaIA:** SAC 0800 777 0000 | Atendimento das 08h às 20h."
    else:
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    # 3. Formato de dicionário que seu Gradio EXIGE
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    
    return historico, ""

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        msg_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Bem-vindo à RenovaIA. Sou seu consultor especialista em saúde financeira. Vamos regularizar sua situação hoje? 🤝"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF não localizado no sistema."

# CSS para deixar o visual mais "Premium"
meu_css = """
.gradio-container { background-color: #f7fafc; }
.main-header { text-align: center; color: #2b6cb0; margin-bottom: 20px; }
"""

with gr.Blocks(title="RenovaIA - Negociação Especializada", css=meu_css) as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 RenovaIA", elem_classes="main-header")
        gr.Markdown("### Acesse seu portal de negociação segura")
        cpf_input = gr.Textbox(label="Seu CPF", placeholder="000.000.000-00")
        btn_entrar = gr.Button("ENTRAR NO PORTAL", variant="primary")
        status = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        gr.Markdown("## 🤝 Central de Negociação")
        chatbot = gr.Chatbot(label="Consultor RenovaIA", height=550)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua proposta ou dúvida...", scale=8, show_label=False)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)
        
        # OS BOTÕES TOP VOLTARAM AQUI:
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
    # share=True para o link externo, inline=False para não poluir o notebook
    demo.launch(share=True, inline=False, debug=True)
