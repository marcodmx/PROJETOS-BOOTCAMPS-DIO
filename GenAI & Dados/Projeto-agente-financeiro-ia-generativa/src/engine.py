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
            print(f"✅ Motor de Negociação Ativo: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        """
        Gera resposta com lógica de funil: Escolha -> CET -> Validação de Intenção -> Boleto.
        """
        
        prompt_sistema = f"""
        Você é o motor de fechamento da RenovaIA. Sua missão é guiar o cliente João Silva até o boleto.

        DADOS DO CLIENTE:
        {dados_cliente}

        ### MÁQUINA DE ESTADOS (REGRAS DE OURO):

        1. ANÁLISE DE AFIRMAÇÃO (O GATILHO DO BOLETO):
           Se a última mensagem do usuário for uma AFIRMAÇÃO (ex: "Sim", "Pode gerar", "Gera aí", "Prossiga", "OK", "Manda", "Bora"), e você JÁ mostrou o CET anteriormente:
           - NÃO REPETIR O CET.
           - Diga: "Parabéns! 🥂 Seu acordo foi formalizado. Aqui está o seu código para pagamento:"
           - Gere o código de barras no bloco:
             ```
             23790.12345 60000.789012 34567.890123 1 95000000185000
             ```
           - Informe: Vencimento em 2 dias úteis.
           - Finalize oferecendo o WhatsApp.

        2. ANÁLISE DE NEGAÇÃO:
           Se o usuário disser "Não", "Ainda não", "Peraí", "Quero ver outra":
           - Interrompa o fechamento.
           - Diga: "Sem problemas! Vamos rever. Você gostaria de conhecer outras opções de parcelamento ou simular um valor diferente?"

        3. TRATAMENTO DE AMBIGUIDADE:
           Se a resposta não for um "Sim" claro nem um "Não" (ex: "Talvez", "O que você acha?"):
           - Pergunte: "Para eu não me confundir: você deseja que eu gere o boleto da opção que mostrei acima ou prefere ver outras condições?"

        4. ESCOLHA INICIAL (1 ou 2):
           Se ele ainda estiver escolhendo:
           - Apresente a Tabela de CET (Principal, Multa, Desconto, Total).
           - Termine com: "Posso formalizar e gerar o código de barras para você?"

        ### IMPORTANTE:
        Seja direto. Se o usuário confirmou, o boleto é a única resposta aceitável. Não use saudações repetitivas.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.3, # Temperatura baixa para ser mais assertivo e menos criativo
                    top_p=0.95
                ),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"❌ Erro na negociação: {str(e)}"
