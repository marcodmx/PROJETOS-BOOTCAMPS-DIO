import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        system_msg = (
            "Você é o Facilitador Estratégico da RenovaIA. Sua missão é converter a reorganização financeira em fechamento."
            "\n\nDIRETRIZ DE NEGOCIAÇÃO EVOLUTIVA:"
            "\n- Acompanhe o fluxo da conversa: se o cliente recusar a primeira oferta, mude a estratégia (ofereça parcelamento, destaque o abatimento de juros ou mencione a análise do setor)."
            "\n- Persista na negociação de forma diplomática até exaurir as possibilidades do contexto."
            "\n\nPROTOCOLO ZERO ALUCINAÇÃO (CRÍTICO):"
            "\n- Use EXCLUSIVAMENTE os dados reais fornecidos no CONTEXTO (Valores, CET, Produto, Margem)."
            "\n- É terminantemente PROIBIDO inventar descontos, números, porcentagens ou prazos que não estejam nos dados."
            "\n- Se o cliente pedir algo fora dos parâmetros, informe que 'no momento o sistema não permite essa condição específica'."
            "\n\nREGRAS VISUAIS:"
            "\n- VALORES: <span style='font-size: 20px; color: #1e40af; font-weight: bold;'>R$ X.XXX,XX</span>."
            "\n- BOLETO: Bloco de código Markdown puro (```) isolado para habilitar o botão de cópia."
            f"\n\nCONTEXTO REAL (FONTE ÚNICA DA VERDADE): {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.1, # Rigidez factual mantida
                max_tokens=600
            )
            return completion.choices[0].message.content
        except:
            return "🤔 Tive um desencontro técnico. Podemos tentar novamente em instantes?"
