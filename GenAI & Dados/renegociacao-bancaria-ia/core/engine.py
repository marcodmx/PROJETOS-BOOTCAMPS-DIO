import os
import re
import ast
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. Seu foco é fechar acordos.\n\n"
            "⚠️ REGRA CRÍTICA DE SEGURANÇA:\n"
            "1. NÃO EXIBA O CÓDIGO DO BOLETO antes que o cliente aceite explicitamente os termos (valor e forma de pagamento).\n"
            "2. Se o cliente pedir o boleto sem ter confirmado o acordo, diga que primeiro precisam chegar a um consenso sobre o valor.\n"
            "3. O boleto é a ÚLTIMA ETAPA. Após o cliente dizer 'eu aceito', apresente o código uma única vez.\n\n"
            "DIRETRIZES GERAIS:\n"
            "- VALORES: <span style=\"font-size: 20px; color: #1e40af; font-weight: bold;\">R$ X.XXX,XX</span>.\n"
            "- BOLETO: Quando autorizado, use bloco de código (```).\n"
            f"CONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        
        if historico_formatado:
            for msg in historico_formatado:
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    if isinstance(content, list): content = content[0] if content else ""
                    messages.append({"role": msg.get("role", "user"), "content": str(content)})
        
        messages.append({"role": "user", "content": str(prompt_user)})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.3
            )
            resposta = completion.choices[0].message.content

            # Sanitização contra vazamento de dicionários
            if resposta.strip().startswith("{") or "text':" in resposta:
                try:
                    res_dict = ast.literal_eval(resposta.strip())
                    if isinstance(res_dict, dict): return res_dict.get('text', resposta)
                except:
                    match = re.search(r"['\"]text['\"]:\s*['\"](.*?)['\"]", resposta, re.DOTALL)
                    if match: return match.group(1)

            return resposta
        except Exception as e:
            print(f"🚨 Erro Groq: {e}")
            return "⚠️ Tive um desencontro técnico. Pode repetir?"
