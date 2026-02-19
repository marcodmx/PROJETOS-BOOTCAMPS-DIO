import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não configurada!")
        
        self.client = genai.Client(api_key=api_key)
        
        # Forçamos o 1.5-flash por ter uma cota diária muito mais ampla que o 2.0
        self.model_id = "gemini-1.5-flash"
        print(f"🚀 Motor Selecionado: {self.model_id} (Modo Estabilidade)")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = (
            f"Você é o consultor sênior da RenovaIA. Dados do Cliente: {dados_cliente}. "
            "DIRETRIZES DE NEGOCIAÇÃO: "
            "1. Inicie sempre de forma cordial e empática. "
            "2. Utilize o Artigo 52 do CDC apenas para fundamentar propostas de quitação à vista. "
            "3. O Art. 52 garante o desconto proporcional de juros para liquidação antecipada. "
            "4. Para parcelamentos, utilize rigorosamente o CET de 1.99% a.m. "
            "5. Apresente os valores e opções em tabelas Markdown para facilitar a leitura."
        )
        
        # Lógica de Retry para resiliência
        for tentativa in range(2):
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
                return response.text if response.text else "Poderia reformular sua dúvida?"
                
            except Exception as e:
                erro_str = str(e).upper()
                
                # Tratamento específico para limites de tráfego
                if "429" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                    if tentativa < 1:
                        time.sleep(3)
                        continue
                    return "⚠️ **Sistema Temporariamente Indisponível:** Devido ao alto volume de propostas simultâneas, sua solicitação entrou em fila de processamento. Por favor, tente enviar novamente em instantes."
                
                # Tratamento para erros de autenticação
                if "API_KEY" in erro_str or "403" in erro_str:
                    return "🚨 **Erro de Autenticação:** Falha na conexão segura com a central de crédito. Verifique as credenciais do sistema."

                return f"🚨 **Instabilidade Técnica:** Ocorreu um erro inesperado no processamento. (Código: {erro_str[:15]})"
