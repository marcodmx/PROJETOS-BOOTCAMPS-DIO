import os
import importlib
from interface.gradio_ui import criar_interface, MEU_CSS

# ==========================================================
# 1. Configuração de Inicialização
# ==========================================================
# Criamos a instância da interface chamando a função do gradio_ui.py
demo = criar_interface()

# ==========================================================
# 2. Execução do Servidor
# ==========================================================
if __name__ == "__main__":
    """
    Nota técnica: Passamos o MEU_CSS dentro do launch() para 
    evitar o UserWarning do Gradio 6.0+, garantindo que os 
    estilos de boleto e cores sejam injetados corretamente.
    """
    print("🚀 Iniciando o Portal RenovaIA...")
    
    demo.launch(
        css=MEU_CSS,            # Injeção de estilo recomendada
        debug=True,             # Mostra erros detalhados no console
        share=False,            # Mude para True se quiser gerar um link público
        show_error=True         # Exibe erros na interface para o usuário
    )
