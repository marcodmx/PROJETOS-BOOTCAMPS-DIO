import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: 
            raise ValueError("Sua GOOGLE_API_KEY sumiu do .env! Dá uma olhada lá.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = None
        
        # 🕵️‍♂️ DESCOBERTA DINÂMICA: O pulo do gato para matar o 404
        try:
            # Lista os modelos disponíveis para a SUA chave
            modelos = self.client.models.list()
            for m in modelos:
                # Procuramos o Flash 1.5 ou 2.0 (o que estiver disponível)
                if "gemini-1.5-flash" in m.name or "gemini-2.0-flash" in m.name:
                    # Remove o prefixo 'models/' se ele vier, a API nova prefere o ID puro
                    self.model_id = m.name.replace("models/", "")
                    break
            
            if not self.model_id:
                self.model_id = "gemini-1.5-flash" # Última tentativa
            
            print(f"✅ Motor Ativo: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Erro ao listar modelos: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o Consultor Sênior da RenovaIA. CLIENTE: {dados_cliente}
        ### REGRAS LEGAIS:
        - Informe CET de 1.99% a.m. e Art. 52 do CDC.
        - Se o cliente aceitar, mande o boleto em bloco de código:
        ```
        23790.12345 60000.789012 34567.890123 1 95000000185000
        ```
        """
        
        try:
            # Força o uso do modelo descoberto
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2,
                ),
                contents=historico_formatado + [
                    types.Content(role="user", parts=[types.Part(text=mensagem)])
                ]
            )
            
            if response and response.text:
                return response.text
            return "🙌 João, tive um pequeno soluço aqui. Pode repetir?"

        except Exception as e:
            print(f"🚨 ERRO CRÍTICO: {str(e)}")
            return "⚠️ Erro de conexão com o banco. Tente de novo em 5 segundos."
            
