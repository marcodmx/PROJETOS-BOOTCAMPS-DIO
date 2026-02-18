import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Chave API não encontrada!")
        
        # Cliente da SDK nova
        self.client = genai.Client(api_key=api_key)
        
        # --- BUSCA AUTOMÁTICA NA SDK NOVA ---
        try:
            # Lista os modelos disponíveis na v2.0
            available_models = [m.name for m in self.client.models.list()]
            
            # Verifica se o flash está na lista (removendo o prefixo 'models/' se a lista trouxer)
            target = "gemini-1.5-flash"
            # Lógica de escolha: se o alvo estiver lá ou algo que contenha o nome, usa ele.
            # Caso contrário, pega o primeiro da lista.
            self.model_id = next((m for m in available_models if target in m), available_models[0])
            
            if self.model_id.startswith("models/"):
                self.model_id = self.model_id.replace("models/", "")
                
            print(f"✅ Modelo selecionado e limpo: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Erro ao listar modelos, usando fallback: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        prompt_sistema = f"""
        Você é o RenovaIA, assistente de negociação. 
        Dados do cliente: {dados_cliente}
        Seja empático e profissional.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.7
                ),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"Erro na chamada da IA: {str(e)}"
