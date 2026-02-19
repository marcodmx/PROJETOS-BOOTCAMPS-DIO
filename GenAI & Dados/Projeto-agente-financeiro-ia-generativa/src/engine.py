import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        # O novo SDK busca automaticamente a chave se o nome da var for GEMINI_API_KEY
        # Mas vamos manter explícito para garantir o funcionamento no Colab
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada nos Segredos do Colab/ENV!")
        
        # Conforme o guia de migração: Cliente centralizado
        self.client = genai.Client(api_key=api_key)
        
        # Usamos apenas o ID curto, o SDK novo cuida do mapeamento interno
        self.model_id = "gemini-1.5-flash"
        print(f"🚀 Motor Inicializado: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = (
            f"Você é o consultor sênior da RenovaIA. Dados: {dados_cliente}. "
            "1. Cordialidade e empatia sempre. "
            "2. Use Art. 52 do CDC para descontos em quitação à vista. "
            "3. Use CET de 1.99% a.m. para parcelamentos. "
            "4. Responda com tabelas Markdown."
        )
        
        for tentativa in range(2):
            try:
                # O método correto do novo SDK conforme o guia de migração
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=historico_formatado + [
                        types.Content(role="user", parts=[types.Part(text=mensagem)])
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=prompt_sistema,
                        temperature=0.2
                    )
                )
                
                if response.text:
                    return response.text
                return "Desculpe, não consegui gerar uma resposta. Pode tentar novamente?"

            except Exception as e:
                erro_str = str(e).upper()
                
                # Tratamento de Cota (429) - O que vimos às 4 da manhã
                if "429" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                    if tentativa < 1:
                        time.sleep(3)
                        continue
                    return "⚠️ **Sistema em Alta Demanda:** Sua proposta está em fila. Tente enviar novamente em instantes."
                
                # Tratamento do 404 que você recebeu agora
                if "404" in erro_str:
                    return "🚨 **Erro de Configuração (404):** O modelo não foi encontrado. Verifique se a chave de API tem permissão para o Gemini 1.5-Flash."

                print(f"DEBUG: {e}")
                return f"🚨 **Instabilidade Técnica:** Ocorreu um erro inesperado ({erro_str[:10]})."
