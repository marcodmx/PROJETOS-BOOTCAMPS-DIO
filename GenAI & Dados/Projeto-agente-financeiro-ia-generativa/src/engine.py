import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada!")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = None
        
        # 🕵️ TÉCNICA DE CONSULTA DINÂMICA
        try:
            modelos_disponiveis = [m.name for m in self.client.models.list()]
            
            # Prioridade 1: 1.5-flash (Estável e com cota)
            # Prioridade 2: 2.0-flash (Caso o 1.5 não apareça)
            if any("gemini-1.5-flash" in m for m in modelos_disponiveis):
                self.model_id = "gemini-1.5-flash"
            elif any("gemini-2.0-flash" in m for m in modelos_disponiveis):
                self.model_id = "gemini-2.0-flash"
            else:
                self.model_id = modelos_disponiveis[0].replace("models/", "")
                
            print(f"✅ Modelo selecionado via consulta: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Falha na consulta, usando fallback: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"Você é o consultor RenovaIA. Cliente: {dados_cliente}. Regras: CET 1.99% a.m. e Art 52 CDC."
        
        try:
            # CONDICIONAL DE CHAMADA
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
            return response.text if response.text else "Sem resposta da IA."
        except Exception as e:
            print(f"🚨 Erro na resposta: {e}")
            return "Erro técnico. Tente novamente em instantes."
            
