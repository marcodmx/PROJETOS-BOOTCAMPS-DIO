
---
# Base de Conhecimento: RenovaIA

## 1. Visão Geral
A base de conhecimento funciona como a "única fonte da verdade" (Single Source of Truth), garantindo que a IA não invente valores ou condições de pagamento.

## 2. Fontes de Dados
- **Arquivo Principal:** `data/clientes_mock.json`
- **Tipo de Dado:** JSON

## 3. Atributos dos Clientes

| Campo | Descrição |
| :--- | :--- |
| `nome` | Nome completo do titular da conta. |
| `cpf` | Identificador único (mascarado). |
| `dividas` | Lista de objetos de dívida com valores, prazo e status. |
| `oferta_minima_avista` | Valor mínimo que pode ser aceito para quitação à vista. |
| `parcelamento_maximo` | Quantidade máxima de parcelas permitida. |
| `status` | Estado atual da dívida (ex: Inadimplente, Atraso Curto). |

## 4. Regras de Negócio
- Descontos máximos conforme política (`configuracoes_gerais`)
- Limite de parcelas por tipo de produto
- Status de acordo só para clientes inadimplentes
- Transbordo para atendimento humano se não aceitar propostas

## 5. Exemplo JSON
```json
{
  "clientes": [
    {
      "id": 1,
      "nome": "João Silva",
      "cpf": "123.456.789-00",
      "dividas": [
        {
          "produto": "Cartão de Crédito Platinum",
          "valor_original": 2500.00,
          "dias_atraso": 125,
          "juros_acumulados": 450.00,
          "valor_total_atualizado": 2950.00,
          "oferta_minima_avista": 1850.00,
          "parcelamento_maximo": 12,
          "status": "Inadimplente",
          "codigo_boleto_atual": "23790.12345 60000.789012 34567.890123 1 95000000185000"
        }
      ]
    }
  ]
}
