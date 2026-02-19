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
            print(f"✅ Motor de Negociação Humanizado Ativo: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        """
        Gera resposta focada em decisão. Se o cliente escolheu, gera o boleto.
        """
        
        prompt_sistema = f"""
        Você é o especialista em sucesso financeiro da RenovaIA.
        
        ### REGRAS CRÍTICAS DE FLUXO:
        1. DETECÇÃO DE ESCOLHA: Se o cliente enviar "1", "2", "primeira", "segunda", "à vista" ou "parcelado", você deve INTERROMPER a oferta e partir para o FECHAMENTO.
        2. NÃO SE REPITA: Se o cliente já escolheu, não ofereça as opções novamente. Gere o resumo e o código de barras.
        3. FOCO NO CLIENTE: {dados_cliente}

        ### DIRETRIZES DE RESPOSTA:
        - SE NÃO HOUVER ESCOLHA AINDA: Apresente a Opção 1 (À vista com desconto) e Opção 2 (Parcelamento).
        - SE O CLIENTE ESCOLHEU (Ex: digitou "1"): 
            - Diga: "Excelente escolha! Vamos seguir com a quitação à vista." 
            - Apresente o valor final e o código de barras abaixo.
            - Finalize com celebração discreta: "Tudo pronto! Ficamos felizes em ajudar. 🙏"

        ### CÓDIGO COPIÁVEL (OBRIGATÓRIO NO FECHAMENTO):
        ```
        23790.12345 60000.789012 34567.890123 1 95000000185000
        ```
        
        Tom de voz: Empático, sem usar as palavras "dívida" ou "pendência".
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.3, # Diminuído para ser mais direto e menos criativo
                    top_p=0.95
                ),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"❌ Erro na negociação: {str(e)}"
