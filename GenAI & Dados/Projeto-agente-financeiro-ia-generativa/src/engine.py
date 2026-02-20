import os
import time
from groq import Groq
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class AgenteNegociador:
    """
    Classe responsável pela inteligência de negociação via Groq Cloud.
    Substitui integralmente o motor anterior (Gemini).
    """
    def __init__(self):
        # Recupera a chave de API específica da Groq
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Erro Crítico: Variável GROQ_API_KEY não configurada no ambiente.")
        
        # Inicializa o cliente Groq
        self.client = Groq(api_key=self.api_key)
        
        # Define o modelo estável (Llama 3.1 8B é o melhor custo-benefício em cota gratuita)
        self.model_id = "llama-3.1-8b-instant"
        
        print(f"--- SISTEMA INICIALIZADO ---")
        print(f"✅ Motor Ativo: {self.model_id}")

    def responder(self, mensagem, dados_cliente, historico_formatado):
        """
        Envia a mensagem para a Groq e retorna a proposta de negociação.
        """
        # Instrução de sistema fixa e direta
        prompt_sistema = (
            f"Você é o consultor financeiro da RenovaIA. "
            f"Dados atuais do cliente: {dados_cliente}. "
            "OBJETIVO: Negociar dívidas de forma empática e profissional. "
            "REGRAS: "
            "1. Propostas à vista devem ter o maior desconto possível. "
            "2. Propostas parceladas devem usar taxa de 1.99% a.m. "
            "3. Apresente as opções de pagamento obrigatoriamente em tabelas Markdown. "
            "4. Seja conciso e evite termos jurídicos complexos."
        )

        # Montagem do payload de mensagens no padrão Groq/OpenAI
        mensagens = [{"role": "system", "content": prompt_sistema}]
        
        # Adiciona o histórico de conversa recebido
        for turno in historico_formatado:
            mensagens.append(turno)
        
        # Adiciona a interação atual do usuário
        mensagens.append({"role": "user", "content": mensagem})

        try:
            # Chamada de inferência
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=mensagens,
                temperature=0.2, # Baixa temperatura para respostas financeiras precisas
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            # Retorna o conteúdo da resposta
            return completion.choices[0].message.content

        except Exception as e:
            msg_erro = str(e).lower()
            if "rate_limit" in msg_erro or "429" in msg_erro:
                return "⚠️ **Limite de requisições atingido na Groq.** Por favor, aguarde 30 segundos e tente novamente."
            
            print(f"Erro técnico Groq: {e}")
            return f"🚨 Ocorreu um erro na comunicação com o motor de IA: {str(e)[:50]}"
