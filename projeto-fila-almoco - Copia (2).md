# Sistema de Lista de Chamada por Comando de Voz - Fila do Almoço

## Visão Geral do Projeto

Sistema automatizado de gerenciamento de fila do almoço escolar, utilizando voz e telas para organizar a chamada de turmas. Projeto desenvolvido para a matéria de Base Técnica (PPI).

## Funcionamento do Sistema

### Fluxo Principal
1. Um timer é iniciado para cada fila (contagem regressiva)
2. Ao final do timer, uma pausa configurável permite que os alunos se movam
3. Uma voz automatizada anuncia a próxima turma
4. A turma é direcionada à fila correspondente
5. O ciclo se repete automaticamente

### Estrutura de Filas
- **Fila 1:** Turmas de primeiros anos
- **Fila 2:** Turmas de segundos e terceiros anos
- As duas filas funcionam **em paralelo**, cada uma com seu próprio timer e sequência de turmas

### Organização das Turmas
- A ordem das turmas na fila é organizada por dia da semana (conforme a folha existente na escola)
- A configuração é estática (a escola possui calendário fixo, sem alterações frequentes)
- As turmas são configuradas diretamente no programa, por dia da semana

### Anúncio de Voz
- **Voz SAPI (Windows)** com seleção automática de voz em português
- Exemplo de anúncio: "Turma 1A, dirija-se à fila 1"
- Fallback silencioso caso a voz não esteja disponível

### Interface Visual (TVs)
- **Duas TVs** conectadas ao notebook via HDMI
- Exibição na tela:
  - Fila atual sendo chamada
  - Próximas turmas que entrarão na fila
  - Countdown do timer
  - Indicador de pausa entre chamadas
- Complemento visual: papel/cartaz identificando fisicamente qual é a Fila 1 e Fila 2

## Infraestrutura

### Hardware
- **Notebook** da escola
- **2 TVs** (não smart)
- **2 Stick HDMI** para exibir a tela do notebook
- Conexão com o sistema de rádio da escola (caixas de som)

### Cabamento
- Cabeamento de áudio para integração com a rádio da escola
- Cabeamento HDMI para as TVs
- Planejamento: furar paredes de uma vez para evitar retrabalho

### Software
- Programa principal de controle
- Módulo de timer automático com pausa configurável
- Módulo de texto-para-fala (TTS) via SAPI/Windows
- Interface visual para as TVs
- Configuração de turmas por dia da semana

### Tecnologia Definida
- **Linguagem:** Python 3.12
- **Interface:** PyQt6
- **TTS:** SAPI via comtypes (voz nativa Windows)
- **Timer:** QTimer (PyQt6)
- **Configuração:** YAML (pyyaml)

## Instruções de Instalação

1. Instale Python 3.12 para o usuário atual
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o programa:
```bash
python main.py
```

## Configuração

Edite o arquivo `config.yaml` ou use a aba CONFIGURACOES no programa:
- **Timer:** Duração da contagem regressiva (5-600 segundos)
- **Pausa entre chamadas:** Tempo de espera entre turmas (0-60 segundos)
- **Turmas por dia:** Configurar fila1 e fila2 para cada dia da semana

### Exemplo config.yaml:
```yaml
turmas:
  segunda:
    fila1: ["1A", "1B", "1C", "1D"]
    fila2: ["2A", "2B", "3A", "3B"]
  terca:
    fila1: ["1B", "1C", "1D", "1A"]
    fila2: ["2B", "3A", "3B", "2A"]
timer:
  segundos: 30
  pausa_entre_chamadas: 5
```

## Funcionalidades Implementadas

- [x] Duas filas independentes com timers separados
- [x] Contagem regressiva visual (minutos:segundos)
- [x] Pausa automática entre chamadas (cor laranja no display)
- [x] Voz automatizada anunciando turmas
- [x] Botões: INICIAR / PARAR / CHAMAR (avanço manual)
- [x] Abas por dia da semana (SEGUNDA a SEXTA)
- [x] Aba de CONFIGURACOES com:
  - Configuração do tempo do timer
  - Configuração da pausa entre chamadas
  - Seleção de dia da semana
  - Gerenciamento de turmas por fila (adicionar/remover)
  - Botão SALVAR por dia específico
- [x] Tratamento de erros no carregamento do config.yaml
- [x] Config padrão caso o arquivo não exista
- [x] Interface dark theme responsiva (1920x1080)
- [x] Reset automático dos painéis ao recarregar config

## Observações

- O projeto visa melhorar o conforto dos alunos nos corredores no horário do almoço, evitando tumulto
- A integração com a rádio da escola reduz custo e complexidade
- O calendário escolar é fixo, o que simplifica a configuração
- As duas filas funcionam simultaneamente e independentemente
- O sistema é Windows-only (usa SAPI e winsound nativos)

## Status

- [x] Conceito definido
- [x] Fluxo do sistema planejado
- [x] Estrutura de filas definida
- [x] Infraestrutura planejada
- [x] Definição da tecnologia/linguagem de desenvolvimento
- [x] Desenvolvimento do programa (estrutura funcional)
- [x] Aba de configurações funcionando por dia
- [x] Pausa entre chamadas implementada
- [x] Tratamento de erros e fallback
- [x] Interface visual dark theme
- [ ] Teste em ambiente real (notebook + TVs + rádio)
- [ ] Definição do hardware (notebook)
- [ ] Instalação física (cabeamento, TVs, sticks)
- [ ] Consideração de controle remoto via celular (pendente - sem WiFi disponível)
