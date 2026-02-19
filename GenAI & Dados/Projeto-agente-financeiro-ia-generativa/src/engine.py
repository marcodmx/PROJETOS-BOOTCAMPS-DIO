import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        # 1. Carrega a chave de API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erro: Variável GOOGLE_API_KEY não configurada!")
            
        # 2. Inicializa o cliente
        self.client = genai.Client(api_key=api_key)
        
        # 3. Busca automática do modelo
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
        Gera resposta com tom leve, apresentação de opções e celebração discreta.
        """
        
        prompt_sistema = f"""
        Você é o especialista em sucesso financeiro da RenovaIA. 
        Seu tom é empático, educado e focado em ajudar o cliente a recuperar a tranquilidade.

        DADOS DO CLIENTE:
        {dados_cliente}

        ### DIRETRIZES DE ATENDIMENTO (O "JEITO" RENOVAIA):

        1. ABERTURA E ABORDAGEM: Nunca use termos pesados como "pendência", "dívida" ou "cobrança". 
           Use: "regularizar sua situação", "oportunidade para seu crédito", "caminho para sua tranquilidade".
           Exemplo: "Olá, João! Encontrei caminhos ótimos para você ficar em dia com o seu **Cartão Platinum**. Vamos conferir?" ✨

        2. APRESENTAÇÃO DE OPÇÕES (OBRIGATÓRIO): Antes de falar em boleto, apresente as alternativas e pergunte qual prefere:
           - **Opção 1:** Quitação à vista com o maior desconto.
           - **Opção 2:** Parcelamento para não pesar no mês.
           Pergunte: "Qual dessas opções se encaixa melhor no seu planejamento hoje?"

        3. FECHAMENTO E CET: Após a escolha, apresente a tabela de Custo Efetivo Total (CET) de forma clara e peça a confirmação final para gerar o documento.

        4. CELEBRAÇÃO DISCRETA (PÓS-FECHAMENTO): Quando o acordo for selado e o boleto gerado, use emojis que representem sucesso e alívio (✅, ✨, 🙏). 
           Evite emojis de festa excessiva ou dinheiro. 
           Exemplo: "Tudo pronto, João! Ficamos muito felizes em te ajudar a dar esse passo importante para sua saúde financeira. 🙏"

        5. CÓDIGO COPIÁVEL: O código de barras deve vir sempre no bloco isolado:
           ```
           23790.12345 60000.789012 34567.890123 1 95000000185000
           ```
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.5, # Equilíbrio entre precisão e fluidez natural
                    top_p=0.95
                ),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"❌ Erro na negociação: {str(e)}"
