# /resultado-mes: filtros avançados

## Intenção
O comercial precisa filtrar a lista de OPs por mais critérios, começando pela Fase.
A coluna de gerente no CSV foi pedida e depois dispensada (2026-11-27): a coluna
"Imobiliária" que já existe atende.

## Filtros avançados
- Botão "Filtros avançados" à esquerda da busca, com a quantidade de filtros ativos.
- Abre um popup (janela sobre a página). No celular ocupa a tela, com rolagem.
- Campos:
  - Fase (várias)
  - Corretor (vários) e Empreendimento (vários)
  - Assinatura (várias): Assinado, Aguardando, Não enviado, Cancelado, Não assinado
  - Sinal (vários): Boleto/PIX, Cartão, Pendente
  - Data: base (Data da venda ou Data Confirmação 2.0), de / até
  - Valor: de / até
  - Ranking (vários, inclui "Sem ranking") e Origem do cliente (várias, inclui "Sem origem")
- As opções das listas vêm das vendas carregadas, já com os filtros do topo.
- Várias marcações no mesmo campo somam; campos diferentes se combinam (E).

## Comportamento (decisão de quem constrói)
- Nada muda até clicar em "Aplicar". Fechar, Esc ou clicar fora descarta. "Limpar" zera o popup.
- Vale para a lista e para o CSV; os cartões do topo não mudam (como os filtros da lista hoje).
- Soma com os filtros atuais (tipo, confirmação, pendência, equipe, busca).
- O "Limpar" da barra e a troca de período zeram também os avançados. Clicar em um número
  da matriz mantém; clicar em uma pendência zera (como hoje com os demais).

## Abordagens
- **Popup (escolhida pelo Gabriel):** cabe muitos campos sem empurrar a lista.
- Linha extra na barra: mais rápida de usar, mas fica alta com tantos campos.

## Fora do escopo
Mudar o Apps Script ou os relatórios do Salesforce.
