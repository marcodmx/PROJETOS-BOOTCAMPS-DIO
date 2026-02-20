import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        # 1. Configuração do Sistema
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. "
            "Seu objetivo é ajudar na reorganização financeira do cliente.\n\n"
            "DIRETRIZES:\n"
            "- Use 'valor em aberto' ou 'solução' em vez de 'dívida' ou 'atraso'.\n"
            "- CET: 14.5% a.a. | Baixa: 3 dias úteis.\n"
            "- FORMATAÇÃO: Valores em <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span>.\n"
            "- BOLETO: Código sempre em bloco de código (```).\n\n"
            f"CONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        # 2. Construção das mensagens com LIMPEZA DE METADADOS
        messages = [{"role": "system", "content": system_msg}]
        
        if historico_formatado:
            for msg in historico_formatado:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # ESTA É A CORREÇÃO: Criamos um novo dict APENAS com role e content
                    # Isso remove o 'metadata' que o Gradio insere e que a Groq rejeita
                    clean_msg = {
                        "role": msg["role"],
                        "content": str(msg["content"])
                    }
                    messages.append(clean_msg)
        
        # 3. Adiciona a pergunta atual do usuário
        messages.append({"role": "user", "content": str(prompt_user)})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.1,
                max_tokens=800
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"🚨 Erro na API Groq: {e}")
            return "⚠️ Tive um desencontro técnico. Poderia repetir?"
