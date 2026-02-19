import os
from google import genai
from google.genai import types

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        
        try:
            modelos = [m.name for m in self.client.models.list()]
            self.model_id = "gemini-1.5-flash" if any("gemini-1.5-flash" in m for m in modelos) else "gemini-2.0-flash"
            print(f"✅ Motor calibrado: {self.model_id}")
        except:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # Instrução de sistema poderosa:
        prompt_sistema = (
            f"Você é o Consultor Financeiro Sênior da RenovaIA. "
            f"DADOS DO CLIENTE: {dados_cliente}. "
            f"DIRETRIZES TÉCNICAS: "
            f"1. Aplique o Art. 52 do CDC (liquidação antecipada) com desconto real sobre os juros. "
            f"2. Calcule parcelamentos com CET de 1.99% a.m. "
            f"3. Formate respostas com Markdown: use Tabelas, Negrito e Emojis. "
            f"4. Se o cliente perguntar de onde vêm os valores, explique o cálculo matemático baseado na dívida dele."
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
            return response.text
        except Exception as e:
            return f"❌ Erro na mesa de negociação: {str(e)}"
