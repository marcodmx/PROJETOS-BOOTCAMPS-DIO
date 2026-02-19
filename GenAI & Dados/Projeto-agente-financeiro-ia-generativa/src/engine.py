import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: raise ValueError("Erro: GOOGLE_API_KEY ausente!")
        self.client = genai.Client(api_key=api_key)
        
        try:
            modelos = [m.name for m in self.client.models.list()]
            selecionado = next((m for m in modelos if "gemini-1.5-flash" in m), modelos[0])
            self.model_id = selecionado.replace("models/", "")
        except:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # DIRETRIZES SÊNIOR: Ética, BACEN, CDC e UX
        prompt_sistema = f"""
        Você é o Consultor Especialista de Saúde Financeira da RenovaIA.
        CLIENTE ATUAL: {dados_cliente}

        ### ⚖️ CONFORMIDADE LEGAL E ÉTICA (BACEN/CDC):
        1. TRANSPARÊNCIA: Sempre informe o Valor Original vs. Valor Negociado.
        2. CET (Custo Efetivo Total): Para parcelamentos, explique que há juros de 1.99% a.m. Informe o valor total final.
        3. AMORTIZAÇÃO (Art. 52, § 2º CDC): Explique: "João, se você antecipar parcelas, terá redução proporcional dos juros. É seu direito legal! ⚖️"
        4. CYBERSEGURANÇA: Nunca repita o CPF completo no chat. Use apenas o primeiro nome.

        ### 🎭 TOM DE VOZ E UX:
        - Use Emojis para humanizar: ✨, 🙌, ✅, 🤝.
        - Quando o cliente aceitar: "Parabéns por esse passo importante para sua saúde financeira! 🥳👏"
        - Se o cliente der uma nota (1 a 10): Responda com "Muito obrigado por sua avaliação! 🌟 Isso nos ajuda a construir uma RenovaIA melhor para você."

        ### 💰 REGRAS DE NEGÓCIO:
        - À Vista: R$ 1.850,00 (Melhor opção).
        - Parcelado: Até 12x com juros.
        - BOLETO (Exemplo): 23790.12345 60000.789012 34567.890123 1 95000000185000

        ### 🧠 LÓGICA DE MEMÓRIA:
        - Se o boleto foi gerado, o status é "ACORDO FIRMADO". Não altere valores. 
        - Reenvie o boleto se ele pedir "Olá" ou "Oi" após o acordo.
        """
        
        try:
            novos_contents = historico_formatado + [types.Content(role="user", parts=[types.Part(text=mensagem)])]
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(system_instruction=prompt_sistema, temperature=0.3),
                contents=novos_contents
            )
            return response.text
        except Exception as e:
            return f"⚠️ Sistema momentaneamente instável. Por favor, tente em instantes."
