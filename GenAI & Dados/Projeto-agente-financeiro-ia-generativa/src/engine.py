import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash" # Prioridade para evitar o 429 do 2.0

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = (
            f"Você é o consultor da RenovaIA. Dados: {dados_cliente}. "
            "Regras: Seja empático. Use o Art. 52 CDC apenas para propostas. CET 1.99%."
        )
        
        # Tentativas automáticas (Retry Logic)
        for tentativa in range(3):
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
                if "429" in str(e) and tentativa < 2:
                    print(f"⏳ Cota atingida. Tentativa {tentativa + 1} de 3... Aguardando 5s.")
                    time.sleep(5) # Espera 5 segundos para o balde esvaziar
                    continue
                return "O servidor está um pouco sobrecarregado. Pode tentar clicar em enviar novamente?"
