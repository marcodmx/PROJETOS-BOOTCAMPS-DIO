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
        
        try:
            available_models = [m.name for m in self.client.models.list()]
            target = "gemini-1.5-flash"
            self.model_id = next((m for m in available_models if target in m), available_models[0])
            if self.model_id.startswith("models/"):
                self.model_id = self.model_id.replace("models/", "")
            print(f"✅ Motor de Negociação Ativo: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"

    def responder(self, historico_mensagens, dados_cliente):
        """
        Recebe o histórico completo e os dados do cliente para manter a memória.
        """
        prompt_sistema = f"""
        Você é o especialista financeiro da RenovaIA.
        CLIENTE: {dados_cliente}

        ### REGRAS DE MEMÓRIA E ESTADO:
        1. Verifique as mensagens anteriores. Se você já apresentou o CÓDIGO DE BARRAS, o acordo está SELADO.
        2. Uma vez selado, NUNCA mais ofereça opções de desconto ou parcelamento, mesmo que o cliente diga "Olá".
        3. No estado PÓS-ACORDO, sua única função é tirar dúvidas sobre o pagamento, informar o SAC (0800 777 0000) e avisar que um humano assumirá o chat.

        ### DIRETRIZES DE NEGOCIAÇÃO:
        - Início: Ofereça Opção 1 (À vista R$ 1.850,00) e Opção 2 (12x).
        - Escolha: Se o cliente escolher, gere o boleto e encerre a oferta.
        - Boleto: ```23790.12345 60000.789012 34567.890123 1 95000000185000```
        """
        
        try:
            # Enviamos o histórico completo para a API (Memória Real)
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2,
                ),
                contents=historico_mensagens
            )
            return response.text
        except Exception as e:
            return f"❌ Erro: {str(e)}"
