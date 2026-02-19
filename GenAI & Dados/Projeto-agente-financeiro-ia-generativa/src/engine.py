import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AgenteNegociador:
    def __init__(self):
        # 1. Carrega a chave de API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erro: Variável GOOGLE_API_KEY não configurada!")
            
        # 2. Inicializa o cliente
        self.client = genai.Client(api_key=api_key)
        
        # 3. Busca automática do modelo (Evita erro 404)
        try:
            available_models = [m.name for m in self.client.models.list()]
            target = "gemini-1.5-flash"
            self.model_id = next((m for m in available_models if target in m), available_models[0])
            if self.model_id.startswith("models/"):
                self.model_id = self.model_id.replace("models/", "")
            print(f"✅ Motor de Negociação Ativo: {self.model_id}")
        except Exception as e:
            self.model_id = "gemini-1.5-flash"

    def responder(self, mensagem, dados_cliente):
        """
        Gera resposta respeitando o contexto da escolha (1 ou 2), 
        apresentando CET e código copiável.
        """
        
        # O "Cérebro" com as regras de contexto e fechamento
        prompt_sistema = f"""
        Você é o motor de fechamento da RenovaIA. Sua missão é converter a conversa em um acordo formal.

        DADOS DO CLIENTE LOCALIZADOS:
        {dados_cliente}

        ### REGRAS DE OURO DO FLUXO:

        1. RECONHECIMENTO DE CONTEXTO: Se o usuário aceitar uma das opções propostas (ex: digitando '1', '2', 'a primeira', 'quero parcelar', etc.):
           - Identifique IMEDIATAMENTE qual oferta ele escolheu.
           - PARE de repetir saudações ou introduções.
           - Responda: "Excelente escolha, [Nome]! Você optou pelo [Nome da Opção]. Veja os detalhes do acordo:"
           - Apresente a TABELA DE CET (Custo Efetivo Total):
             * Principal: R$ [Valor]
             * Multa/Juros: R$ [Valor]
             * Desconto: -R$ [Valor]
             * **TOTAL FINAL: R$ [Valor]**
           - Pergunte: "Posso formalizar e gerar o código de barras para você?"

        2. CÓDIGO COPIÁVEL: Se o usuário confirmar ('Sim', 'Pode', 'Gerar'), responda com:
           "Parabéns! 🥂 Seu acordo foi concluído. Este passo é fundamental para sua liberdade financeira."
           Exiba o código de barras EXATAMENTE neste bloco para habilitar o botão de copiar:
           ```
           23790.12345 60000.789012 34567.890123 1 95000000185000
           ```
           - Vencimento: D+2 (2 dias úteis a partir de hoje).
           - Aviso: Pagamentos após o vencimento cancelam o desconto e o acordo.

        3. WHATSAPP: Somente após o código estar na tela, pergunte se ele deseja receber a cópia no WhatsApp.

        4. POSTURA: Seja empático, profissional e use **NEGRITO** para valores. Se ele sair do fluxo, lembre-o gentilmente que precisa concluir o acordo escolhido.
        """
        
        try:
            # 4. Chamada para a geração de conteúdo
            response = self.client.models.generate_content(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.7,
                    top_p=0.95
                ),
                contents=[mensagem]
            )
            return response.text
        except Exception as e:
            return f"❌ Erro na negociação: {str(e)}"
