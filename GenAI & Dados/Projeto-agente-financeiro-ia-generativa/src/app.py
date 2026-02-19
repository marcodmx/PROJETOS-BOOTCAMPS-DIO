import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: 
            raise ValueError("Chave de API não encontrada!")
        
        self.client = genai.Client(api_key=api_key)
        
        # 🎯 AJUSTE DE PRECISÃO:
        # Testes mostram que em algumas regiões o SDK v1 exige o prefixo 'models/'
        # para evitar o erro 404, enquanto outras rejeitam. 
        # Vamos usar o padrão que a maioria dos endpoints v1 aceita agora:
        self.model_id = "models/gemini-1.5-flash"
        print(f"✅ MOTOR SINCRONIZADO: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = f"""
        Você é o Consultor Sênior de Saúde Financeira da RenovaIA. 
        DADOS DO CLIENTE: {dados_cliente}
        
        ### ⚖️ DIRETRIZES:
        - Informe CET de 1.99% a.m.
        - Cite o Art. 52 do CDC.
        - Boleto em bloco de código.
        """
        
        try:
            # Forçamos o envio com o ID que o Google reportou estar disponível
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.1
                ),
                contents=historico_formatado + [
                    types.Content(role="user", parts=[types.Part(text=mensagem)])
                ]
            )
            
            if response and response.text:
                return response.text
            return "Desculpe, João. Pode repetir? Meu sistema oscilou."

        except Exception as e:
            error_msg = str(e)
            print(f"🚨 LOG TÉCNICO INTERNO: {error_msg}")
            
            # Se der 404 de novo com o prefixo, tentamos SEM o prefixo na próxima
            if "404" in error_msg and "models/" in self.model_id:
                self.model_id = "gemini-1.5-flash"
                return "⚠️ Ajustando conexão com o servidor... Tente enviar sua mensagem novamente agora."
                
            if "429" in error_msg:
                return "⚠️ Muita gente negociando agora! Aguarde 15 segundos e clique em Enviar."
                
            return "⚠️ Erro de comunicação. Tente novamente em instantes."
