import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: 
            raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env!")
        
        # Inicializa o cliente GenAI
        self.client = genai.Client(api_key=api_key)
        
        # 🎯 DEFINIÇÃO DIRETA: O Google as vezes falha ao listar. 
        # Vamos usar o ID puro que é o padrão da v1.
        self.model_id = "gemini-1.5-flash"
        print(f"✅ Motor de Negociação configurado para: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # ⚖️ PROMPT SÊNIOR: Rigor legal + UX Emocional
        prompt_sistema = f"""
        Você é o Consultor Sênior de Saúde Financeira da RenovaIA. CLIENTE: {dados_cliente}
        
        ### ⚖️ REGRAS LEGAIS E BANCÁRIAS:
        1. CET (Custo Efetivo Total): Informe sempre que parcelamentos têm juros de 1.99% a.m.
        2. AMORTIZAÇÃO (Art. 52 CDC): Se o cliente escolher parcelar, diga: "João, lembre-se que ao antecipar parcelas, você tem direito legal ao desconto proporcional dos juros! ⚖️"
        3. BOLETO: Se ele aceitar, forneça o código: 
        ```
        23790.12345 60000.789012 34567.890123 1 95000000185000
        ```
        
        ### 🎭 UX EMOCIONAL:
        - Use emojis e parabenize o cliente pela decisão de regularizar a vida financeira.
        - Seja transparente, ético e empático.
        """
        
        try:
            # 🚀 CHAMADA BLINDADA: Usamos o model_id sem o prefixo 'models/'
            # Isso evita o erro 404 em 99% dos casos no SDK novo
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
            return "⚠️ A IA não retornou texto. Tente novamente."

        except Exception as e:
            # Log real no terminal para debug
            print(f"🚨 ERRO CRÍTICO NA API: {str(e)}")
            return "⚠️ Erro técnico de conexão. Por favor, tente novamente em alguns instantes."
