import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        # 1. Carrega a chave de API do ambiente
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erro: Variável GOOGLE_API_KEY não configurada!")
            
        # 2. Inicializa o cliente da SDK v2.0
        self.client = genai.Client(api_key=api_key)
        
        # 3. Lógica de Busca Automática do Modelo
        try:
            available_models = [m.name for m in self.client.models.list()]
            target = "gemini-1.5-flash"
            
            self.model_id = next((m for m in available_models if target in m), available_models[0])
            
            if self.model_id.startswith("models/"):
                self.model_id = self.model_id.replace("models/", "")
                
            print(f"✅ Modelo validado para negociação: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Usando fallback: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        """
        Gera a resposta da IA com foco em fechamento, CET e código copiável.
        """
        
        # O "Cérebro" da negociação com as regras que alinhamos
        prompt_sistema = f"""
        Você é o motor de fechamento da RenovaIA. Sua comunicação é funcional, clara e focada em resultados.

        DADOS DO CLIENTE LOCALIZADOS NO SISTEMA:
        {dados_cliente}

        ### DIRETRIZES RÍGIDAS DE FLUXO (Siga a risca):

        1. RECONHECIMENTO DE OPÇÃO (STOP LOOP): Se o usuário digitar '1', '2' ou escolher uma oferta, PARE de dar saudações ou explicações genéricas. 
           Responda imediatamente: "Você escolheu a **Opção [X]**. Confira o detalhamento do seu acordo abaixo:"

        2. TABELA DE DETALHAMENTO (CET): Logo após a confirmação, apresente os valores de forma profissional:
           - Valor Principal: R$ [X]
           - Multa/Encargos de Atraso: R$ [X]
           - Desconto Aplicado: -R$ [X]
           - **TOTAL FINAL A PAGAR: R$ [Valor Calculado]**
           Pergunte: "Posso formalizar este acordo e gerar seu código de barras agora?"

        3. FECHAMENTO E CÓDIGO COPIÁVEL: Se o usuário confirmar (ex: 'Sim', 'Pode', 'Confirmar'), responda:
           "Parabéns! 🥂 Seu acordo foi formalizado com sucesso. Este é um grande passo para sua saúde financeira."
           Exiba o código de barras EXATAMENTE neste bloco para habilitar o botão de copiar:
           ```
           23790.12345 60000.789012 34567.890123 1 95000000185000
           ```
           Informe claramente:
           - Vencimento: em 2 dias úteis.
           - Importante: Pagamentos após o prazo cancelam o acordo e geram novos juros.

        4. WHATSAPP: Somente APÓS gerar o código de barras, pergunte se ele deseja receber uma cópia no WhatsApp cadastrado.

        5. POSTURA: Seja empático, mas proativo. Use **NEGRITO** para destacar valores e datas.
        """
        
        try:
            # 4. Chamada para a geração de conteúdo usando a Configuração de Instrução do Sistema
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.7,
                    top_p=0.95
                ),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"❌ Erro ao processar negociação: {str(e)}"
