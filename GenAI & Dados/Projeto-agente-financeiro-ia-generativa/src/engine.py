import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada no ambiente!")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = None
        
        # Lógica de Auto-Descoberta de Modelo
        try:
            modelos = [m.name for m in self.client.models.list()]
            if any("gemini-1.5-flash" in m for m in modelos):
                self.model_id = "gemini-1.5-flash"
            elif any("gemini-2.0-flash" in m for m in modelos):
                self.model_id = "gemini-2.0-flash"
            else:
                self.model_id = modelos[0].replace("models/", "")
            print(f"✅ Modelo selecionado via consulta: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Falha na consulta, usando fallback 1.5-flash: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # Regras de negócio rígidas no System Instruction
        prompt_sistema = (
            f"Você é o consultor especializado da RenovaIA. "
            f"Dados do Cliente atual: {dados_cliente}. "
            f"REGRAS DE NEGOCIAÇÃO: "
            f"1. Taxa de juros (CET) máxima de 1.99% a.m. "
            f"2. Sempre cite o Artigo 52 do CDC sobre liquidação antecipada e descontos. "
            f"3. Seja empático, mas focado em recuperar o crédito. "
            f"4. Use emojis moderadamente para manter o tom profissional."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.3
                ),
                contents=historico_formatado + [
                    types.Content(role="user", parts=[types.Part(text=mensagem)])
                ]
            )
            return response.text if response.text else "Desculpe, tive um problema ao processar sua proposta. Pode repetir?"
        except Exception as e:
            print(f"🚨 Erro na API Gemini: {e}")
            return "Estou com instabilidade na conexão. Por favor, tente novamente em alguns segundos."
            
