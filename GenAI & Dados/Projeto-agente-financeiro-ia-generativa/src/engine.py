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
        
        # Lógica de Prioridade: 1.5-flash (Mais cota) > 2.0-flash > Fallback
        try:
            modelos_disponiveis = [m.name for m in self.client.models.list()]
            if any("gemini-1.5-flash" in m for m in modelos_disponiveis):
                self.model_id = "gemini-1.5-flash"
            elif any("gemini-2.0-flash" in m for m in modelos_disponiveis):
                self.model_id = "gemini-2.0-flash"
            else:
                self.model_id = modelos_disponiveis[0].replace("models/", "")
            print(f"✅ Motor Selecionado: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"
            print(f"⚠️ Usando fallback fixo: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = (
            f"Você é o consultor sênior da RenovaIA. Dados do Cliente: {dados_cliente}. "
            f"DIRETRIZES DE ATENDIMENTO: "
            f"1. Seja humano, cordial e empático. Não cite leis na saudação inicial. "
            f"2. Utilize o Artigo 52 do CDC apenas como fundamentação técnica ao apresentar propostas de quitação. "
            f"3. Aplique desconto proporcional de juros para antecipação (Art. 52). "
            f"4. Para parcelamentos, utilize CET de 1.99% a.m. "
            f"5. Formate propostas e valores em tabelas Markdown para clareza absoluta."
        )
        
        # Tentativas automáticas para evitar quedas por tráfego
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
                return response.text if response.text else "Poderia repetir sua solicitação?"
            except Exception as e:
                if "429" in str(e) and tentativa < 1:
                    time.sleep(3) # Pausa técnica de 3 segundos
                    continue
                
                # Mensagem profissional para o Protótipo
                if "429" in str(e):
                    return "⚠️ **Sistema Temporariamente Indisponível:** Devido ao alto volume de propostas simultâneas, sua solicitação entrou em fila. Por favor, tente enviar novamente em instantes."
                return f"🚨 **Aviso:** Conexão instável com a central de crédito. Tente novamente."
