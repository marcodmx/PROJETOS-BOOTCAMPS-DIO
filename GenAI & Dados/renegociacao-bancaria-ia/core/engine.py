import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        # Tenta pegar a chave do ambiente
        self.api_key = os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            print("❌ ERRO: Variável GROQ_API_KEY não encontrada!")
        
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        # Se o contexto vier como string de dicionário, tentamos deixar ele mais limpo
        # para a IA focar no que importa: a primeira dívida da lista.
        
        system_msg = (
            "Você é o Facilitador Estratégico do Banco RenovaIA S.A. Seu objetivo é ajudar na reorganização financeira."
            "\n\nDIRETRIZES:"
            "\n- NUNCA use: 'dívida', 'atraso' ou 'pendência'. Use: 'valor em aberto' ou 'solução'."
            "\n- FATOS: Use os valores reais do contexto. CET 14.5% a.a. Baixa em 3 dias úteis."
            "\n- NEGOCIAÇÃO: Se o cliente quiser desconto, diga que enviou para o 'Setor de Liberação' analisar."
            "\n\nFORMATAÇÃO:"
            "\n- VALORES: <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span>."
            "\n- BOLETO: O código deve estar SOZINHO em bloco de código (```)."
            f"\n\nCONTEXTO DO CLIENTE: {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        
        # Garante que o histórico passe corretamente
        if historico_formatado:
            messages.extend(historico_formatado)
            
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.1,
                max_tokens=600
            )
            return completion.choices[0].message.content
        except Exception as e:
            # Imprime o erro real no console para você saber o que houve
            print(f"🚨 Erro na API Groq: {e}")
            return f"⚠️ Tive um desencontro técnico ao processar sua solicitação. (Erro: {type(e).__name__})"
