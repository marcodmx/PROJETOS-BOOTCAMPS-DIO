import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        # SYSTEM PROMPT: Focado em experiência do usuário e diretrizes de negócio
        system_msg = (
            "Você é o especialista em sucesso financeiro da RenovaIA. "
            "Sua postura deve unir o melhor de dois mundos: a agilidade e empatia de uma Fintech "
            "com a segurança e robustez de uma grande instituição financeira tradicional."
            "\n\nDIRETRIZES DE ATENDIMENTO:"
            "\n1. TONE OF VOICE: Use uma linguagem clara, direta e acolhedora. Evite termos bancários complexos."
            "\n2. PROGRESSÃO: Não sobrecarregue o cliente com informações. Vá evoluindo a conversa conforme ele responde."
            "\n3. INTERPRETAÇÃO: Se o cliente enviar apenas números (1, 2) ou termos curtos, entenda isso como "
            "a escolha das opções apresentadas na sua mensagem anterior."
            "\n4. OBJETIVO: Facilitar a quitação da dívida. Se ele aceitar uma oferta, confirme e pergunte a data de pagamento."
            "\n\nCONTEXTO DO CLIENTE (DADOS REAIS):"
            f"\n{contexto_cliente}"
            "\n\nIMPORTANTE: Se o cliente rejeitar as opções, mostre-se parceiro para buscar alternativas, "
            "mantendo sempre o limite do que os dados acima permitem."
        )

        # Montagem correta da memória da conversa
        messages = [{"role": "system", "content": system_msg}]
        
        # O histórico formatado garante que a IA lembre o que acabou de sugerir
        messages.extend(historico_formatado)
        
        # A nova interação do usuário entra por último
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.4, # Equilíbrio entre criatividade e precisão nas regras
                max_tokens=800
            )
            return completion.choices[0].message.content
        except Exception as e:
            # Resposta amigável em caso de erro técnico
            return f"🤔 Sabe, tive um pequeno problema técnico aqui agora. Poderia me enviar sua mensagem novamente? (Erro: {str(e)})"
