import os
import re
import ast
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        # Captura a chave de API do ambiente
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        # PROMPT DE SISTEMA: Ajustado para ação imediata após o "Sim"
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. Seu objetivo é fechar o acordo.\n\n"
            "🚀 GATILHO DE FECHAMENTO:\n"
            "1. Se o cliente disser 'Sim', 'Aceito', 'Confirmo', 'Pode gerar' ou qualquer variação de aceite, "
            "você DEVE fornecer o código do boleto IMEDIATAMENTE na mesma resposta.\n"
            "2. Não peça confirmação sobre algo que já foi aceito. Seja direto e celebre o fechamento.\n"
            "3. O código do boleto deve vir OBRIGATORIAMENTE dentro de um bloco de código Markdown (```) "
            "para que o botão 'Copiar' funcione.\n\n"
            "DIRETRIZES DE ESTILO:\n"
            "- VALORES: Use <span style=\"font-size: 20px; color: #1e40af; font-weight: bold;\">R$ X.XXX,XX</span>.\n"
            "- SEGURANÇA: Não invente valores. Use apenas o que está no contexto abaixo.\n\n"
            f"CONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        # Preparação das mensagens para a API
        messages = [{"role": "system", "content": system_msg}]
        
        # Limpeza do histórico para evitar campos extras que causam Error 400
        if historico_formatado:
            for msg in historico_formatado:
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    # Garante que o conteúdo seja string, mesmo que venha como lista do Gradio
                    if isinstance(content, list): 
                        content = content[0] if content else ""
                    messages.append({
                        "role": msg.get("role", "user"), 
                        "content": str(content)
                    })
        
        messages.append({"role": "user", "content": str(prompt_user)})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.4, # Temperatura equilibrada para persuasão e precisão
                max_tokens=800
            )
            resposta = completion.choices[0].message.content

            # --- SANITIZAÇÃO ANTI-JSON/DICT ---
            # Caso o Gradio ou a IA tentem encapsular a resposta em um dicionário
            if resposta.strip().startswith("{") or "text':" in resposta:
                try:
                    # Tenta converter string de dict em texto puro usando AST
                    res_dict = ast.literal_eval(resposta.strip())
                    if isinstance(res_dict, dict): 
                        return res_dict.get('text', resposta)
                    if isinstance(res_dict, list) and len(res_dict) > 0:
                        return res_dict[0].get('text', resposta)
                except:
                    # Fallback com Regex se a conversão falhar
                    match = re.search(r"['\"]text['\"]:\s*['\"](.*?)['\"]", resposta, re.DOTALL)
                    if match: return match.group(1)

            return resposta

        except Exception as e:
            # Log de erro no console para diagnóstico rápido
            print(f"🚨 Erro crítico na API Groq: {e}")
            return "⚠️ Tive um desencontro técnico ao processar sua proposta. Poderia repetir?"
