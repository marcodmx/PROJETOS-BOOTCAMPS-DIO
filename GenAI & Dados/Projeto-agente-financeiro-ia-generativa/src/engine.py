import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: 
            raise ValueError("Chave de API não encontrada no .env!")
        
        self.client = genai.Client(api_key=api_key)
        
        # 🎯 FORÇANDO 1.5-FLASH: O 2.0 está sem cota (429) para contas free.
        # O ID "gemini-1.5-flash" é o mais estável e evita o erro 404.
        self.model_id = "gemini-1.5-flash"
        print(f"✅ MOTOR DE ESTABILIDADE ATIVO: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o Consultor Sênior de Saúde Financeira da RenovaIA. CLIENTE: {dados_cliente}
        
        ### ⚖️ DIRETRIZES LEGAIS:
        - Informe sempre o CET de 1.99% a.m. para qualquer parcelamento.
        - Cite o Art. 52 do CDC sobre o direito ao desconto na antecipação de parcelas.
        
        ### 📋 FORMATAÇÃO DO BOLETO:
        Se o cliente aceitar o acordo, envie o código EXATAMENTE assim:
        ```
        23790.12345 60000.789012 34567.890123 1 95000000185000
        ```
        
        ### 🎭 UX:
        Seja empático, use emojis e foque na solução do problema.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.1 # Baixa temperatura para cálculos mais precisos
                ),
                contents=historico_formatado + [
                    types.Content(role="user", parts=[types.Part(text=mensagem)])
                ]
            )
            
            if response and response.text:
                return response.text
            return "João, tive um pequeno atraso no processamento. Pode repetir?"

        except Exception as e:
            print(f"🚨 LOG TÉCNICO: {str(e)}")
            if "429" in str(e):
                return "⚠️ O sistema está com muitas requisições. Aguarde 10 segundos e tente enviar novamente."
            return "⚠️ Erro de conexão. Por favor, tente de novo."
            
