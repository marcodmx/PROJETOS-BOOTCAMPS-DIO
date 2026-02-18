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
        # 4. Prompt aprimorado para melhorar a UX (conforme solicitado)
        prompt_sistema = f"""
        Você é o RenovaIA, um assistente especialista em negociação de dívidas.
        Sua missão é ajudar o cliente a regularizar sua situação de forma amigável e clara.

        DADOS DO CLIENTE LOCALIZADOS NO SISTEMA:
        {dados_cliente}

        DIRETRIZES DE RESPOSTA:
        1. Comece sempre saudando o cliente pelo primeiro nome.
        2. Seja extremamente empático: reconheça que momentos difíceis acontecem.
        3. Use NEGRITO para destacar valores (ex: **R$ 1.500,00**) e nomes de produtos.
        4. No final de cada resposta, seja PROATIVO e dê 2 opções claras para o cliente escolher.
           Exemplo: "Você prefere que eu explique o desconto à vista ou quer simular um parcelamento?"
        5. Mantenha as respostas objetivas, mas acolhedoras.
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
