# Resultado do mês: vários empreendimentos e vários meses

Aprovado em 2026-11-26.

**Intenção:** o comercial quer ver juntos os números de mais de um empreendimento e de mais de um mês.

**Escopo**
- Empreendimento: seleção múltipla com caixas de marcar. Nenhum marcado = todos. Cidade continua simples; ao escolher uma cidade, saem os empreendimentos marcados de outras cidades.
- Período, aba Mês: marcar quaisquer meses (separados ou de anos diferentes) e clicar em Aplicar. Limpar volta ao estado sem marcação (Aplicar desativado).
- A página inteira mostra a soma. Não há quadro mês a mês (não-objetivo).
- Trimestre e Ano continuam como atalho de um clique, um só por vez. Cidade e Imobiliária continuam simples.
- Título: "Vendas de setembro + novembro 2026". Com vários meses as setas ficam desativadas.

**Abordagens**
1. (escolhida) Buscar cada mês no Web App atual, com cache por mês, e juntar no navegador. Nada a publicar no Apps Script. Cada venda conta em um único mês, então a junção não duplica. A primeira carga é mais lenta.
2. Web App aceitar uma lista de meses. Uma requisição só, mas exige publicar versão nova no Apps Script.

**Decisões do desenvolvedor:** no máximo 3 buscas simultâneas; se um mês falhar, mostra o erro (nunca soma parcial); "Atualizado às" usa a carga mais antiga; a lista de OPs pagina em 300 como no trimestre.
