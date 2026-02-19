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
        self.model_id = None
        
        try:
            modelos_disponiveis = [m.name for m in self.client.models.list()]
            # Prioridade 1.5-flash para estabilidade de tráfego
            if any("gemini-1.5-flash" in m for m in modelos_disponiveis):
                self.model_id = "gemini-1.5-flash"
            else:
                self.model_id = "gemini-2.0-flash"
            print(f"✅ Motor Selecionado: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = (
            f"Você é o consultor sênior da RenovaIA. Dados: {dados_cliente}. "
            "1. Seja cordial e empático. "
            "2. Use o Artigo 52 do CDC apenas para fundamentar propostas de quitação. "
            "3. Aplique desconto de juros para antecipação e CET de 1.99% a.m. para parcelas. "
            "4. Responda com tabelas Markdown."
        )
        
        for tentativa in range(2):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    config=types.GenerateContentConfig(system_instruction=prompt_sistema, temperature=0.2),
                    contents=historico_formatado + [types.Content(role="user", parts=[types.Part(text=mensagem)])]
                )
                return response.text if response.text else "Poderia repetir?"
            except Exception as e:
                if "429" in str(e) and tentativa < 1:
                    time.sleep(3)
                    continue
                
                # MENSAGEM CORRIGIDA PARA O PROTÓTIPO:
                if "429" in str(e):
                    return "⚠️ **Sistema Temporariamente Indisponível:** Devido ao alto volume de propostas simultâneas, sua solicitação entrou em fila de processamento. Por favor, tente enviar novamente em instantes."
                return "🚨 **Aviso:** Conexão instável com a central de crédito. Tente novamente."
