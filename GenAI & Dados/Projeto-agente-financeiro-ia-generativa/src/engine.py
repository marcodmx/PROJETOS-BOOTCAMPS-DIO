import os
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
        
        # Lógica de Prioridade: 1.5-flash (Estável) > Outros > Fallback
        try:
            modelos_disponiveis = [m.name for m in self.client.models.list()]
            
            # Buscamos o 1.5-flash primeiro por ser mais generoso na cota
            if any("gemini-1.5-flash" in m for m in modelos_disponiveis):
                self.model_id = "gemini-1.5-flash"
            # Se não houver, tentamos o 2.0-flash
            elif any("gemini-2.0-flash" in m for m in modelos_disponiveis):
                self.model_id = "gemini-2.0-flash"
            # Fallback para o primeiro da lista se nenhum dos acima existir
            else:
                self.model_id = modelos_disponiveis[0].replace("models/", "")
                
            print(f"✅ Motor inteligente: Prioridade 1.5-flash. Selecionado: {self.model_id}")
        except Exception as e:
            print(f"⚠️ Erro ao consultar modelos, usando fallback fixo: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = (
            f"Você é o consultor sênior da RenovaIA. Dados do Cliente: {dados_cliente}. "
            f"COMPORTAMENTO: "
            f"1. Cordialidade e empatia total. "
            f"2. Artigo 52 do CDC apenas para fundamentar propostas de quitação. "
            f"3. CET de 1.99% a.m. para parcelamentos. "
            f"4. Respostas técnicas em tabelas Markdown."
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
            return response.text if response.text else "Poderia repetir a pergunta?"
        except Exception as e:
            if "429" in str(e):
                return "⚠️ Cota temporariamente atingida. Por favor, aguarde alguns segundos antes de tentar novamente."
            return f"🚨 Erro no processamento: {str(e)}"
