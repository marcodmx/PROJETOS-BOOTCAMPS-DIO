import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erro: Variável GOOGLE_API_KEY não configurada!")
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash"
        print(f"✅ Motor de Negociação Ativo: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o especialista financeiro da RenovaIA. CLIENTE: {dados_cliente}
        
        ### REGRA DE BLOQUEIO PÓS-ACORDO:
        - Analise o histórico. Se o código de barras já foi enviado, o acordo está selado.
        - Não ofereça novas opções. Informe que o acordo está formalizado.
        - Se o cliente insistir, direcione para o SAC: 0800 777 0000 e informe o transbordo humano.
        
        ### FLUXO DE NEGOCIAÇÃO:
        - Opção 1: À vista (R$ 1.850,00).
        - Opção 2: Parcelado (12x).
        
        BOLETO: ```23790.12345 60000.789012 34567.890123 1 95000000185000```
        """
        
        try:
            chat = self.client.chats.create(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.1
                ),
                history=historico_formatado
            )
            response = chat.send_message(mensagem)
            return response.text
        except Exception as e:
            return f"❌ Erro na API: {str(e)}"
