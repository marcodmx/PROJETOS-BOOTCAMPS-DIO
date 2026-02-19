import gradio as gr
from database import buscar_cliente_por_cpf
from engine import AgenteNegociador
# ESSA LINHA ABAIXO É A QUE FALTAVA:
from google.genai import types 

agente = AgenteNegociador()

def responder_chat(mensagem, historico, cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)

    # Agora o 'types' será reconhecido aqui:
    historico_ia = []
    for turno in historico:
        role_ia = "user" if turno['role'] == 'user' else "model"
        # Criando o objeto que o Google exige para não dar erro de validação
        historico_ia.append(types.Content(role=role_ia, parts=[types.Part(text=turno['content'])]))

    if "Já efetuei o pagamento" in mensagem:
        res = "✨ **Recebemos sua informação!** Agora é só aguardar a compensação bancária. 🙏"
    elif "Encerrar Atendimento" in mensagem:
        res = "A **RenovaIA** agradece o contato. Até logo! ✨"
    else:
        # Chama o motor passando a mensagem, dados e o histórico convertido
        res = agente.responder(mensagem, str(cliente), historico_ia)
    
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": res})
    return historico, ""

# ... restante do código (validar_e_entrar e Blocks) permanece igual ...
def validar_e_entrar(cpf_com_mascara):
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    if cliente:
        nome = cliente['nome'].split()[0]
        hist_inicial = [{"role": "assistant", "content": f"✨ **Olá, {nome}!** Encontrei ótimas ofertas para você hoje. Vamos conferir?"}]
        return gr.update(visible=False), gr.update(visible=True), hist_inicial, ""
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ CPF inválido."

with gr.Blocks() as demo:
    with gr.Column(visible=True) as tela_login:
        gr.Markdown("# 🏦 RenovaIA")
        cpf_input = gr.Textbox(label="CPF")
        btn_verificar = gr.Button("ENTRAR")
        status_msg = gr.Markdown("")

    with gr.Column(visible=False) as tela_chat:
        chatbot = gr.Chatbot(label="Chat", height=500)
        txt_msg = gr.Textbox(placeholder="Digite aqui...")
        btn_send = gr.Button("Enviar")

    btn_verificar.click(validar_e_entrar, [cpf_input], [tela_login, tela_chat, chatbot, status_msg])
    btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

if __name__ == "__main__":
    demo.launch(share=True)
