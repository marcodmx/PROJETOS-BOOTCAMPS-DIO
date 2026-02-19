import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erro: Variável GOOGLE_API_KEY não configurada!")
        
        self.client = genai.Client(api_key=api_key)
        
        # 🚀 Atualizado para o modelo mais recente disponível (2.0 Flash)
        # Se preferir a estabilidade total, use "gemini-1.5-flash"
        self.model_id = "gemini-2.0-flash-exp" 
        print(f"✅ Motor de Negociação Ativo: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        # Instrução de sistema otimizada para o Gemini 2.0
        prompt_sistema = f"""
        Você é o especialista financeiro da RenovaIA. CLIENTE: {dados_cliente}
        
        ### REGRAS CRÍTICAS:
        1. MEMÓRIA: Analise o histórico. Se o código de barras já foi enviado, o acordo está SELADO.
        2. BLOQUEIO: No estado SELADO, não ofereça descontos. Apenas dê suporte sobre o pagamento.
        3. SAC: 0800 777 0000.
        
        ### VALORES:
        - À vista: R$ 1.850,00 | Parcelado: 12x.
        - BOLETO: 23790.12345 60000.789012 34567.890123 1 95000000185000
        """
        
        try:
            # Usando a estrutura de chat nativa da biblioteca v1
            chat = self.client.chats.create(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.1, # Menos criatividade, mais precisão
                ),
                history=historico_formatado
            )
            response = chat.send_message(mensagem)
            return response.text
        except Exception as e:
            # Fallback automático: se o 2.0 falhar por quota, tenta o 1.5
            if "404" in str(e) or "not found" in str(e).lower():
                return self._fallback_15(mensagem, dados_cliente, historico_formatado)
            return f"❌ Erro na API: {str(e)}"

    def _fallback_15(self, mensagem, dados_cliente, historico_formatado):
        """Método de segurança para garantir que o sistema não pare."""
        try:
            chat = self.client.chats.create(
                model="gemini-1.5-flash",
                config=types.GenerateContentConfig(temperature=0.1),
                history=historico_formatado
            )
            response = chat.send_message(mensagem)
            return response.text
        except:
            return "⚠️ Erro crítico de conexão. Tente novamente em instantes."
