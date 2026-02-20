from interface.gradio_ui import criar_interface

# ==========================================================
# Criação da interface
# ==========================================================
demo = criar_interface()  # variável expoável para Colab ou outros imports

# ==========================================================
# Execução direta
# ==========================================================
if __name__ == "__main__":
    demo.launch(
        share=True,   # necessário no Colab
        debug=True,
        prevent_thread_lock=True  # evita travamento de threads no notebook
    )
