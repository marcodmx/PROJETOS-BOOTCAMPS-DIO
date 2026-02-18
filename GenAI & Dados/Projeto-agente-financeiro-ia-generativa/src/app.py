import gradio as gr
import datetime
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

# Inicializa o motor
agente = AgenteNegociador()

def validar_e_avancar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), "⚠️ CPF incompleto."
    
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        hora = datetime.datetime.now().hour
        saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
        msg = f"### ✨ {saudacao}, {cliente['nome'].split()[0]}!\nLocalizamos seu cadastro."
        return gr.update(visible=False), gr.update(visible=True), msg
    return gr.update(visible=True), gr.update(visible=False), "❌ CPF não encontrado."

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Busca resposta da IA
    resposta_ia = agente.responder(mensagem, str(cliente))
    
    # FORMATO GRADIO 5: Lista de dicionários
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": resposta_ia})
    
    return historico, ""

css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.cpf-box input { font-size: 24px !important; text-align: center !important; font-weight: bold; }
"""

js_mask = """
() => {
    const applyMask = () => {
        const el = document.querySelector('#cpf_input input');
        if (el && !el.dataset.maskSet) {
            el.addEventListener('input', (e) => {
                let v = e.target.value.replace(/\D/g, '').slice(0, 11);
                if (v.length > 9) v = v.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
                else if (v.length > 6) v = v.replace(/^(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
                else if (v.length > 3) v = v.replace(/^(\d{3})(\d{1,3})/, "$1.$2");
                e.target.value = v;
            });
            el.dataset.maskSet = "true";
        }
    };
    setInterval(applyMask, 500);
}
"""

with gr.Blocks(css=css, theme=gr.themes.Soft(), js=js_mask) as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🤖 RenovaIA\n### Identifique-se para acessar suas ofertas")
        cpf_input = gr.Textbox(label="CPF", placeholder="000.000.000-00", elem_id="cpf_input", elem_classes="cpf-box")
        btn_verificar = gr.Button("🔍 CONSULTAR PENDÊNCIAS", variant="primary", size="lg")
        status_msg = gr.Markdown("", textAlign="center")

    with gr.Column(visible=False) as tela_chat:
        header_chat = gr.Markdown("")
        chatbot = gr.Chatbot(label="Atendimento", type="messages", height=450)
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Como posso ajudar?", show_label=False, scale=8)
            btn_send = gr.Button("Enviar", variant="primary", scale=2)

    btn_verificar.click(validar_e_avancar, [cpf_input], [tela_login, tela_chat, header_chat])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    demo.launch(share=True)
