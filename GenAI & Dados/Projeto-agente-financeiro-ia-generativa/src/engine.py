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
        
        # 3. Lógica de Busca Automática (O que resolveu o erro 404)
        try:
            # Lista os modelos disponíveis na sua conta
            available_models = [m.name for m in self.client.models.list()]
            target = "gemini-1.5-flash"
            
            # Busca o modelo alvo ou pega o primeiro disponível como fallback
            self.model_id = next((m for m in available_models if target in m), available_models[0])
            
            # Limpeza crucial: remove 'models/' se a API retornar com o prefixo
            if self.model_id.startswith("models/"):
                self.model_id = self.model_id.replace("models/", "")
                
            print(f"✅ Modelo selecionado e validado: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Erro ao listar modelos, usando padrão fixo: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        """
        Gera a resposta da IA utilizando os dados do cliente e o prompt otimizado.
        """
        # Unindo empatia com regras de fechamento profissional
        prompt_sistema = f"""
        Você é o RenovaIA, assistente especialista em negociação de dívidas.
        MISSÃO: Ajudar o cliente a regularizar sua situação de forma amigável, clara e motivadora.

        DADOS DO CLIENTE:
        {dados_cliente}

        DIRETRIZES DE RESPOSTA (Mantenha sempre):
        1. Saudações pelo primeiro nome e empatia total.
        2. Use **NEGRITO** para valores e produtos.
        3. Seja PROATIVO: ofereça sempre dois caminhos (Ex: à vista ou parcelado).

        NOVAS REGRAS DE FECHAMENTO (ESSENCIAL):
        4. CELEBRAÇÃO: Se o cliente aceitar um acordo, diga: "Parabéns! 🥂 Este é um passo gigante para sua liberdade financeira."
        5. VENCIMENTO: Todo boleto (à vista ou 1ª parcela) vence em 2 dias úteis. Informe isso claramente.
        6. JUROS: Avise que pagamentos após o vencimento cancelam o acordo e geram encargos.
        7. PARCELAMENTO: Se parcelado, liste as parcelas e explique que as próximas vencem no mesmo dia dos meses seguintes.
        8. FORMATO DO BOLETO: Apresente o código de barras (fictício, mas realista) dentro de um bloco de código Markdown:
           ```
           23790.12345 60000.789012 34567.890123 1 95000000185000
           ```
        """
        
        try:
            # 5. Chamada para a geração de conteúdo
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
            return f"❌ Erro ao processar resposta da IA: {str(e)}"
