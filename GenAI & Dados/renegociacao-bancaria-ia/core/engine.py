import os
from groq import Groq

class AgenteNegociador:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=self.api_key)
        self.model_id = "llama-3.3-70b-versatile"

    def responder(self, prompt_user, contexto_cliente, historico_formatado):
        # 15 PARÂMETROS DE CONTROLE E SEGURANÇA (SYSTEM INSTRUCTIONS)
        # 1. Autenticidade: Só falar com base no CPF validado.
        # 2. Sigilo Bancário: Não revelar dados de outros clientes.
        # 3. Compliance BACEN: Proibido prometer juros zero sem autorização.
        # 4. Transparência: Sempre informar o valor total com encargos.
        # 5. Empatia Situacional: Detectar se o cliente está estressado.
        # 6. Gatilho de Escassez: Informar validade da oferta.
        # 7. Upsell de Parcelamento: Oferecer parcelas que cabem no bolso.
        # 8. Incentivo de Adiantamento: Explicar o abatimento de juros.
        # 9. Verificação de Identidade: Não pedir senhas ou tokens.
        # 10. Linguagem Inclusiva: Sem jargões técnicos bancários complexos.
        # 11. Resiliência: Saber lidar com recusas sem ser insistente.
        # 12. Confirmação Dupla: Antes de gerar o boleto, confirmar os valores.
        # 13. Limite de Alucinação: Se não souber, direcionar para o botão 'Ajuda'.
        # 14. Prevenção de Fraude: Informar que o boleto é emitido pela RenovaIA.
        # 15. Etiqueta Digital: Responder Small Talk com elegância (sem grosseria).

        system_msg = (
            "Você é o Estrategista de Negociação da RenovaIA. "
            "Sua meta é converter dívidas em acordos sustentáveis usando inteligência comportamental."
            "\n\nREGRAS DE OURO PARA FECHAMENTO:"
            "\n- ABATIMENTO DE JUROS: Se o cliente hesitar no valor total, explique: 'Adiantar parcelas ou pagar à vista garante o abatimento proporcional de juros (Regulamentação BACEN)'."
            "\n- PSICOLOGIA FINANCEIRA: Use frases como 'Vamos limpar seu nome hoje para você recuperar seu crédito no mercado?'."
            "\n- TEMPO CERTO: Se o cliente reclamar do valor, ofereça imediatamente o parcelamento como alternativa de fôlego financeiro."
            "\n- SEGURANÇA: Nunca peça dados sensíveis. Informe que todo o processo segue as normas do Banco Central."
            f"\n\nCONTEXTO DO CLIENTE (DADOS REAIS): {contexto_cliente}"
        )

        messages = [{"role": "system", "content": system_msg}]
        messages.extend(historico_formatado)
        messages.append({"role": "user", "content": prompt_user})

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.45, # Ligeiramente mais alto para fluidez natural, mas seguro.
                max_tokens=1000,
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"🤔 Tive um desencontro técnico. Podemos tentar novamente? (Erro: {str(e)})"
