# 🏦 RenovaIA: Inteligência Artificial para Renegociação Bancária

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Gradio](https://img.shields.io/badge/Interface-Gradio-orange.svg)
![Groq](https://img.shields.io/badge/LLM-Llama%203.3%20(Groq)-red.svg)
![Status](https://img.shields.io/badge/Status-Finalizado-green.svg)

O **RenovaIA** é um agente inteligente de renegociação de dívidas que utiliza IA Generativa para humanizar o atendimento financeiro. O sistema automatiza a jornada de recuperação de crédito, oferecendo transparência, descontos dinâmicos e fechamento de acordos em tempo real.

---

## 🎯 Diferenciais Estratégicos

* **⚡ Negociação Ultrarrápida:** Implementado sobre a infraestrutura da **Groq**, garantindo latência mínima e alta fluidez na conversa.
* **🛡️ Grounding e Segurança:** Sistema ancorado em dados reais (`clientes_mock.json`). A IA opera sob regras estritas de negócio, evitando alucinações de valores ou prazos.
* **🤖 Engine de Fechamento:** Diferente de chatbots comuns, o RenovaIA possui gatilhos de conversão que geram linhas digitáveis e propostas formais diretamente no chat.
* **📂 Arquitetura Modular:** Código organizado em camadas (Core, Services, Interface) seguindo padrões corporativos de engenharia de software.

---

## 🏗️ Estrutura do Projeto

A organização do repositório reflete uma arquitetura escalável e limpa:

```text
renegociacao-bancaria-ia/
├── core/               # Regras de negócio, cálculos e motor de negociação
├── data/               # Base de conhecimento e configurações (JSON)
├── docs/               # Documentação técnica, métricas e pitch
├── interface/          # UI customizada (Gradio + CSS)
├── services/           # Adaptadores de LLM e configuração de ambiente
└── app.py              # Ponto de entrada e inicialização do sistema
```
---

## 🚀 Como Executar

### 1. Pré-requisitos
* **Python 3.10** ou superior instalado.
* Uma **API Key** válida da [Groq Cloud](https://console.groq.com/).

### 2. Instalação e Configuração
Siga os passos abaixo para configurar o ambiente local:

```bash
# 1. Clone o repositório para sua máquina local
# 2. Acesse a pasta do projeto:
cd "GenAI & Dados/renegociacao-bancaria-ia"

# 3. Instale as dependências necessárias:
pip install -r requirements.txt
```



### 📄 Licença e Autoria
Projeto desenvolvido por **Marco Garcia** como parte do desafio prático no **Bootcamp Bradesco - Geração de IA e Dados** na plataforma **DIO**.
