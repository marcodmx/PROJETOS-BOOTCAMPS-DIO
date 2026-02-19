import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não configurada!")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = None
        
        try:
            modelos = [m.name for m in self.client.models.list()]
            # Preferência pelo 2.0-flash que o seu ambiente já detectou
            self.model_id = "gemini-2.0-flash" if any("gemini-2.0-flash" in m for m in modelos) else "gemini-1.5-flash"
            print(f"✅ Motor calibrado com: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-2.0-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # A lei entra apenas no fechamento, não na saudação.
        prompt_sistema = (
            f"Você é o consultor sênior da RenovaIA. Dados do Cliente: {dados_cliente}. "
            f"DIRETRIZES DE NEGOCIAÇÃO: "
            f"1. Seja cordial, humano e empático. Não cite leis na recepção. "
            f"2. Se o cliente pedir propostas, valores ou boletos, aplique o Artigo 52 do CDC. "
            f"3. O Art. 52 garante desconto proporcional dos juros para liquidação antecipada. Calcule isso. "
            f"4. Para parcelamentos, use o CET de 1.99% a.m. "
            f"5. Formate propostas em tabelas Markdown para clareza."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2
                ),
                contents=historico_formatado + [
                    types.Content(role="user", parts=[types.Part(text=mensagem)])
                ]
            )
            return response.text if response.text else "Poderia repetir?"
        except Exception as e:
            print(f"🚨 Erro Gemini: {e}")
            return "Tive um problema nos cálculos. Pode tentar novamente?"
