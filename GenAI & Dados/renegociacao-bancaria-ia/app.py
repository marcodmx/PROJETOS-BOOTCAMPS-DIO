from interface.gradio_ui import criar_interface, MEU_CSS

demo = criar_interface()

if __name__ == "__main__":
    print("🚀 Banco RenovaIA Online!")
    demo.launch(css=MEU_CSS, debug=True)
