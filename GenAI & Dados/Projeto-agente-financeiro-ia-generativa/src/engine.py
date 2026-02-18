import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

class AgenteNegociador:
    def __init__(self):
        # Busca a chave de API
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("Erro: Variável GOOGLE_API_KEY não configurada!")
            
        # Inicializa o cliente moderno da Google
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        """
        Envia o contexto do cliente e a pergunta para o Gemini.
        """
        prompt_sistema = f"""
        Você é o RenovaIA, um assistente amigável e especialista em negociação de dívidas.
        Dados do cliente atual: {dados_cliente}
        
        INSTRUÇÕES:
        - Use os dados acima para informar ao cliente sobre suas dívidas e prazos.
        - Seja empático, mas mantenha o foco na negociação financeira.
        - Se o CPF não retornar dados (cliente nulo), peça educadamente para conferir o CPF.
        - Ofereça condições de parcelamento ou descontos conforme as regras do banco.
        """
        
        # Chamada moderna da SDK v2.0
        response = self.client.models.generate_content(
            model=self.model_id,
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                temperature=0.7
            ),
            contents=[mensagem]
        )
        
        return response.text
