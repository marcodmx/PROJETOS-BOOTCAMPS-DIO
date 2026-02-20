import importlib
from interface.gradio_ui import criar_interface, MEU_CSS

# Criamos a interface
demo = criar_interface()

if __name__ == "__main__":
    print("🚀 Iniciando Banco RenovaIA v2...")
    
    # O CSS deve ser passado aqui para evitar Warnings e funcionar na v6
    demo.launch(
        css=MEU_CSS, 
        debug=True,
        show_error=True
    )
