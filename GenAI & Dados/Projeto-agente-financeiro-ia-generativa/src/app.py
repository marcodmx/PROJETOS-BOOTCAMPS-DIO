import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

agente = AgenteNegociador()

def validar_e_avancar(cpf_numeros):
    # Limpa o CPF para buscar no banco
    cpf_limpo = cpf_numeros.replace(".", "").replace("-", "").strip()
    
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), "⚠️ Digite os 11 números do CPF."
    
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        # Se achou, esconde a tela de login e mostra a tela de chat
        saudacao = f"Olá, {cliente['nome'].split()[0]}! Localizamos sua conta."
        return gr.update(visible=False), gr.update(visible=True), saudacao
    else:
        return gr.update(visible=True), gr.update(visible=False), "❌ CPF não localizado ou sem pendências."

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # --- ESTADO INTERNO ---
    cliente_atual = gr.State()

    # --- TELA 1: LOGIN / CPF ---
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("## 🏦 Portal de Renegociação RenovaIA")
        gr.Markdown("Digite seu CPF para consultar ofertas exclusivas.")
        
        with gr.Row(variant="panel"):
            cpf_input = gr.Textbox(
                label="CPF (apenas números)",
                placeholder="000.000.000-00",
                max_length=14,
                container=False,
                autofocus=True,
                elem_id="cpf_box"
            )
        
        btn_verificar = gr.Button("🔍 VERIFICAR PENDÊNCIAS", variant="primary", size="lg")
        msg_erro = gr.Markdown("")

    # --- TELA 2: CHAT (Inicia Escondida) ---
    with gr.Column(visible=False) as tela_chat:
        saudacao_header = gr.Markdown("### ✨ Bem-vindo")
        
        chatbot = gr.Chatbot(label="Atendimento RenovaIA", height=450)
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Como posso te ajudar com sua dívida?",
                show_label=False,
                scale=9
            )
            btn_enviar = gr.Button("Enviar", scale=1)
        
        gr.Examples(
            examples=["Quais são minhas opções?", "Quero um desconto à vista", "Posso parcelar?"],
            inputs=msg_input
        )

    # --- LÓGICA DE TRANSIÇÃO ---
    # Ao clicar ou dar Enter no CPF
    btn_verificar.click(
        validar_e_avancar, 
        inputs=[cpf_input], 
        outputs=[tela_login, tela_chat, saudacao_header]
    )
    cpf_input.submit(
        validar_e_avancar, 
        inputs=[cpf_input], 
        outputs=[tela_login, tela_chat, saudacao_header]
    )

    # Lógica do Chat
    def chat_fluxo(mensagem, historico, cpf):
        cliente = buscar_cliente_por_cpf(cpf)
        resposta = agente.responder(mensagem, str(cliente))
        historico.append((mensagem, resposta))
        return historico, ""

    btn_enviar.click(chat_fluxo, [msg_input, chatbot, cpf_input], [chatbot, msg_input])
    msg_input.submit(chat_fluxo, [msg_input, chatbot, cpf_input], [chatbot, msg_input])

if __name__ == "__main__":
    demo.launch(share=True)
