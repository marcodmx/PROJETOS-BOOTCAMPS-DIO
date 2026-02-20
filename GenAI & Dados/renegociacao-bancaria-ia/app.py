import os
import importlib
from interface.gradio_ui import criar_interface, MEU_CSS

# ============================================================
# 1. PREPARAÇÃO DO AMBIENTE
# ============================================================
# Dica: Certifique-se de que a variável GROQ_API_KEY esteja 
# configurada no seu ambiente operacional antes de rodar.

# ============================================================
# 2. INICIALIZAÇÃO DA INTERFACE
# ============================================================
# Chamamos a função que constrói os blocos do Gradio
demo = criar_interface()

# ============================================================
# 3. LANÇAMENTO DO SERVIDOR
# ============================================================
if __name__ == "__main__":
    """
    Execução do servidor Gradio.
    Passamos o MEU_CSS aqui para evitar o 'UserWarning' das versões 
    mais recentes e garantir que o design do Banco RenovaIA seja aplicado.
    """
    print("🚀 Servidor Banco RenovaIA iniciando...")
    
    demo.launch(
        css=MEU_CSS,            # Aplica o estilo customizado (Boleto, Cores, Fontes)
        debug=True,             # Ativa log detalhado para facilitar correções
        show_error=True,        # Exibe mensagens de erro amigáveis na UI
        server_name="0.0.0.0",  # Permite acesso externo se necessário
        quiet=False             # Mantém o log de inicialização visível
    )
