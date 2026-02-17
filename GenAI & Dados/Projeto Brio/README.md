# 🦁 Projeto Brio: Assistente de Voz Inteligente

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Google Gemini](https://img.shields.io/badge/google%20gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![OpenAI Whisper](https://img.shields.io/badge/OpenAI%20Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)

## 📌 Sobre o Projeto
O **Brio** é um sistema avançado de conversação por voz desenvolvido para o **Bootcamp Bradesco - Geração de IA e Dados**, realizado na plataforma **DIO (Digital Innovation One)**. O projeto evolui o conceito de interação humano-máquina ao combinar tecnologias de **Speech-to-Text (STT)** e **Text-to-Speech (TTS)** para criar uma experiência fluida e inteligente.

Diferente de assistentes convencionais, o Brio utiliza o **Whisper**, uma tecnologia de Reconhecimento Automático de Fala (ASR) da OpenAI treinada com 680.000 horas de dados multilíngues. Isso garante robustez contra sotaques e ruídos de fundo. Para a camada de inteligência, o projeto integra o modelo **Gemini 1.5 Flash da Google**, proporcionando respostas rápidas e contextuais com alta eficiência.

---

## 🛠️ Tecnologias Utilizadas

A solução foi construída sobre um ecossistema tecnológico diversificado para garantir o melhor desempenho em cada etapa:

* **ASR (Automatic Speech Recognition):** [OpenAI Whisper](https://github.com/openai/whisper) – Transcrição de áudio com precisão técnica e suporte multilíngue.
* **LLM (Large Language Model):** [Google Gemini 1.5 Flash](https://aistudio.google.com/) – O "cérebro" do sistema, configurado com *System Instructions* para atuar como um assistente bancário profissional.
* **TTS (Text-to-Speech):** [Google gTTS](https://pypi.org/project/gTTS/) – Conversão da resposta textual em voz, configurado com cadência otimizada (`slow=False`).
* **Interface:** JavaScript (MediaStream Recording API) e HTML5/CSS3 para uma interface visual de alta legibilidade desenvolvida no Google Colab.

---

## 🚀 Diferenciais Estratégicos (O Tripé do Projeto)

A apresentação deste projeto na **DIO** fundamenta-se em três pilares essenciais para o setor financeiro:

1.  **Acessibilidade e Inclusão:** O Brio remove barreiras de interação. Ao permitir consultas e comandos 100% por voz, o projeto foca na inclusão de pessoas com deficiência visual, idosos ou usuários com limitações motoras, alinhando a tecnologia à responsabilidade social do **Bradesco**.

2.  **Segurança e Eficiência Operacional:** Ao utilizar modelos de baixa latência como o Gemini 1.5 Flash, o sistema reduz o tempo de espera do cliente. A arquitetura foi desenhada para que a comunicação seja direta e eficiente, tratando a linguagem técnica bancária de forma natural.

3.  **Abordagem Multicloud:** O projeto demonstra maturidade técnica ao não depender de um único provedor. A integração entre **OpenAI** (Whisper) e **Google Cloud** (Gemini e gTTS) prova que é possível extrair o melhor de cada plataforma para criar uma solução robusta e resiliente.

---

## 🖥️ Experiência Visual e Interface
Um dos maiores focos deste desenvolvimento foi a **Interface de Usuário (UI)**. Através de estilização CSS customizada, os resultados são apresentados em cards de alta legibilidade:

* **Exibição Integral:** A interface foi programada para ser dinâmica, garantindo que **nenhuma informação seja cortada**, independentemente da extensão da resposta gerada pela IA.
* **Hierarquia Visual:** Fontes em tamanho ampliado (**26px**) e separação clara por cores facilitam a leitura e a compreensão imediata dos dados apresentados.

---

## ⚙️ Como Executar
1. Abra o notebook no **Google Colab**.
2. Configure sua `API_KEY` do Google Gemini.
3. Execute as células de inicialização para carregar os modelos Whisper e Gemini.
4. Utilize o comando de voz para interagir com o Brio e acompanhe a transcrição e resposta visual nos cards.

---

### 📄 Licença e Autoria
Projeto desenvolvido por **Marco Garcia** como parte do desafio prático no **Bootcamp Bradesco - Geração de IA e Dados** na plataforma **DIO**.
