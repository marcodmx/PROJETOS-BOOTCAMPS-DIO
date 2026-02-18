# Base de Conhecimento: RenovaIA

## 1. Visão Geral
Este documento descreve a estrutura de dados utilizada pelo Agente RenovaIA para realizar consultas e negociações. A base de conhecimento funciona como a "única fonte da verdade" (Single Source of Truth), garantindo que a IA não invente valores ou condições de pagamento.

## 2. Fontes de Dados
Os dados estão centralizados em um arquivo estruturado que simula um sistema bancário legado:
- **Arquivo Principal:** `data/base_conhecimento.json`
- **Tipo de Dado:** JSON

## 3. Atributos dos Clientes
Cada registro de cliente na base de conhecimento contém os seguintes campos obrigatórios:

| Campo | Descrição |
| :--- | :--- |
| `nome` | Nome completo do titular da conta. |
| `cpf` | Identificador único (mascarado para segurança). |
| `produto` | Tipo de dívida (Cartão, Empréstimo, Financiamento). |
| `valor_original` | Valor principal da dívida antes dos juros. |
| `dias_atraso` | Tempo de inadimplência (essencial para cálculo de descontos). |
| `oferta_minima` | O menor valor que a IA pode aceitar para quitação à vista. |

## 4. Regras de Negócio e Políticas
O Agente deve seguir rigorosamente as diretrizes abaixo durante a interação:

- [x] **Cálculo de Desconto:** Dívidas acima de 90 dias podem receber até 30% de desconto no valor total.
- [x] **Parcelamento:** Limite máximo de 12 parcelas para cartões e 24 para empréstimos pessoais.
- [x] **Status de Acordo:** Somente clientes com status "Inadimplente" recebem ofertas ativas de negociação.
- [x] **Transbordo:** Casos onde o cliente não aceita nenhuma das 3 propostas automáticas devem ser encaminhados ao suporte humano.

---

## 5. Exemplo de Estrutura (JSON)
O modelo de dados segue o padrão abaixo para facilitar a leitura da LLM:

```json
{
  "cliente": {
    "nome": "Exemplo",
    "divida": 1000.00,
    "politica": "Max 12x"
  }
}
