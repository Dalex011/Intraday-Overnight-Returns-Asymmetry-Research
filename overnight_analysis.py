import numpy as np
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import warnings
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.express as px
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')


#US MARKET
#tickers = ["SPY", "IWM", "QQQ", "RSP"]

#US 11 Sectors
tickers = ["SPY", "XLK", "XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLU"]

#US Stocks
#tickers = ["SPY", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "HD", "WMT", "PG", "XOM", "CVX", "JPM", "BAC", "UNH", "JNJ", "CAT", "HON", "LIN", "APD", "PLD", "AMT", "NEE", "SO"]

#Estreme Case: Micron
#tickers = ["SPY", "MU"]


stocks = yf.download(tickers, period="10y", interval="1d")

opens = stocks["Open"]
closes = stocks["Close"]
inversion_inicial = 1000

intraday_returns = ((closes - opens) / opens).fillna(0)
overnight_returns = ((opens - closes.shift(1)) / closes.shift(1)).fillna(0)

port_ret_intraday = intraday_returns.mean(axis=1)
port_ret_overnight = overnight_returns.mean(axis=1)

capital_intraday = (1 + intraday_returns).cumprod() * inversion_inicial
capital_overnight = (1 + overnight_returns).cumprod() * inversion_inicial

port_cap_intraday = (1 + port_ret_intraday).cumprod() * inversion_inicial
port_cap_overnight = (1 + port_ret_overnight).cumprod() * inversion_inicial

delta_capital = capital_overnight - capital_intraday

colores = plt.cm.tab20(np.linspace(0, 1, len(tickers)))

plt.figure(figsize=(12, 6))
for ticker, color in zip(tickers, colores):
    plt.plot(delta_capital.index, delta_capital[ticker], label=ticker, color=color, linewidth=1.2)
plt.axhline(0, color='black', linestyle='--', linewidth=1.5, label='Equilibrio')
plt.title("1. Asimetría de Retornos: Overnight vs Intradía (Delta Individual)")
plt.ylabel("Diferencia a favor de Overnight ($)")
plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize='small', ncol=2)
plt.grid(True, alpha=0.3)
plt.tight_layout()


fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
for ticker, color in zip(tickers, colores):
    ax1.plot(capital_intraday.index, capital_intraday[ticker], label=ticker, color=color, linewidth=1.2)
    ax2.plot(capital_overnight.index, capital_overnight[ticker], label=ticker, color=color, linewidth=1.2)
ax1.set_title("2A. Crecimiento Individual: Sesión Intradía")
ax1.set_ylabel("Capital ($)")
ax1.grid(True, alpha=0.3)
ax2.set_title("2B. Crecimiento Individual: Sesión Overnight")
ax2.set_ylabel("Capital ($)")
ax2.grid(True, alpha=0.3)
ax2.legend(loc="center left", bbox_to_anchor=(1, 1), fontsize='small', ncol=1)
fig2.tight_layout()


plt.figure(figsize=(10, 5))
plt.plot(port_cap_intraday.index, port_cap_intraday, label="Portafolio Intradía", color="red", linewidth=2)
plt.plot(port_cap_overnight.index, port_cap_overnight, label="Portafolio Overnight", color="blue", linewidth=2)
plt.title("3. Comportamiento Agregado del Portafolio (Promedio de todas las acciones)")
plt.ylabel("Capital Promedio ($)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()


resumen_estadistico = []

def plot_distribution_analysis(ret_intra, ret_over, name):
    mean_in, std_in, skew_in, kurt_in = ret_intra.mean(), ret_intra.std(), ret_intra.skew(), ret_intra.kurtosis()
    mean_ov, std_ov, skew_ov, kurt_ov = ret_over.mean(), ret_over.std(), ret_over.skew(), ret_over.kurtosis()
    
    resumen_estadistico.append({
        "Activo": name,
        "Media Intradía (%)": round(mean_in * 100, 4),
        "Media Overnight (%)": round(mean_ov * 100, 4),
        "Std Intradía (%)": round(std_in * 100, 4),
        "Std Overnight (%)": round(std_ov * 100, 4),
        "Skewness Intradía": round(skew_in, 4),
        "Skewness Overnight": round(skew_ov, 4),
        "Kurtosis Intradía": round(kurt_in, 4),
        "Kurtosis Overnight": round(kurt_ov, 4)
    })

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f"Análisis de Riesgo de Cola: {name}", fontsize=16, fontweight='bold')
    
    ax1 = axes[0]
    sns.histplot(ret_intra, bins=100, stat='density', alpha=0.3, color='red', label='Intradía', ax=ax1)
    sns.kdeplot(ret_intra, color='red', linewidth=2, ax=ax1)
    sns.histplot(ret_over, bins=100, stat='density', alpha=0.3, color='blue', label='Overnight', ax=ax1)
    sns.kdeplot(ret_over, color='blue', linewidth=2, ax=ax1)
    
    mu, std = stats.norm.fit(np.concatenate([ret_intra, ret_over]))
    xmin, xmax = ax1.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    ax1.plot(x, stats.norm.pdf(x, mu, std), 'k--', linewidth=2, label='Normal Teórica')
    
    textstr = (
        f"Intradía:\n Media: {mean_in*100:.3f}%\n Vol: {std_in*100:.2f}%\n Skew: {skew_in:.2f}\n Kurt: {kurt_in:.2f}\n\n"
        f"Overnight:\n Media: {mean_ov*100:.3f}%\n Vol: {std_ov*100:.2f}%\n Skew: {skew_ov:.2f}\n Kurt: {kurt_ov:.2f}"
    )
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray'))
    ax1.set_title("KDE & Histograma")
    ax1.set_xlim([mu - 5*std, mu + 5*std])
    ax1.legend(loc='upper right')

    ax2 = axes[1]
    stats.probplot(ret_intra, dist="norm", plot=ax2)
    lineas = ax2.get_lines()
    lineas[0].set(markerfacecolor='red', markeredgecolor='red', markersize=4, alpha=0.4, label='Intradía')
    lineas[1].set(color='red', linestyle='--')
    
    stats.probplot(ret_over, dist="norm", plot=ax2)
    lineas = ax2.get_lines()
    lineas[2].set(markerfacecolor='blue', markeredgecolor='blue', markersize=4, alpha=0.4, label='Overnight')
    lineas[3].set(color='blue')

    ax2.set_title("Q-Q Plot Overlay: Comparación de Colas")
    ax2.legend(loc="upper left")
    plt.tight_layout()

for ticker in tickers:
    plot_distribution_analysis(intraday_returns[ticker], overnight_returns[ticker], ticker)


plot_distribution_analysis(port_ret_intraday, port_ret_overnight, "PORTAFOLIO EQUIPONDERADO")


rf_annual = 0.05
rf_daily = (1 + rf_annual)**(1/252) - 1

rf_intraday = rf_daily * (6.5 / 24)
rf_overnight = rf_daily * (17.5 / 24)

resumen_avanzado = []

def calcular_metricas(retornos_activo, retornos_bench, rf_prorrateado, nombre, sesion):
    exceso_activo = retornos_activo - rf_prorrateado
    exceso_bench = retornos_bench - rf_prorrateado
    

    sharpe = (exceso_activo.mean() / exceso_activo.std()) * np.sqrt(252)
    
    # CAPM (Alpha & Appraisal)
    X = sm.add_constant(exceso_bench)
    modelo = sm.OLS(exceso_activo, X).fit()
    alpha_diario = modelo.params.iloc[0]
    alpha_anualizado = alpha_diario * 252
    appraisal = alpha_anualizado / (modelo.resid.std() * np.sqrt(252)) if modelo.resid.std() > 0 else np.nan
    
    # Maximum Drawdown (MDD)
    capital_acumulado = (1 + retornos_activo).cumprod()
    drawdown = (capital_acumulado - capital_acumulado.cummax()) / capital_acumulado.cummax()
    mdd = drawdown.min()
    
    # Capture Ratios
    mercado_alcista = retornos_bench > 0
    mercado_bajista = retornos_bench < 0
    captura_up = retornos_activo[mercado_alcista].mean() / retornos_bench[mercado_alcista].mean() if len(retornos_activo[mercado_alcista]) > 0 else np.nan
    captura_down = retornos_activo[mercado_bajista].mean() / retornos_bench[mercado_bajista].mean() if len(retornos_activo[mercado_bajista]) > 0 else np.nan
    ratio_captura = captura_up / captura_down if captura_down and captura_down != 0 else np.nan
    
    resumen_avanzado.append({
        "Activo": nombre,
        "Sesión": sesion,
        "Sharpe": round(sharpe, 3),
        "Alpha Jensen": round(alpha_anualizado, 4),
        "Appraisal Ratio": round(appraisal, 3),
        "MDD (%)": round(mdd * 100, 2),
        "Up Capture": round(captura_up, 2),
        "Down Capture": round(captura_down, 2),
        "Capture Ratio (Up/Down)": round(ratio_captura, 2)
    })

# Benchmark es el S&P 500 (SPY)
for ticker in tickers:
    calcular_metricas(intraday_returns[ticker], intraday_returns["SPY"], rf_intraday, ticker, "Intradía")
    calcular_metricas(overnight_returns[ticker], overnight_returns["SPY"], rf_overnight, ticker, "Overnight")

# Portafolio Equiponderado
calcular_metricas(port_ret_intraday, intraday_returns["SPY"], rf_intraday, "PORTAFOLIO EQUIPONDERADO", "Intradía")
calcular_metricas(port_ret_overnight, overnight_returns["SPY"], rf_overnight, "PORTAFOLIO EQUIPONDERADO", "Overnight")



df_metricas = pd.DataFrame(resumen_avanzado)

resumen_dist_limpio = []
for registro in resumen_estadistico:
    # Fila Intradía
    resumen_dist_limpio.append({
        "Activo": registro["Activo"],
        "Sesión": "Intradía",
        "Media (%)": registro["Media Intradía (%)"],
        "Std (%)": registro["Std Intradía (%)"],
        "Skewness": registro["Skewness Intradía"],
        "Kurtosis": registro["Kurtosis Intradía"]
    })
    # Fila Overnight
    resumen_dist_limpio.append({
        "Activo": registro["Activo"],
        "Sesión": "Overnight",
        "Media (%)": registro["Media Overnight (%)"],
        "Std (%)": registro["Std Overnight (%)"],
        "Skewness": registro["Skewness Overnight"],
        "Kurtosis": registro["Kurtosis Overnight"]
    })

df_dist = pd.DataFrame(resumen_dist_limpio)

df_reporte_limpio = pd.merge(df_dist, df_metricas, on=["Activo", "Sesión"], how="inner")

df_reporte_limpio = df_reporte_limpio.sort_values(by=["Activo", "Sesión"], ascending=[True, True])

columnas_ordenadas = [
    "Activo", "Sesión", "Media (%)", "Std (%)", "Skewness", "Kurtosis",
    "Sharpe", "Alpha Jensen", "Appraisal Ratio", "MDD (%)", 
    "Up Capture", "Down Capture", "Capture Ratio (Up/Down)"
]
df_reporte_limpio = df_reporte_limpio[columnas_ordenadas]

nombre_archivo_limpio = "reporte_limpio_overnight.txt"
df_reporte_limpio.to_csv(nombre_archivo_limpio, sep='\t', index=False)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\n=======================================================================================================================")
print("REPORTE MAESTRO REESTRUCTURADO (Con Risk-Free Rate prorrateado correctamente):")
print("=======================================================================================================================")
print(df_reporte_limpio.head(12).to_string(index=False))
print(f"\n¡Listo! El archivo se ha guardado con TODA la información completa en: '{nombre_archivo_limpio}'")


cap_intra_export = capital_intraday.copy()
cap_intra_export["PORTAFOLIO EQUIPONDERADO"] = port_cap_intraday

cap_over_export = capital_overnight.copy()
cap_over_export["PORTAFOLIO EQUIPONDERADO"] = port_cap_overnight

cap_intra_export.columns = [f"{c} (Intradía)" for c in cap_intra_export.columns]
cap_over_export.columns = [f"{c} (Overnight)" for c in cap_over_export.columns]

cap_total = pd.concat([cap_intra_export, cap_over_export], axis=1)

primer_dia = cap_total.iloc[[0]]
ultimo_dia = cap_total.iloc[[-1]]

#6 Month aggregate
medio_ano = cap_total.resample('6M').last() 

df_crecimiento = pd.concat([primer_dia, medio_ano, ultimo_dia])
df_crecimiento = df_crecimiento[~df_crecimiento.index.duplicated(keep='last')].sort_index()

df_crecimiento = df_crecimiento.round(2)
df_crecimiento.index = df_crecimiento.index.strftime('%Y-%m-%d')
df_crecimiento.index.name = "Fecha"

nombre_archivo_crecimiento = "crecimiento_capital_semestral.txt"
df_crecimiento.to_csv(nombre_archivo_crecimiento, sep='\t')

print(f"¡Datos de crecimiento para gráficos exportados en: '{nombre_archivo_crecimiento}'")

plt.show()