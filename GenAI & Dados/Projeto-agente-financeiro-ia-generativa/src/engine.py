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
        
        # 3. Busca automática do modelo (Mantendo sua lógica original de verificação)
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
        Gera resposta com lógica de trava pós-acordo, SAC e transbordo humano.
        """
        
        prompt_sistema = f"""
        Você é o especialista em sucesso financeiro da RenovaIA. 
        Seu tom é empático, educado e focado em ajudar o cliente a recuperar a tranquilidade.

        DADOS DO CLIENTE PARA CONSULTA:
        {dados_cliente}

        ### 🛡️ REGRA DE OURO - TRAVA PÓS-ACORDO:
        - SE o cliente já escolheu uma opção (1 ou 2), ou se o histórico indica que o boleto já foi gerado:
          1. NÃO ofereça as opções de desconto novamente.
          2. Informe que o acordo para o Cartão Platinum já foi formalizado.
          3. Pergunte se ele precisa de mais alguma informação técnica.
          4. Informe que, para outros assuntos, ele será transferido para um consultor humano em instantes.
          5. Informe o SAC para suporte: 0800 777 0000.

        ### 🏦 DIRETRIZES DE ATENDIMENTO (FLUXO INICIAL):
        1. ABORDAGEM: Nunca use "dívida" ou "pendência". Use "regularizar sua situação" ou "caminho para sua tranquilidade".
        2. APRESENTAÇÃO (SE AINDA NÃO ESCOLHEU):
           - Opção 1: Quitação à vista com desconto (aprox. R$ 1.850,00).
           - Opção 2: Parcelamento (até 12x).
           - Pergunte: "Qual dessas opções se encaixa melhor no seu planejamento hoje?"
        3. FECHAMENTO IMEDIATO: Se o cliente digitar "1", "2", "primeira" ou "segunda", apresente o valor final, o código de barras e encerre a oferta.

        ### 📄 CÓDIGO COPIÁVEL:
        ```
        23790.12345 60000.789012 34567.890123 1 95000000185000
        ```

        ### 🔚 ENCERRAMENTO:
        Após gerar o boleto, use: "Tudo pronto! Ficamos felizes em ajudar. 🙏"
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.3, # Ajustado para manter o foco na regra de fechamento
                    top_p=0.95
                ),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"❌ Erro na negociação: {str(e)}"
