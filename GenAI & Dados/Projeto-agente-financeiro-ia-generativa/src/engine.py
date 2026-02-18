import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Tenta carregar o arquivo .env se existir (para uso local)
load_dotenv()

class AgenteNegociador:
    def __init__(self):
        # Busca a chave no ambiente (configurada no Colab ou .env)
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("Erro: GOOGLE_API_KEY não encontrada no ambiente!")
            
        # Cliente moderno da SDK 2.0
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        prompt_sistema = f"""
        Você é o RenovaIA, o assistente virtual de renegociação de dívidas.
        Dados do cliente atual: {dados_cliente}
        
        REGRAS:
        1. Seja empático e profissional.
        2. Use os dados do JSON para informar valores de dívida e descontos.
        3. Se o CPF não for encontrado ou os dados forem nulos, peça para o usuário conferir o CPF.
        4. NUNCA invente dívidas que não estão nos dados fornecidos.
        """
        
        # Chamada moderna para o Gemini
        response = self.client.models.generate_content(
            model=self.model_id,
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema
            ),
            contents=[mensagem]
        )
        
        return response.text
