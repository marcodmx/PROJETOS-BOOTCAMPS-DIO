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
            print(f"✅ Motor de Negociação Ativo: {self.model_id}")
        except:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o Consultor Sênior de Saúde Financeira da RenovaIA. CLIENTE: {dados_cliente}
        
        ### ⚖️ REGRAS LEGAIS E BANCÁRIAS (BACEN/CDC):
        1. CET (Custo Efetivo Total): Informe sempre que parcelamentos têm juros de 1.99% a.m.
        2. AMORTIZAÇÃO (Art. 52 CDC): Se o cliente escolher parcelar, diga: "João, lembre-se que ao antecipar parcelas, você tem direito legal ao desconto proporcional dos juros! ⚖️"
        3. BOLETO: Se ele aceitar, forneça o código: 23790.12345 60000.789012 34567.890123 1 95000000185000
        
        ### 🎭 UX EMOCIONAL:
        - Use emojis (✨, 🙌, ✅, 🤝, 🥳).
        - Ao fechar acordo, parabenize o cliente pelo passo importante.
        - Não peça nota (NPS) aqui; a interface cuidará disso no encerramento.

        ### 💰 TABELA:
        - À Vista: R$ 1.850,00 (Melhor Opção).
        - Parcelado: Saldo de R$ 2.950,00 em até 12x (incidência de CET).
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
            return "⚠️ Ocorreu um erro na comunicação. Por favor, tente novamente."
