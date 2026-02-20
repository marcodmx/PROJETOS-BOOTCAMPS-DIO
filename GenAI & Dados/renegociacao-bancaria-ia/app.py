# app.py
from interface.gradio_ui import criar_interface

# ==========================================================
# Criação da interface
# ==========================================================
demo = criar_interface()  # variável global para importação

if __name__ == "__main__":
    # Lança a interface apenas quando rodar app.py diretamente
    demo.launch()
