# AGENTS.md — Projeto Fila do Almoco

## Estado Atual (atualizado em 08/09/2026)

O sistema foi **migrado do notebook para o celular**. O programa principal agora é um único arquivo HTML:

- **`fila_almoco.html`** ← arquivo principal (versão celular, roda offline)
  - Obs: atualmente este arquivo está salvo na pasta como `fila_almoco parte final 100% confirmado.html` (mesmo conteúdo)
  - Tip: acesse rápido com `Start-Process "fila_almoco parte final 100% confirmado.html"`

### Como funciona o novo fluxo
1. Página web única (`fila_almoco.html`), roda **offline** no navegador do celular (sem internet, WiFi ou servidor)
2. O celular espelha a tela inteira na TV via **stick HDMI receptor** (opção "Transmitir" do painel do celular)
3. Tela única espelhada: o que aparece no celular = o que aparece na TV
4. Voz do anúncio sai pelo navegador do celular (speechSynthesis)

### Funcionalidades do `fila_almoco.html`
- Duas filas: Fila 1 (primeiros anos) azul, Fila 2 (segundos/terceiros) vermelho
- Timer regressivo (configurável 5-600s), pausa entre chamadas (0-60s, exibida em laranja)
- Turmas por dia da semana (segunda a sexta), vindas do config.yaml
- Aba CONFIG: edita timer, pausa e turmas; salva no celular (localStorage)
- Aviso de orientação: em retrato na tela de exibição pede para deitar o celular
- Navegação: clicar em dia estando na CONFIG volta ao display; botões "← VOLTAR SEM SALVAR" e "SALVAR E VOLTAR"
- Detalhe voz: precisa **tocar uma vez na tela** antes para liberar áudio (política de autoplay do celular)

## Arquivos do projeto
- `fila_almoco.html` — versão celular (USAR este)
- `main.py` — versão antiga do notebook (PyQt6 + Flask + QR). Mantida, mas **fora de uso**
- `web_server.py` — servidor Flask da versão antiga (fora de uso)
- `config.yaml` — turmas/timer em formato YAML (usado pela versão antiga)
- `projeto-fila-almoco.md` — documentação do projeto (usa "1A" mas config usa "1ºA")
- `README.md`
- `registro-sessao-2026-09-08.md` — registro detalhado da sessão de hoje
- `imagens do projeto/` — capturas de tela

## GitHub (em andamento)
- Repositório: https://github.com/osjotajjj-debug/Lunch_Line.git
- Git local configurado: user.name `osjotajjj-debug`, user.email `osjotajjj@gmail.com`
- Commit local: `6841784` (11 arquivos)
- **PENDENTE**: autenticação no GitHub (gh auth login / device code) e `git push -u origin main`
- Instalados via winget: Git 2.55.0.3 e GitHub CLI 2.100.0

## Anotações úteis
- As turmas reais usam formato com "º" (ex: 1ºA, 3ºB)
- Config do dia padrão: segunda/sexta Fila1 [1ºA,1ºB,1ºC,1ºD,2ºA], etc. (ver `config.yaml`)
- O QR code do servidor web NÃO é mais necessário (não existe servidor)
- Ambiente: Windows, shell PowerShell

## Comandos úteis
- Abrir versão celular: `Start-Process "fila_almoco.html"` (ou `python -m http.server` para testar local)
- Versão notebook (legada): `python main.py`
- Push GitHub: pedir login primeiro (`gh auth login --web`) depois `git push -u origin main`