import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: raise ValueError("GOOGLE_API_KEY não encontrada!")
        self.client = genai.Client(api_key=api_key)
        
        # Forçamos o modelo estável para evitar erros de permissão em modelos experimentais
        self.model_id = "gemini-1.5-flash"
        print(f"✅ Motor Ativo: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o Consultor Sênior de Saúde Financeira da RenovaIA. CLIENTE: {dados_cliente}
        
        ### ⚖️ REGRAS LEGAIS:
        - Informe CET de 1.99% a.m. para parcelamentos.
        - Cite o Art. 52 do CDC sobre amortização de juros.
        
        ### 📋 BOLETO:
        Use blocos de código markdown para o código de barras:
        ```
        23790.12345 60000.789012 34567.890123 1 95000000185000
        ```
        """
        
        try:
            # A correção: Unificamos o histórico e a nova mensagem em uma lista limpa de Parts
            # Isso evita que a API se confunda com formatos de dicionário do Gradio
            conteudo_atual = types.Content(
                role="user", 
                parts=[types.Part(text=mensagem)]
            )
            
            # Chamada usando o método generate_content que é mais estável que o chat.send_message em loops
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2
                ),
                contents=historico_formatado + [conteudo_atual]
            )
            
            if response.text:
                return response.text
            else:
                return "⚠️ A IA não conseguiu gerar uma resposta. Tente reformular."

        except Exception as e:
            # Esse print aparecerá no console do seu VS Code / Colab para sabermos o motivo real
            print(f"🚨 ERRO NA API GEMINI: {str(e)}")
            return "⚠️ Erro técnico de conexão. Por favor, tente novamente em alguns segundos."
