import os
from google import genai
from google.genai import types

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash" # Estável para cálculos

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # Instrução que obriga a IA a ser técnica e matemática
        prompt_sistema = (
            f"Você é um assistente de negociação bancária. Dados do cliente: {dados_cliente}. "
            f"REGRAS TÉCNICAS: "
            f"1. Se o cliente pedir ofertas, calcule o desconto de antecipação (Art. 52 do CDC). "
            f"2. O desconto deve ser sobre os juros contratuais originais. "
            f"3. Apresente os valores em formato de tabela: [Valor Original] | [Desconto Art. 52] | [Valor Final]. "
            f"4. Para parcelamento, aplique 1.99% de CET. "
            f"Não prometa o que não calculou."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.1
                ),
                contents=historico_formatado + [
                    types.Content(role="user", parts=[types.Part(text=mensagem)])
                ]
            )
            return response.text
        except Exception as e:
            return f"Erro técnico: {str(e)}"
