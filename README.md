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

📌 Conclusão

Este projeto oferece:

Monitoramento em tempo real

Detecção e log de anomalias

Relatórios detalhados e gráficos

Simulação de dados fictícios para teste de anomalias

Preparado para integração com hardware real (Arduino + NRF24L01)

Ideal para ambientes IIoT, protótipos de SmartFactory e estudo de manufatura avançada.