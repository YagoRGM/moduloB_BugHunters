import serial
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import random
from colorama import Fore, Style, init

init(autoreset=True)  # Para colorir texto no console

# ================== CONFIGURAÇÃO ==================
PORTA_SERIAL = 'COM10'
BAUDRATE = 9600

CSV_FILE = os.path.join('python', 'dados_sensores.csv')
LOG_FILE = os.path.join('python', 'anomalias.log')

TEMP_MAX = 30.0
UMID_MIN = 40.0
UMID_MAX = 70.0

# ================== INICIALIZAÇÃO ==================
os.makedirs('python', exist_ok=True)

try:
    ser = serial.Serial(PORTA_SERIAL, BAUDRATE, timeout=1)
    print(f"{Fore.CYAN}📡 Conectado à porta {PORTA_SERIAL}")
except Exception:
    print(f"{Fore.YELLOW}⚙️  Modo simulação ativado (sem conexão serial).")
    ser = None

if not os.path.isfile(CSV_FILE):
    df = pd.DataFrame(columns=['timestamp', 'node', 'temperatura', 'umidade'])
    df.to_csv(CSV_FILE, index=False)
else:
    df = pd.read_csv(CSV_FILE)

# ================== SIMULAÇÃO DE LEITURA ==================
base_temp = 25.0
base_umid = 55.0
contador_sim = 0

def simular_leitura():
    """
    Gera dados normais e anomalias a cada 4 leituras:
    - 2 normais
    - 1 anomalia alta
    - 1 anomalia baixa
    """
    global base_temp, base_umid, contador_sim
    contador_sim += 1

    fase = contador_sim % 4

    # --- Valores normais ---
    if fase in [1, 2]:
        temp = base_temp + random.uniform(-0.5, 0.5)
        umid = base_umid + random.uniform(-1.5, 1.5)
    else:
        # --- Valores anômalos ---
        if fase == 3:
            temp = TEMP_MAX + random.uniform(1, 5)  # alta
            umid = UMID_MAX + random.uniform(1, 5)  # alta
        else:
            temp = TEMP_MAX - 15 - random.uniform(0, 5)  # baixa
            umid = UMID_MIN - 10 - random.uniform(0, 5)  # baixa

    # Atualiza base para próxima leitura
    base_temp = temp
    base_umid = umid

    # Limitar valores possíveis
    temp = round(max(0, min(50, temp)), 2)
    umid = round(max(0, min(100, umid)), 2)

    return f"Node1 | Temp: {temp:.2f}°C | Umid: {umid:.2f}"

# ================== ESTILO DO GRÁFICO ==================
plt.ion()
sns.set_theme(style='whitegrid')
plt.figure(figsize=(12, 6))

plt.rcParams.update({
    'axes.facecolor': '#ffffff',
    'figure.facecolor': '#ffffff',
    'axes.edgecolor': '#333',
    'grid.color': '#ddd',
    'axes.labelcolor': '#111',
    'xtick.color': '#111',
    'ytick.color': '#111',
    'axes.titlecolor': '#007BFF'
})

# ================== LOOP PRINCIPAL ==================
while True:
    try:
        # Leitura
        if ser:
            linha = ser.readline().decode('utf-8', errors='ignore').strip()
        else:
            time.sleep(1)
            linha = "Recebido: " + simular_leitura()

        if linha and linha.startswith("Recebido:"):
            try:
                linha = linha.replace("Recebido:", "").strip()
                parts = linha.split('|')
                node = parts[0].strip()
                temp = float(parts[1].split(':')[1].replace('°C', '').strip())
                umid = float(parts[2].split(':')[1].strip())
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Salva no DataFrame
                novo_dado = pd.DataFrame([{
                    'timestamp': timestamp,
                    'node': node,
                    'temperatura': temp,
                    'umidade': umid
                }])
                df = pd.concat([df, novo_dado], ignore_index=True)
                df = df.tail(50)
                df.to_csv(CSV_FILE, index=False)

                # ================= DETECÇÃO DE ANOMALIAS =================
                anomalia = []
                if temp > TEMP_MAX:
                    anomalia.append(f"Temperatura alta ({temp}°C)")
                if umid < UMID_MIN or umid > UMID_MAX:
                    anomalia.append(f"Umidade fora dos limites ({umid}%)")

                if anomalia:
                    alerta_texto = f"{timestamp} | {node} | {' | '.join(anomalia)}"
                    with open(LOG_FILE, 'a') as f:
                        f.write(alerta_texto + "\n")
                    print(f"{Fore.RED}⚠️ ANOMALIA DETECTADA: {alerta_texto}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ {timestamp} | {node} OK - Temp: {temp}°C | Umid: {umid}%")

                # ================= GRÁFICO =================
                plt.clf()
                plt.title(f"🌡️ Monitoramento em Tempo Real ({node})", fontsize=18, pad=15)
                plt.xlabel("Timestamp", fontsize=12)
                plt.ylabel("Valor", fontsize=12)

                plt.axhline(TEMP_MAX, color='red', linestyle='--', linewidth=1.2, label=f'Temp Máx {TEMP_MAX}°C')
                plt.axhline(UMID_MIN, color='#ffb300', linestyle='--', linewidth=1.2, label=f'Umid Mín {UMID_MIN}%')
                plt.axhline(UMID_MAX, color='#3ddc97', linestyle='--', linewidth=1.2, label=f'Umid Máx {UMID_MAX}%')

                df_node = df[df['node'] == node]
                plt.plot(df_node['timestamp'], df_node['temperatura'],
                         color='#ff6b6b', linewidth=2.3, marker='o', markersize=6, label='Temperatura (°C)')
                plt.plot(df_node['timestamp'], df_node['umidade'],
                         color='#1dd1a1', linewidth=2.3, marker='s', markersize=6, label='Umidade (%)')

                plt.fill_between(df_node['timestamp'], df_node['temperatura'], color='#ff6b6b', alpha=0.12)
                plt.fill_between(df_node['timestamp'], df_node['umidade'], color='#1dd1a1', alpha=0.12)

                plt.xticks(rotation=45)
                plt.legend(facecolor='#ffffff', edgecolor='#333', fontsize=10)
                plt.grid(alpha=0.25, linestyle=':')
                plt.tight_layout()
                plt.pause(0.05)

            except Exception as parse_err:
                print(f"{Fore.YELLOW}❌ Erro ao processar linha: '{linha}' | {parse_err}")

    except KeyboardInterrupt:
        print(f"{Fore.MAGENTA}🛑 Encerrando script...")
        if ser:
            ser.close()
        break
