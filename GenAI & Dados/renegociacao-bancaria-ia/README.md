# Agente Inteligente de Renegociação Bancária

## 📌 Objetivo

Desenvolver um agente conversacional com IA capaz de auxiliar clientes na renegociação de dívidas, respeitando regras institucionais, limites operacionais e boas práticas de governança.

---

## 🏗 Arquitetura

- `core/` → regras de negócio
- `services/` → integração com LLM
- `interface/` → camada de apresentação
- `data/` → base mockada

Separação clara de responsabilidades.

---

## 🔒 Regras de Governança

- Limite máximo de 3 tentativas
- Propostas limitadas às regras do sistema
- Mudança de estado ao fechar acordo
- Validação básica de CPF

---

## 🤖 Modelo Utilizado

- Llama 3 via Groq API

---

## ▶ Como Executar

```bash
pip install -r requirements.txt
export GROQ_API_KEY="sua_chave"
python app.py
