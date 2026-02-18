# Base de Conhecimento: RenovaIA

## 1. Descrição dos Dados
Esta base contém informações fictícias de clientes inadimplentes, simulando um extrato de conta para renegociação. O objetivo é permitir que a IA realize o "Grounding" (ancoragem), evitando que ela invente valores ou condições de pagamento.

## 2. Estrutura do Arquivo JSON
Os dados estão organizados por CPF, contendo:
- **Dados Pessoais:** Nome e CPF.
- **Detalhamento da Dívida:** Produto, valor original, dias de atraso e juros.
- **Regras de Acordo:** Valor mínimo aceitável para quitação e parcelas permitidas.

## 3. Políticas de Negociação (Regras de Negócio)
- **Desconto à Vista:** Até 30% de desconto para dívidas com mais de 90 dias de atraso.
- **Parcelamento:** Em até 12x com juros de 1% ao mês sobre o saldo devedor.
- **Segunda Via:** Boletos só podem ser gerados para acordos com status "Pendente".

------
*Nota: Todos os CPFs e nomes neste projeto são gerados aleatoriamente para fins de teste.*
