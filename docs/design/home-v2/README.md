# Home V2 — referência visual aprovada

Canvas aprovado em 30/10/2026: https://claude.ai/artifact/EXA8gKipsovaU11Atc1n8E

## Arquivos

- `fonte/Main.dc.html` — Home desktop (página fluida). Todo o CSS, as animações (abertura, entrada, flutuação dos ícones) e os estados de hover estão no `<helmet><style>`.
- `fonte/MobileHome.dc.html` — Home a 390 px (menu em folha, cidades empilhadas, carrossel com um card por vez e bolinhas).
- `fonte/EmBreve.dc.html` e `fonte/MobileEmBreve.dc.html` — tela "Em breve" do Match de Unidades.
- `fonte/canvas.json` — disposição das quatro telas no canvas.
- `assets/` — fotos das cidades já recortadas em 1200×800 e os dois ícones 3D novos.

As URLs `/_blob/<id>` dentro dos `.dc.html` só valem no canvas. No site, use os arquivos do repositório:

| No canvas | No repositório |
|---|---|
| logo grande da abertura | `assets/img/logo-direcional.jpg` |
| logo da navbar | `assets/img/logo-direcional-header.png` |
| ícones 3D (prédio, pino, alvo, moedas) | `assets/img/icones-3d/{predio,pino,alvo,moedas}.svg` |
| ícones 3D novos | `assets/img/icones-3d/{calculadora,tabela}.svg` (vêm de `assets/` desta pasta) |
| fotos das cidades | `assets/img/cidades/<id-da-cidade>.webp` (vêm de `assets/` desta pasta) |
| fotos dos empreendimentos | `assets/img/cards/<id>@640.webp` (já existem) |

## Origem das fotos

As três fotos de cidade foram enviadas pelo Gabriel na conversa de design. Confirmar o direito de uso antes de publicar.
