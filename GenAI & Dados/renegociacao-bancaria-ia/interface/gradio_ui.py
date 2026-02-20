import gradio as gr
import random
from core.database import buscar_cliente_por_cpf
from core.engine import AgenteNegociador

# Inicializa o motor da IA
agente = AgenteNegociador()

TITULOS_IA = ["✨ Sua Jornada Financeira", "🚀 Rumo ao Azul", "🤝 Vamos resolver?"]

# Estilização completa para botões, cores e blocos de código (boleto)
MEU_CSS = """
.gradio-container { background-color: #f8fafc !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; color: #0f172a; font-weight: 800; font-size: 32px; padding: 20px; }
.action-btn { font-weight: 700 !important; margin-bottom: 12px !important; }
.error-msg { color: #dc2626 !important; font-weight: 600 !important; text-align: center; margin-top: 10px; }

/* Destaque para valores monetários */
span[style*="font-size: 20px"] {
    background-color: #eff6ff;
    padding: 2px 6px;
    border-radius: 4px;
}

/* Formatação do bloco de código para o botão 'Copiar' funcionar bem */
.prose pre {
    background-color: #f1f5f9 !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 12px !important;
}
"""

def validar_e_entrar(cpf_com_mascara):
    """Valida o login e prepara a saudação inicial suave."""
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    
    if len(cpf_limpo) != 11:
        return gr.update(visible=True), gr.update(visible=False), None, "### ⚠️ Atenção: Digite os 11 números do seu CPF."

    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    if cliente:
        nome = cliente.get('nome', 'Cliente').split()[0]
        # Pega a primeira dívida da lista para a saudação
        dividas = cliente.get('dividas', [])
        produto = dividas[0].get('produto', 'crédito') if dividas else "crédito"
        
        # Inicia o chat com formato de dicionário (padrão Gradio 5+)
        msg_inicial = [{"role": "assistant", "content": f"👋 Olá, {nome}! Que bom ter você aqui. Encontrei uma excelente oportunidade para seu {produto}. Como posso te ajudar?"}]
        return gr.update(visible=False), gr.update(visible=True), msg_inicial, ""
    
    return gr.update(visible=True), gr.update(visible=False), None, "### ❌ Erro: CPF não localizado em nossa base."

def responder_chat(mensagem, historico, cpf_com_mascara):
    """Gerencia a negociação evolutiva enviando contexto limpo para a IA."""
    if not mensagem: return historico, ""
    
    cpf_limpo = "".join(filter(str.isdigit, cpf_com_mascara))
    cliente = buscar_cliente_por_cpf(cpf_limpo)
    
    # Extrai apenas os dados essenciais da primeira dívida para não confundir a IA
    divida_ativa = cliente.get('dividas', [{}])[0] if cliente else {}
    contexto_ia = {
        "cliente": cliente.get("nome"),
        "produto": divida_ativa.get("produto"),
        "valor_total": divida_ativa.get("valor_total_atualizado"),
        "oferta_vista": divida_ativa.get("oferta_minima_avista"),
        "boleto": divida_ativa.get("codigo_boleto_atual"),
        "instituicao": "Banco RenovaIA S.A.",
        "prazo_baixa": "3 dias úteis"
    }

    # Garante que o histórico seja uma lista (mesmo que vazia)
    historico = historico or []
    
    # Chama a IA enviando o contexto mastigado e o histórico de mensagens
    resposta_ia = agente.responder(mensagem, str(contexto_ia), historico)
    
    # Atualiza o histórico visual com o novo par de mensagens
    historico.append({"role": "user", "content": mensagem})
    historico.append({"role": "assistant", "content": resposta_ia})
    
    return historico, ""

def criar_interface():
    """Constrói a estrutura visual do Portal."""
    titulo_sessao = random.choice(TITULOS_IA)
    
    with gr.Blocks(title="RenovaIA Pro") as demo:
        # TELA 01: LOGIN
        with gr.Column(visible=True) as tela_login:
            gr.Markdown("# 🏦 Portal RenovaIA", elem_classes="main-header")
            cpf_input = gr.Textbox(label="CPF", placeholder="Apenas números", max_lines=1)
            btn_entrar = gr.Button("ACESSAR", variant="primary")
            status_login = gr.Markdown("", elem_classes="error-msg")

        # TELA 02: NEGOCIAÇÃO
        with gr.Column(visible=False) as tela_chat:
            with gr.Row():
                with gr.Column(scale=8):
                    gr.Markdown(f"## {titulo_sessao}")
                with gr.Column(scale=1, min_width=100):
                    btn_sair = gr.Button("Sair 🚪", variant="secondary")

            with gr.Row():
                with gr.Column(scale=4):
                    # Chatbot configurado para mensagens dinâmicas
                    chatbot = gr.Chatbot(label="Consultor Virtual", height=550, sanitize_html=False)
                    with gr.Row():
                        txt_msg = gr.Textbox(placeholder="Escreva aqui sua dúvida ou proposta...", scale=8, show_label=False)
                        btn_send = gr.Button("Enviar", variant="primary", scale=2)
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚡ Ações Rápidas")
                    btn_ofertas = gr.Button("🔍 Minha Solução", elem_classes="action-btn")
                    btn_desc = gr.Button("📉 Propor Valor", elem_classes="action-btn")
                    btn_boleto = gr.Button("📄 Gerar Boleto", elem_classes="action-btn")

        # MAPEAMENTO DE EVENTOS
        btn_entrar.click(
            validar_e_entrar, 
            [cpf_input], 
            [tela_login, tela_chat, chatbot, status_login]
        )
        
        btn_sair.click(
            lambda: (gr.update(visible=True), gr.update(visible=False), None, ""), 
            None, 
            [tela_login, tela_chat, chatbot, status_login]
        )
        
        btn_send.click(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])
        txt_msg.submit(responder_chat, [txt_msg, chatbot, cpf_input], [chatbot, txt_msg])

        # Atalhos de Negociação
        btn_ofertas.click(lambda h, c: responder_chat("Quais são as condições e o CET para meu caso?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_desc.click(lambda h, c: responder_chat("Gostaria de propor um valor diferente para quitação.", h, c), [chatbot, cpf_input], [chatbot, txt_msg])
        btn_boleto.click(lambda h, c: responder_chat("Pode me enviar o código do boleto?", h, c), [chatbot, cpf_input], [chatbot, txt_msg])

    return demo
