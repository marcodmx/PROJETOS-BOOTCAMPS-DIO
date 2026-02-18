import gradio as gr
import datetime
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

agente = AgenteNegociador()

# --- Lógica de Negócio ---
def validar_e_avancar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), "⚠️ CPF incompleto."
    
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        hora = datetime.datetime.now().hour
        saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
        msg = f"### ✨ {saudacao}, {cliente['nome'].split()[0]}!\nLocalizamos seu cadastro com sucesso."
        return gr.update(visible=False), gr.update(visible=True), msg
    else:
        return gr.update(visible=True), gr.update(visible=False), "❌ CPF não encontrado em nossa base."

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Chama o motor da IA
    resposta_ia = agente.responder(mensagem, str(cliente))
    
    # Formato moderno exigido pelo Gradio 5+ (Lista de Dicionários)
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": resposta_ia})
    
    return historico, ""

# --- Interface Customizada ---
css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
body, .gradio-container { font-family: 'Inter', sans-serif !important; }
.cpf-box input { 
    font-size: 24px !important; 
    text-align: center !important; 
    letter-spacing: 2px;
    font-weight: bold;
}
.title-text { text-align: center; margin-bottom: 30px; }
"""

# JavaScript para Máscara de CPF em Tempo Real
js_mask = """
() => {
    const selector = '#cpf_input input';
    setInterval(() => {
        const el = document.querySelector(selector);
        if (el && !el.dataset.maskSet) {
            el.addEventListener('input', (e) => {
                let v = e.target.value.replace(/\D/g, '');
                if (v.length > 11) v = v.slice(0, 11);
                if (v.length > 9) v = v.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
                else if (v.length > 6) v = v.replace(/^(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
                else if (v.length > 3) v = v.replace(/^(\d{3})(\d{1,3})/, "$1.$2");
                e.target.value = v;
            });
            el.dataset.maskSet = "true";
        }
    }, 500);
}
"""

with gr.Blocks(css=css, theme=gr.themes.Soft(), js=js_mask) as demo:
    
    # Tela de Identificação
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🤖 RenovaIA", elem_classes="title-text")
        gr.Markdown("### Identifique-se para acessar suas ofertas", elem_classes="title-text")
        
        with gr.Row():
            cpf_input = gr.Textbox(
                label="CPF", 
                placeholder="000.000.000-00", 
                elem_id="cpf_input",
                elem_classes="cpf-box",
                container=True
            )
        
        btn_verificar = gr.Button("🔍 CONSULTAR PENDÊNCIAS", variant="primary", size="lg")
        status_msg = gr.Markdown("", textAlign="center")

    # Tela de Chat (Inicia Oculta)
    with gr.Column(visible=False) as tela_chat:
        header_chat = gr.Markdown("")
        
        # Chatbot usando formato de mensagens moderno
        chatbot = gr.Chatbot(label="RenovaIA Atendimento", type="messages", height=500)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua dúvida aqui...", show_label=False, scale=8)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)

    # Eventos de Transição
    btn_verificar.click(
        validar_e_avancar, 
        inputs=[cpf_input], 
        outputs=[tela_login, tela_chat, header_chat]
    )
    
    # Eventos do Chat
    btn_send.click(
        responder_chat, 
        inputs=[txt_msg, chatbot, cpf_input], 
        outputs=[chatbot, txt_msg]
    )
    txt_msg.submit(
        responder_chat, 
        inputs=[txt_msg, chatbot, cpf_input], 
        outputs=[chatbot, txt_msg]
    )

if __name__ == "__main__":
    demo.launch(share=True)
