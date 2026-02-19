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
            if any("gemini-1.5-flash" in m for m in modelos):
                self.model_id = "gemini-1.5-flash"
            else:
                self.model_id = "gemini-2.0-flash"
            print(f"✅ Motor calibrado com: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # CDC apenas como argumento de fechamento técnico
        prompt_sistema = (
            f"Você é o consultor sênior da RenovaIA. Dados do Cliente: {dados_cliente}. "
            f"COMPORTAMENTO ESPERADO: "
            f"1. Seja humano, empático e cordial no início. "
            f"2. Somente quando o cliente tratar de valores, propostas ou boletos, apresente os cálculos. "
            f"3. Use o Art. 52 do Código de Defesa do Consumidor (CDC) como base legal para garantir o desconto "
            f"proporcional de juros e encargos na antecipação da dívida. "
            f"4. Para parcelamentos, aplique rigorosamente o CET de 1.99% a.m. "
            f"5. Formate as propostas em tabelas Markdown para clareza absoluta."
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
            return "Estou com uma instabilidade momentânea. Tente novamente."
