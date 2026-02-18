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
        
        self.client = genai.Client(api_key=api_key)
        
        try:
            # Busca automática do modelo disponível
            available_models = [m.name for m in self.client.models.list()]
            target = "gemini-1.5-flash"
            
            # Seleciona o modelo e limpa o prefixo 'models/' se existir
            self.model_id = next((m for m in available_models if target in m), available_models[0])
            if self.model_id.startswith("models/"):
                self.model_id = self.model_id.replace("models/", "")
                
            print(f"✅ Modelo selecionado e limpo: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Erro ao listar modelos, usando padrão: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        prompt_sistema = f"Você é o RenovaIA. Dados do cliente: {dados_cliente}. Seja empático."
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(system_instruction=prompt_sistema),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"Erro na IA: {str(e)}"
