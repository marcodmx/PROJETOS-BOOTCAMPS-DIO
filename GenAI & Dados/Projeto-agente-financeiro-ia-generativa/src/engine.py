import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: raise ValueError("GOOGLE_API_KEY não encontrada!")
        self.client = genai.Client(api_key=api_key)
        
        try:
            modelos = [m.name for m in self.client.models.list()]
            selecionado = next((m for m in modelos if "gemini-1.5-flash" in m), modelos[0])
            self.model_id = selecionado.replace("models/", "")
            print(f"✅ Motor Ativo: {self.model_id}")
        except:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o Consultor Sênior de Saúde Financeira da RenovaIA. CLIENTE: {dados_cliente}
        
        ### ⚖️ REGRAS LEGAIS (BACEN/CDC):
        - Informe sempre o CET de 1.99% a.m. para parcelamentos.
        - Cite o Art. 52 do CDC sobre amortização de juros no pagamento antecipado.
        
        ### 📋 FORMATAÇÃO DO BOLETO (OBRIGATÓRIO):
        Quando o cliente aceitar o acordo, você DEVE enviar o código exatamente dentro de um bloco de código Markdown. Isso habilita o botão de cópia automática:
        
        Aqui está seu código de barras para pagamento:
        ```
        23790.12345 60000.789012 34567.890123 1 95000000185000
        ```
        
        ### 🎭 UX EMOCIONAL:
        - Use emojis e parabenize o cliente pela decisão.
        - Não solicite notas (NPS); a interface cuida disso no encerramento.
        """
        
        try:
            novos_contents = historico_formatado + [types.Content(role="user", parts=[types.Part(text=mensagem)])]
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(system_instruction=prompt_sistema, temperature=0.2),
                contents=novos_contents
            )
            return response.text
        except Exception as e:
            return "⚠️ Erro técnico. Por favor, tente novamente."
