import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    """
    Classe responsável pela interface com a API Google Gemini,
    gerenciando a seleção de modelos e a geração de respostas.
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Chave de API (GOOGLE_API_KEY) não configurada.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = None

        try:
            # Identificação dinâmica de modelos disponíveis
            modelos = list(self.client.models.list())
            nomes_modelos = [m.name for m in modelos]
            
            # Prioridade de seleção baseada na disponibilidade da conta
            for nome in nomes_modelos:
                if "gemini-2.0-flash" in nome:
                    self.model_id = nome
                    break
            
            if not self.model_id:
                for nome in nomes_modelos:
                    if "gemini-1.5-flash" in nome:
                        self.model_id = nome
                        break

            if self.model_id:
                print(f"Status: Motor selecionado - {self.model_id}")
            else:
                self.model_id = "gemini-1.5-flash"
                print("Aviso: Utilizando identificador padrão gemini-1.5-flash.")

        except Exception as e:
            print(f"Erro na inicialização do motor: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        """
        Gera resposta baseada nas diretrizes de negócio e direitos do consumidor.
        """
        prompt_sistema = (
            f"Você é o consultor especializado da RenovaIA. Dados do cliente: {dados_cliente}. "
            "DIRETRIZES DE NEGOCIAÇÃO: "
            "1. Cordialidade e empatia no atendimento. "
            "2. Para ofertas à vista, informe ao cliente que, conforme o Art. 52, § 2º do CDC, "
            "ele possui o direito legal à liquidação antecipada do débito com redução proporcional dos juros. "
            "3. Para parcelamentos, utilize a taxa de CET de 1.99% a.m. "
            "4. Formatação: Apresente as opções de pagamento (À Vista vs. Parcelado) em tabelas Markdown."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2
                ),
                contents=historico_formatado + [
                    types.Content(role="user", parts=[types.Part(text=mensagem)])
                ]
            )
            return response.text if response.text else "Erro: Resposta vazia da API."
        except Exception as e:
            print(f"Erro na geração de conteúdo: {e}")
            return f"Erro no processamento da solicitação: {str(e)[:50]}"
