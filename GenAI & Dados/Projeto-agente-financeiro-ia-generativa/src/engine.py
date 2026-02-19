import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: raise ValueError("GOOGLE_API_KEY ausente!")
        
        # Inicializa o cliente
        self.client = genai.Client(api_key=api_key)
        
        # 🔍 DESCOBERTA DINÂMICA (Para matar o erro 404)
        try:
            modelos = self.client.models.list()
            # Procuramos por qualquer um que seja 'gemini-1.5-flash'
            # A API pode retornar 'gemini-1.5-flash' ou 'models/gemini-1.5-flash'
            for m in modelos:
                if "gemini-1.5-flash" in m.name:
                    self.model_id = m.name # Pega o nome exato que a API quer
                    break
            else:
                self.model_id = "gemini-1.5-flash" # Fallback
            
            print(f"✅ Motor Ativo: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Erro ao listar: {e}. Usando padrão.")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o Consultor Sênior da RenovaIA. CLIENTE: {dados_cliente}
        ### REGRAS:
        - Informe CET de 1.99% a.m. e Art. 52 do CDC.
        - Use blocos de código para o boleto.
        """
        
        try:
            # A API v1 prefere receber apenas o nome sem o prefixo 'models/' se der erro
            model_name = self.model_id.replace("models/", "")
            
            response = self.client.models.generate_content(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2
                ),
                contents=historico_formatado + [types.Content(role="user", parts=[types.Part(text=mensagem)])]
            )
            return response.text
        except Exception as e:
            print(f"🚨 ERRO NA API GEMINI: {str(e)}")
            return "⚠️ Erro técnico. Tente novamente em instantes."
