from interface.gradio_ui import criar_interface, MEU_CSS

# ==========================================================
# Criação da interface
# ==========================================================
# Criamos a interface chamando a função do arquivo gradio_ui.py
demo = criar_interface()

if __name__ == "__main__":
    # Lançamos com o CSS aqui para evitar o Warning do Gradio e share=True para o Colab
    demo.launch(css=MEU_CSS, share=True)
