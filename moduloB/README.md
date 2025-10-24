# 🌡️ SmartFactory Connect – Monitoramento IIoT de Temperatura e Umidade - Bug Hunters

Este projeto implementa um **sistema de monitoramento de sensores de temperatura e umidade** voltado à **manufatura avançada**, simulando um ambiente **Industrial IoT (IIoT)**. Ele inclui:

- Detecção de **anomalias**  
- **Alertas automáticos** no terminal  
- **Relatórios** em Excel e Markdown  
- **Gráficos em tempo real**  
- Simulação de **dados fictícios** ou integração com **sensores reais via Arduino + NRF24L01**

---

## 🔧 Bibliotecas Python Utilizadas

| Biblioteca | Função |
|------------|--------|
| `pandas` | Manipulação de dados, cálculos estatísticos, exportação Excel/Markdown |
| `matplotlib` | Plotagem de gráficos em tempo real |
| `seaborn` | Estilização dos gráficos |
| `matplotlib.widgets.Button` | Botão interativo para exportar relatórios |
| `colorama` | Colorir mensagens no terminal |
| `random` | Gerar dados fictícios para simulação |
| `datetime` | Marcação de timestamp para leituras e relatórios |
| `os` | Criação de diretórios e manipulação de arquivos |

> ⚠️ Para exportação Excel: `pip install openpyxl`

---

## 🏗 Estrutura de Arquivos



python/
│
├─ analisa_sensores.py # Script Python para dados reais
├─ analisa_sensores_valor_ficticio.py # Script Python para dados fictícios com anomalias
├─ dados_sensores.csv # CSV com dados reais
├─ dados_sensores_ficticios.csv # CSV com dados simulados
├─ relatorios/ # Relatórios gerados automaticamente
├─ anomalias.log # Log de anomalias detectadas


---

## ⚡ Funcionalidades

1. **Coleta de dados**
   - **Dados reais** (`analisa_sensores.py`): lê sensores Arduino via Serial e registra temperatura e umidade de cada nó (Node1, Node2, Node3).  
   - **Dados fictícios** (`analisa_sensores_valor_ficticio.py`): gera leituras com variações e anomalias para testes de alerta e análise preditiva.

2. **Detecção de anomalias**
   - Temperatura acima de `TEMP_MAX`  
   - Umidade fora do intervalo (`UMID_MIN` – `UMID_MAX`)  
   - Registra eventos em `anomalias.log`  
   - Exibe alertas coloridos no terminal

3. **Visualização gráfica**
   - Gráfico em tempo real de temperatura e umidade por nó  
   - Limites destacados com linhas tracejadas  
   - Atualização dinâmica a cada segundo

4. **Relatórios automáticos**
   - **Excel**: resumo por nó, dados completos, anomalias e sugestões  
   - **Markdown**: resumo, total de anomalias, sugestões e gráfico de tendência  
   - Sugestões automáticas baseadas em padrões detectados  
   - Arquivos salvos em `relatorios/`

---

## 🔄 Fluxo do Sistema

1. Inicializa CSV e diretórios de relatório.  
2. Lê dados:
   - **Fictícios:** função `simular_leitura()` gera variações e anomalias.  
   - **Reais:** lê Serial do Arduino (CSV formatado: timestamp, Node, temperatura, umidade).  
3. Detecta anomalias e registra log.  
4. Atualiza gráfico em tempo real.  
5. Exporta relatório Excel e Markdown ao clicar no botão "Exportar Relatório" ou finalizar script.

---

## 🔌 Integração com Arduino (Opcional / Avançado)

**Componentes sugeridos:**

- 2x Arduino Uno  
- 1x Sensor DHT11  
- 2x Módulo NRF24L01 (NÃO ligar em 5V)  
- Buzzer, micro servo, LEDs, fios e protoboard  

**Funcionalidades no Arduino:**

- Cada Node lê DHT11 e envia dados via NRF24L01  
- Detecta temperatura crítica:
  - `ALARME_ON` e buzzer acionado  
  - `DESLIGAR_MOTOR` para esteira  
- Quando temperatura normalizada:
  - `ALARME_OFF`  
  - `LIGAR_MOTOR`  

**Receptor central Arduino:**

- Recebe dados de todos os nós  
- Imprime no Serial em formato CSV/JSON para Python  
- Pode receber comandos de controle enviados pelo Python

---

## 📝 Relatórios

- **Resumo por nó**: média, máximo e mínimo de temperatura e umidade  
- **Número total de anomalias detectadas**  
- **Sugestões automáticas**: ex. “Possível superaquecimento persistente no Node2 – verifique sistema de ventilação”  
- **Gráficos de tendência**: temperatura e umidade ao longo do tempo  
- Exportação em **Excel** e **Markdown**  
- Gráficos salvos em `relatorios/grafico_tendencia.png`

---

## 🖥️ Execução

### 1. Com dados fictícios (anomalias garantidas)

```bash
1. Com dados ficticios para variação e anomalias
python analisa_sensores_valor_ficticio.py

2. Com dados reais do Arduino

Ajustar função de leitura para Serial no script analisa_sensores.py:

import serial
ser = serial.Serial('COM3', 9600)  # Ajustar porta
linha = ser.readline().decode().strip()
# Parse para timestamp, node, temperatura, umidade


Executar script:

python analisa_sensores.py

3. Exportar relatórios

Clique no botão “Exportar Relatório” no gráfico ou finalize o script (Ctrl+C)

Relatórios gerados automaticamente em Excel e Markdown na pasta relatorios/

⚙️ Configuração de limites
TEMP_MAX = 30.0    # Temperatura máxima (°C)
UMID_MIN = 40.0    # Umidade mínima (%)
UMID_MAX = 70.0    # Umidade máxima (%)


Ajuste conforme ambiente ou sensores reais.


🚀 Como Executar o Projeto – Passo a Passo Completo

Siga este guia para colocar o sistema funcionando, desde o Arduino até o Python:

1️⃣ Clonar o Repositório

Abra o terminal e execute:

git clone https://github.com/seu_usuario/seu_repositorio.git
cd seu_repositorio/python

2️⃣ Instalar Bibliotecas Python

Instale todas as bibliotecas necessárias:

pip install pandas matplotlib seaborn colorama openpyxl


⚠️ openpyxl é necessária para exportar arquivos Excel.

3️⃣ Preparar Arduino (Nó Sensor)

Monte o circuito no Arduino conforme os vídeos e instruções do projeto:

DHT11 para temperatura e umidade

NRF24L01 (não ligar em 5V, usar 3.3V)

Buzzer e micro servo para alarme e controle de esteira

LEDs indicadores (opcional)

Abra o Arduino IDE, carregue o código do transmissor (transmissor.ino) em cada Arduino.

Ajuste os IDs de nó para Node1, Node2 e Node3.

Configure os pinos de acordo com o hardware montado (DHT, buzzer, servo, NRF24L01).

4️⃣ Preparar Arduino (Estação Receptora)

Monte o segundo Arduino como estação central.

Carregue o código do receptor (receptor.ino).

Conecte ao computador via USB para ler os dados pelo Monitor Serial.

5️⃣ Ajustar Porta Serial no Python

No script analisa_sensores.py, configure a porta correta do Arduino:

import serial
ser = serial.Serial('COM3', 9600)  # Substitua COM3 pela porta do seu Arduino
linha = ser.readline().decode().strip()
# Parse para timestamp, node, temperatura, umidade

6️⃣ Executar Scripts Python

Para dados fictícios (testes de anomalia garantida):

python analisa_sensores_valor_ficticio.py


Para dados reais do Arduino:

python analisa_sensores.py


Durante a execução, o gráfico será atualizado em tempo real e alertas de anomalias aparecerão no terminal.

7️⃣ Exportar Relatórios

Clique no botão “Exportar Relatório” no gráfico

Ou finalize o script (Ctrl+C) para gerar automaticamente.

Relatórios serão salvos na pasta relatorios/ em Excel e Markdown.

8️⃣ Configuração de Limites (opcional)
TEMP_MAX = 30.0    # Temperatura máxima (°C)
UMID_MIN = 40.0    # Umidade mínima (%)
UMID_MAX = 70.0    # Umidade máxima (%)


Ajuste conforme ambiente ou sensores reais.


📌 Conclusão

Este projeto oferece:

Monitoramento em tempo real

Detecção e log de anomalias

Relatórios detalhados e gráficos

Simulação de dados fictícios para teste de anomalias

Preparado para integração com hardware real (Arduino + NRF24L01)

Ideal para ambientes IIoT, protótipos de SmartFactory e estudo de manufatura avançada.