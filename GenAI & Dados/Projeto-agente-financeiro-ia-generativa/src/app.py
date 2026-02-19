import gradio as gr
import datetime
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador

agente = AgenteNegociador()

def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "⚠️ CPF incompleto."
    
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        hora = datetime.datetime.now().hour
        saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
        nome = cliente['nome'].split()[0]
        
        # MENSAGEM COM EMOJI DE BANCO 🏦
        historico_inicial = [
            {"role": "assistant", "content": f"🏦 **{saudacao}, {nome}! Bem-vindo ao portal de negociação.**\n\nLocalizei sua pendência referente ao produto **{cliente.get('produto', 'Crédito')}**. Sou o **RenovaIA** e estou aqui para facilitar sua quitação com as melhores taxas. 💰\n\nComo posso te ajudar agora?"}
        ]
        
        return gr.update(visible=False), gr.update(visible=True), historico_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "❌ CPF não localizado em nossa base."

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    resposta_ia = agente.responder(mensagem, str(cliente))
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": resposta_ia})
    return historico, ""

# CSS Azul Bancário (Premium)
css = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.gradio-container { background-color: #f7fafc !important; }
.cpf-box { background: white; padding: 30px; border-radius: 20px; border-top: 5px solid #2b6cb0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.cpf-box input { font-size: 28px !important; text-align: center !important; font-weight: bold; color: #1a365d; }
.btn-banco { background: #2b6cb0 !important; border: none !important; color: white !important; font-weight: bold !important; }
.title-bank { color: #1a365d; text-align: center; font-size: 2.5em; margin-bottom: 0.5em; }
"""

js_mask = r"""
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
        gr.Markdown("# 🏦 RenovaIA", elem_classes="title-bank")
        gr.Markdown("### Acesse seu painel de negociação seguro", textAlign="center")
        
        with gr.Column(elem_classes="cpf-box"):
            cpf_input = gr.Textbox(label="Informe seu CPF para continuar", placeholder="000.000.000-00", elem_id="cpf_input")
            btn_verificar = gr.Button("VERIFICAR MINHAS OFERTAS 📈", variant="primary", elem_classes="btn-banco")
            status_msg = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        gr.Markdown("## 🏦 Atendimento RenovaIA", elem_classes="title-bank")
        chatbot = gr.Chatbot(label="Chat Seguro", type="messages", height=550)
        
        with gr.Row():
            txt_msg = gr.Textbox(placeholder="Digite sua dúvida aqui...", show_label=False, scale=8)
            btn_send = gr.Button("Enviar 🚀", variant="primary", scale=2, elem_classes="btn-banco")
        
        gr.Examples(
            examples=["Quais são minhas dívidas?", "Quero desconto à vista", "Opções de parcelamento"],
            inputs=txt_msg
        )

    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
    txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    demo.launch(share=True)
