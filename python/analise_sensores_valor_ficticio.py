import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import seaborn as sns
import time
import os
from datetime import datetime
import random
from colorama import Fore, Style, init

init(autoreset=True)

# ================= CONFIGURAÇÃO =================
CSV_FILE = os.path.join('python', 'dados_sensores_ficticios.csv')
RELATORIO_DIR = os.path.join('python', 'relatorios')
LOG_FILE = os.path.join('python', 'anomalias.log')
os.makedirs(RELATORIO_DIR, exist_ok=True)

TEMP_MAX = 30.0
UMID_MIN = 40.0
UMID_MAX = 70.0

# ================= INICIALIZAÇÃO =================
if not os.path.isfile(CSV_FILE):
    df = pd.DataFrame(columns=['timestamp', 'node', 'temperatura', 'umidade'])
    df.to_csv(CSV_FILE, index=False)
else:
    df = pd.read_csv(CSV_FILE)

# ================= SIMULAÇÃO DE LEITURA =================
base_temp = 25.0
base_umid = 55.0
contador_sim = 0

def simular_leitura():
    global base_temp, base_umid, contador_sim
    contador_sim += 1
    fase = contador_sim % 4
    if fase in [1,2]:
        temp = base_temp + random.uniform(-0.5,0.5)
        umid = base_umid + random.uniform(-1.5,1.5)
    else:
        if fase == 3:
            temp = TEMP_MAX + random.uniform(1,5)
            umid = UMID_MAX + random.uniform(1,5)
        else:
            temp = TEMP_MAX - 15 - random.uniform(0,5)
            umid = UMID_MIN - 10 - random.uniform(0,5)
    base_temp = temp
    base_umid = umid
    temp = round(max(0,min(50,temp)),2)
    umid = round(max(0,min(100,umid)),2)
    return f"Node1 | Temp: {temp:.2f}°C | Umid: {umid:.2f}"

# ================= FUNÇÃO DE EXPORTAÇÃO =================
def exportar_relatorio(event):
    try:
        df_rel = pd.read_csv(CSV_FILE)

        # ================= RESUMO =================
        resumo = df_rel.groupby('node').agg(
            Temp_Media=('temperatura','mean'),
            Temp_Max=('temperatura','max'),
            Temp_Min=('temperatura','min'),
            Umid_Media=('umidade','mean'),
            Umid_Max=('umidade','max'),
            Umid_Min=('umidade','min')
        ).round(2)

        # ================= ANOMALIAS E SUGESTOES =================
        df_rel['anomalia'] = ((df_rel['temperatura']>TEMP_MAX) | 
                              (df_rel['umidade']>UMID_MAX) | 
                              (df_rel['umidade']<UMID_MIN))
        total_anomalias = df_rel['anomalia'].sum()

        sugestoes = []
        for node in df_rel['node'].unique():
            node_df = df_rel[df_rel['node']==node]
            if (node_df['temperatura']>TEMP_MAX).mean() > 0.3:
                sugestoes.append(f"Possível superaquecimento persistente no {node} – verifique sistema de ventilação")
            if (node_df['umidade']<UMID_MIN).mean() > 0.3:
                sugestoes.append(f"Umidade muito baixa no {node} – verificar hidratação/umidificador")
            if (node_df['umidade']>UMID_MAX).mean() > 0.3:
                sugestoes.append(f"Umidade muito alta no {node} – verificar ventilação ou sistema de exaustão")

        # ================= GRÁFICO DE TENDENCIA =================
        fig, ax_g = plt.subplots(figsize=(10,5))
        for node in df_rel['node'].unique():
            node_df = df_rel[df_rel['node']==node]
            ax_g.plot(node_df['timestamp'], node_df['temperatura'], marker='o', label=f'{node} Temp')
            ax_g.plot(node_df['timestamp'], node_df['umidade'], marker='s', label=f'{node} Umid')
        ax_g.set_xlabel("Timestamp")
        ax_g.set_ylabel("Valores")
        ax_g.set_title("Tendência de Temperatura e Umidade")
        ax_g.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        grafico_path = os.path.join(RELATORIO_DIR, "grafico_tendencia.png")
        fig.savefig(grafico_path)
        plt.close(fig)

        # ================= EXPORTAR EXCEL =================
        from pandas import ExcelWriter
        nome_arquivo = os.path.join(RELATORIO_DIR, f"Relatorio_3.2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        with ExcelWriter(nome_arquivo) as writer:
            # Página Resumo
            resumo.to_excel(writer, sheet_name='Resumo', index=True)
            # Página Dados completos
            df_rel.to_excel(writer, sheet_name='Dados_Completos', index=False)
            # Página Anomalias e Sugestoes
            pd.DataFrame({
                'Total de Anomalias': [total_anomalias],
                'Sugestoes': [", ".join(sugestoes)]
            }).to_excel(writer, sheet_name='Analise_Preditiva', index=False)

        # ================= EXPORTAR MARKDOWN OPCIONAL =================
        md_file = os.path.join(RELATORIO_DIR, f"Relatorio_3.2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 3.2 - Relatório de Desempenho ou Análise Preditiva\n\n")
            f.write("## Resumo por Nó\n")
            f.write(resumo.to_markdown())
            f.write(f"\n\n## Total de Anomalias: {total_anomalias}\n\n")
            f.write("## Sugestões Automáticas\n")
            for s in sugestoes:
                f.write(f"- {s}\n")
            f.write(f"\n![Gráfico de Tendência]({grafico_path})\n")

        print(f"{Fore.CYAN}{Style.BRIGHT}✅ Relatório Excel gerado: {nome_arquivo}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}✅ Relatório Markdown gerado: {md_file}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}📊 Gráfico de tendência salvo: {grafico_path}{Style.RESET_ALL}")


    except ModuleNotFoundError:
        print("❌ Instale o openpyxl: pip install openpyxl")
    except Exception as e:
        print(f"❌ Erro: {e}")


# ================= CONFIGURAÇÃO DO GRÁFICO REAL TIME =================
sns.set_theme(style='whitegrid')
plt.ion()
fig, ax = plt.subplots(figsize=(12,6))
plt.subplots_adjust(bottom=0.2)
ax.set_title("🌡️ Monitoramento de Dados Fictícios", fontsize=18, color='#0A1F44')
ax.set_xlabel("Timestamp")
ax.set_ylabel("Valor")

# Botão Exportar Relatório
ax_btn = plt.axes([0.81, 0.05, 0.15, 0.075])
btn = Button(ax_btn,'Exportar Relatório')
btn.on_clicked(exportar_relatorio)

# ================= LOOP PRINCIPAL =================
while True:
    try:
        time.sleep(1)
        linha = simular_leitura()
        parts = linha.split('|')
        node = parts[0].strip()
        temp = float(parts[1].split(':')[1].replace('°C','').strip())
        umid = float(parts[2].split(':')[1].strip())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Salvar CSV
        novo_dado = pd.DataFrame([{'timestamp':timestamp,'node':node,'temperatura':temp,'umidade':umid}])
        df = pd.concat([df,novo_dado], ignore_index=True)
        df = df.tail(50)
        df.to_csv(CSV_FILE,index=False)

        # Anomalias
        anomalia = []
        if temp > TEMP_MAX:
            anomalia.append(f"Temperatura alta ({temp}°C)")
        if umid < UMID_MIN or umid > UMID_MAX:
            anomalia.append(f"Umidade fora dos limites ({umid}%)")
        if anomalia:
            alerta_texto = f"{timestamp} | {node} | {' | '.join(anomalia)}"
            with open(LOG_FILE,'a') as f:
                f.write(alerta_texto+'\n')
            print(f"{Fore.RED}⚠️ {alerta_texto}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ {timestamp} | {node} OK - Temp: {temp}°C | Umid: {umid}%")

        # Atualizar gráfico
        ax.clear()
        ax.plot(df['timestamp'], df['temperatura'], color='#ff6b6b', marker='o', label='Temperatura')
        ax.plot(df['timestamp'], df['umidade'], color='#1dd1a1', marker='s', label='Umidade')
        ax.axhline(TEMP_MAX, color='red', linestyle='--', label=f'Temp Máx {TEMP_MAX}°C')
        ax.axhline(UMID_MIN, color='#ffb300', linestyle='--', label=f'Umid Mín {UMID_MIN}%')
        ax.axhline(UMID_MAX, color='#3ddc97', linestyle='--', label=f'Umid Máx {UMID_MAX}%')

        # Reaplicar título e labels
        ax.set_title("🌡️ Monitoramento de Dados Fictícios", fontsize=18, color='#0A1F44')
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Valor")

        ax.set_xticklabels(df['timestamp'], rotation=45)
        ax.legend()
        ax.grid(True, linestyle=':')
        plt.pause(0.05)

    except KeyboardInterrupt:
        print(f"{Fore.MAGENTA}🛑 Encerrando script...")
        break
