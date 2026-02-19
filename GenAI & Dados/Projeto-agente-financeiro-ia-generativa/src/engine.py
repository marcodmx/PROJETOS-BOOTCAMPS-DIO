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
            # Prioriza 1.5-flash por ser o cavalo de batalha da Free Tier
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
            "1. Cordialidade e empatia. "
            "2. Use Art. 52 do CDC apenas para fundamentar propostas. "
            "3. Aplique desconto de juros para antecipação e CET de 1.99% a.m. "
            "4. Responda em tabelas Markdown."
        )
        
        for tentativa in range(2):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    config=types.GenerateContentConfig(system_instruction=prompt_sistema, temperature=0.2),
                    contents=historico_formatado + [types.Content(role="user", parts=[types.Part(text=mensagem)])]
                )
                return response.text if response.text else "Poderia reformular sua pergunta?"
                
            except Exception as e:
                erro_str = str(e).upper()
                
                # Tratamento para excesso de tráfego/cota
                if "429" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                    if tentativa < 1:
                        time.sleep(3)
                        continue
                    return "⚠️ **Sistema Temporariamente Indisponível:** Devido ao alto volume de propostas simultâneas, sua solicitação entrou em fila de processamento. Por favor, tente enviar novamente em instantes."
                
                # Tratamento para erro de autenticação (Chave errada)
                if "API_KEY" in erro_str or "403" in erro_str:
                    return "🚨 **Erro de Autenticação:** Falha na conexão segura com a central de crédito. Verifique suas credenciais."

                # Tratamento para qualquer outro erro técnico
                print(f"DEBUG ERRO REAL: {e}")
                return f"🚨 **Instabilidade Técnica:** Ocorreu um erro inesperado no processamento. (Código: {erro_str[:15]})"
