import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erro: GOOGLE_API_KEY não encontrada!")
        
        self.client = genai.Client(api_key=api_key)
        
        # Lógica inteligente de descoberta de modelo (A que funcionava)
        try:
            modelos_disponiveis = [m.name for m in self.client.models.list()]
            # Prioriza 1.5-flash pela estabilidade no tier gratuito, mas aceita 2.0 se houver
            selecionado = next((m for m in modelos_disponiveis if "gemini-1.5-flash" in m), modelos_disponiveis[0])
            self.model_id = selecionado.replace("models/", "")
            print(f"✅ Motor de Negociação Ativo: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"
            print(f"⚠️ Erro ao listar modelos, usando padrão: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o especialista financeiro da RenovaIA. CLIENTE: {dados_cliente}
        
        ### REGRA DE OURO (MEMÓRIA):
        - Verifique o histórico de mensagens. 
        - SE você já enviou o CÓDIGO DE BARRAS, o acordo está encerrado.
        - Não ofereça descontos novamente. Informe que o boleto já foi gerado.
        - SAC: 0800 777 0000.
        
        ### VALORES:
        - Opção 1 (À vista): R$ 1.850,00
        - Opção 2 (Parcelado): 12x
        - BOLETO: 23790.12345 60000.789012 34567.890123 1 95000000185000
        """
        
        try:
            # Usando a estrutura de contents para enviar o histórico + a nova mensagem
            # Isso garante que a API receba toda a conversa para manter a memória
            novos_contents = historico_formatado + [
                types.Content(role="user", parts=[types.Part(text=mensagem)])
            ]
            
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.1,
                ),
                contents=novos_contents
            )
            return response.text
        except Exception as e:
            print(f"DEBUG Erro API: {e}")
            return "⚠️ Ocorreu um erro na comunicação. Por favor, tente novamente."
