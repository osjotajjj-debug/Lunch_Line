# Registro da Sessão — 08/09/2026

## Projeto: Fila do Almoco (Sistema de Chamada por Voz)

## Contexto Inicial
- O projeto já estava na fase final do desenvolvimento para **notebook** (main.py + PyQt6 + config.yaml)
- Faltavam itens físicos: teste no ambiente real, instalação, controle remoto via celular

## Mudança de Direção Importante
Decidiu-se **abandonar o notebook como dispositivo principal** e mover o sistema para o **celular**, com exibição na TV via **stick HDMI receptor** (os baratinhos da China, que só recebem espelhamento).

### Como funciona o novo fluxo
1. O programa vira uma **página web única** (`fila_almoco.html`)
2. Roda **offline** no navegador do celular (não precisa de internet, WiFi ou servidor)
3. O celular espelha a tela inteira na TV através do stick (opção "Transmitir" do painel do celular)
4. O que aparece no celular = o que aparece na TV (tela única espelhada)
5. A voz do anúncio sai pelo próprio navegador do celular (speechSynthesis)

## O Arquivo `fila_almoco.html` (versão celular)
- **Mesmo projeto** da versão notebook: duas filas (Fila 1 primeiros anos, Fila 2 segundos/terceiros anos), timer regressivo, pausa entre chamadas, anúncio por voz
- Turmas configuradas por dia da semana (segunda a sexta), vindas do config.yaml atual
- Aba de configurações: tempo do timer, pausa, edição de turmas (adicionar/remover) — salva no celular via localStorage
- Autossuficiente: um único HTML, sem dependências externas

### Ajustes feitos ao longo do dia
1. **Layout TV/espelho**: refinado para modo paisagem (deitado) com fontes grandes; modo retrato funcional em pé
2. **Botões touch**: feedback visual ao tocar (sombra, "apertar"), tamanhos confortáveis para o polegar
3. **Correção da voz**: o navegador do celular bloqueava a fala até o primeiro toque (autoplay) e as vezes descarregava as vozes em português com atraso
   - Solução: carregar vozes pt automaticamente, desbloquear áudio no primeiro toque, atraso após cancel(), resume() periódico
   - Precisa tocar uma vez na tela antes de falar (política do próprio celular)
4. **Aviso de orientação**: se o celular está em pé (retrato) na tela de exibição, aparece "Gire o celular para o modo deitado"
5. **Bug da navegação CONFIG**: estava confuso (usuário achava que travava ao clicar nos dias da semana)
   - Agora: clicar num dia de cima estando nas configurações volta para a tela do dia
   - Botão CONFIG fica verde quando ativo; dias da semana ficam esmaecidos
   - Botões claros: "← VOLTAR SEM SALVAR" (roxo) e "SALVAR E VOLTAR" (verde)
   - Dica amarela no topo explicando como sair

## Envio para o GitHub (em andamento)
- **Instalado**: Git 2.55.0.3 (via winget) e GitHub CLI 2.100.0
- **Repositório**: https://github.com/osjotajjj-debug/Lunch_Line.git (nome `fila-do-almoco` escolhido, mas o usuário criou como `Lunch_Line`)
- Config do Git local: user.name `osjotajjj-debug`, user.email `osjotajjj@gmail.com`
- Commit criado localmente: `6841784` "Sistema de Fila do Almoco: versao celular + notebook" (11 arquivos)
- **Pendências**:
  - Autenticação no GitHub ainda não concluída (faça o login do gh cli / Git Credential Manager)
  - Depois de autenticar: `git push -u origin main`

## Arquivos no repositório (commit local)
- `.gitignore` (ignora `__pycache__/`)
- `README.md`
- `config.yaml`
- `fila_almoco.html` ← **novo arquivo principal (versão celular)**
- `main.py` (versão notebook, mantida)
- `projeto-fila-almoco.md`
- `requirements.txt`
- `web_server.py` (servidor Flask da versão antiga, mantido)
- `imagens do projeto/` (capturas de tela)

## Decisões de Hoje
- [x] Programa migrado para o celular (HTML único offline)
- [x] Espelho via stick na TV validado (está funcionando)
- [x] Voz corrigida no celular
- [x] Navegação CONFIG corrigida e clarificada para uso real
- [x] Git local iniciado + commit criado
- [ ] Push para o GitHub (aguardando login na conta)

## Conclusões Importantes para o Projeto
- O computador/notebook **não é mais necessário** para o funcionamento diário
- O controle remoto via celular substituiu completamente o servidor Flask/QR code (que era para conectar o celular ao notebook)
- O QR code não faz mais sentido no novo formato (não existe servidor)
- A única dependência do celular é: navegador, voz em português, e o espelhamento via stick