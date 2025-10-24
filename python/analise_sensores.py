import serial
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import random

# ----------------- CONFIGURAÇÃO -----------------
PORTA_SERIAL = 'COM10'
BAUDRATE = 9600

# Arquivos
CSV_FILE = os.path.join('python', 'dados_sensores.csv')
LOG_FILE = os.path.join('python', 'anomalias.log')

# Limites
TEMP_MAX = 30.0
UMID_MIN = 40.0
UMID_MAX = 70.0

# ----------------- INICIALIZAÇÃO -----------------
os.makedirs('python', exist_ok=True)

# Simulação: caso não tenha serial, comentar a linha abaixo
try:
    ser = serial.Serial(PORTA_SERIAL, BAUDRATE, timeout=1)
    print(f"📡 Conectado à porta {PORTA_SERIAL}")
except Exception:
    print(f"⚙️ Modo simulação ativado (sem conexão serial).")
    ser = None

# DataFrame inicial
if not os.path.isfile(CSV_FILE):
    df = pd.DataFrame(columns=['timestamp', 'node', 'temperatura', 'umidade'])
    df.to_csv(CSV_FILE, index=False)
else:
    df = pd.read_csv(CSV_FILE)

# ----------------- ESTILO DO GRÁFICO -----------------
plt.ion()
sns.set_theme(style='whitegrid')
plt.style.use('dark_background')
plt.figure(figsize=(12, 6))
plt.rcParams['axes.facecolor'] = '#111'
plt.rcParams['figure.facecolor'] = '#000'
plt.rcParams['axes.edgecolor'] = '#444'
plt.rcParams['grid.color'] = '#333'

# ----------------- FUNÇÃO DE SIMULAÇÃO -----------------
base_temp = 25.0
base_umid = 55.0
variacoes = [3, -2, 2, -3, 1, -1]  # padrão de variação cíclica
indice_var = 0

def simular_leitura():
    """Gera dados fictícios de temperatura e umidade com leve oscilação."""
    global base_temp, base_umid, indice_var
    var = variacoes[indice_var % len(variacoes)]
    base_temp += var * 0.3  # ajuste gradual
    base_umid += random.uniform(-1.5, 1.5)
    base_temp = max(20, min(35, base_temp))
    base_umid = max(35, min(75, base_umid))
    indice_var += 1
    return f"Node1 | Temp: {base_temp:.2f}°C | Umid: {base_umid:.2f}"

# ----------------- LOOP PRINCIPAL -----------------
while True:
    try:
        if ser:
            linha = ser.readline().decode('utf-8', errors='ignore').strip()
        else:
            # Modo simulação
            time.sleep(1)
            linha = "Recebido: " + simular_leitura()

        if linha and linha.startswith("Recebido:"):
            try:
                linha = linha.replace("Recebido:", "").strip()
                parts = linha.split('|')
                node = parts[0].strip()
                temp = float(parts[1].split(':')[1].replace('°C', '').strip())
                umid = float(parts[2].split(':')[1].strip())
                timestamp = datetime.now().strftime('%H:%M:%S')

                # Atualiza DataFrame
                novo_dado = pd.DataFrame([{
                    'timestamp': timestamp,
                    'node': node,
                    'temperatura': temp,
                    'umidade': umid
                }])
                df = pd.concat([df, novo_dado], ignore_index=True)
                if len(df) > 30:  # mantém apenas os últimos 30 pontos
                    df = df.tail(30)
                df.to_csv(CSV_FILE, index=False)

                # ----------------- ANOMALIAS -----------------
                anomalia = []
                if temp > TEMP_MAX:
                    anomalia.append(f"Temp alta ({temp}°C)")
                if umid < UMID_MIN or umid > UMID_MAX:
                    anomalia.append(f"Umid fora ({umid}%)")
                if anomalia:
                    with open(LOG_FILE, 'a') as f:
                        f.write(f'{timestamp} | {node} | {" | ".join(anomalia)}\n')
                    print(f"⚠️ {timestamp}: {' | '.join(anomalia)}")

                # ----------------- GRÁFICO -----------------
                plt.clf()
                plt.title(f"🌡️ Monitoramento em tempo real ({node})", fontsize=18, color='#00c1ff', pad=15)
                plt.xlabel("Tempo", fontsize=12, color='#ddd')
                plt.ylabel("Valor", fontsize=12, color='#ddd')

                # Linhas de limite
                plt.axhline(TEMP_MAX, color='red', linestyle='--', linewidth=1.2, label=f'Temp Max {TEMP_MAX}°C')
                plt.axhline(UMID_MIN, color='orange', linestyle='--', linewidth=1.2, label=f'Umid Min {UMID_MIN}%')
                plt.axhline(UMID_MAX, color='orange', linestyle='--', linewidth=1.2, label=f'Umid Max {UMID_MAX}%')

                df_node = df[df['node'] == node]
                plt.plot(df_node['timestamp'], df_node['temperatura'],
                         color='#ff6b6b', linewidth=2.5, marker='o', markersize=6, label='Temperatura (°C)')
                plt.plot(df_node['timestamp'], df_node['umidade'],
                         color='#1dd1a1', linewidth=2.5, marker='s', markersize=6, label='Umidade (%)')

                plt.fill_between(df_node['timestamp'], df_node['temperatura'],
                                 color='#ff6b6b', alpha=0.15)
                plt.fill_between(df_node['timestamp'], df_node['umidade'],
                                 color='#1dd1a1', alpha=0.15)

                plt.xticks(rotation=45, color='#bbb')
                plt.yticks(color='#bbb')
                plt.legend(facecolor='#111', edgecolor='#444', fontsize=10)
                plt.grid(alpha=0.3, linestyle=':')
                plt.tight_layout()
                plt.pause(0.05)

            except Exception as parse_err:
                print(f"❌ Erro ao processar linha: '{linha}' | {parse_err}")

    except KeyboardInterrupt:
        print("🛑 Encerrando script...")
        if ser:
            ser.close()
        break
