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
            raise ValueError("Chave de API (GOOGLE_API_KEY) não configurada.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = None

        try:
            # Lista os modelos e imprime para diagnóstico no console do Colab
            modelos = list(self.client.models.list())
            print("--- MODELOS DETECTADOS NA CONTA ---")
            for m in modelos:
                print(f"ID Original: {m.name}")
            
            # Filtra apenas o ID final (ex: de 'models/gemini-1.5-flash' para 'gemini-1.5-flash')
            # Isso resolve o erro 404 em muitas versões do SDK novo
            ids_limpos = {m.name.split("/")[-1]: m.name for m in modelos}
            
            # Prioridade de seleção
            if "gemini-2.0-flash" in ids_limpos:
                self.model_id = "gemini-2.0-flash"
            elif "gemini-1.5-flash" in ids_limpos:
                self.model_id = "gemini-1.5-flash"
            else:
                # Tenta pegar qualquer um que contenha 'flash' como última alternativa
                for clean_id in ids_limpos.keys():
                    if "flash" in clean_id:
                        self.model_id = clean_id
                        break

            if self.model_id:
                print(f"--- MOTOR SELECIONADO: {self.model_id} ---")
            else:
                self.model_id = "gemini-1.5-flash"
                print("Aviso: Utilizando ID padrão por falta de correspondência na lista.")

        except Exception as e:
            print(f"Erro na inicialização: {e}")
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente, historico_formatado):
        prompt_sistema = (
            f"Você é o consultor especializado da RenovaIA. Dados do cliente: {dados_cliente}. "
            "DIRETRIZES: "
            "1. Cordialidade e empatia. "
            "2. Em propostas à vista, cite o Art. 52, § 2º do CDC: o cliente tem direito legal "
            "à liquidação antecipada com redução proporcional dos juros. "
            "3. Em parcelamentos, aplique CET de 1.99% a.m. "
            "4. Formatação: Use tabelas Markdown para comparar À Vista vs. Parcelado."
        )
        
        try:
            # O SDK novo costuma aceitar o model_id sem o prefixo 'models/'
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
            print(f"Erro detalhado na chamada: {e}")
            return f"🚨 Erro no processamento: {str(e)[:50]}"
