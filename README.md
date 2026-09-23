# Intraday-Overnight-Returns-Asymmetry-Research
Ongoing investigation regarding intraday-overnight returns asymmetry in the US and Chilean stock market.

This is my first-ever GitHub repository, so I apologize in advance for any mistake I might make while I learn to navigate the platform!

## **Motivation**

The main goal behind this investigation is to experiment with overnight-intraday returns behavior. I intend to learn about the different risk-to-reward characteristics of these time periods, explore what may cause them, and eventually test whether this well documented anomaly holds true in the Chilean market and in what form.

To achieve this goal, I plan on using mainly Python coupled with the appropriate libraries, Excel, and Bloomberg data when needed, extracted from the terminals of my university.

Although this is a topic that has been extensively researched for the past 50 or so years, applying it to the Chilean market appears to be new territory. This repo documents the US pilot phase, where I mainly focus on replicating known patterns and testing my own methodology.

Even though this is my first time doing such research, I will still attempt to find interesting results and learn from my mistakes along the way.

## **Key Findings**

Universe: SPY + 11 SPDR sector ETFs, equal-weighted portfolio, daily data, ≈10 years (Sep 2016 - Sep 2026)

<img width="1200" height="600" alt="return_asymmetry_delta" src="https://github.com/user-attachments/assets/45555821-0c3d-4689-a5a6-2cc970e62196" />

- The overnight return bias holds true for 11 of the 13 assets, having higher daily mean returns and sharpe ratios in the overnight period compared to their intraday counterparts. Health (XLV) and Basic Needs (XLP) being the notable exceptions to this rule.
- Energy (XLE) is by far the most extreme case, having negative annualized mean returns (-3.78%) for the intraday period while having a substantial positive annualized mean returns (18.85%) for the overnight period. Over the sample period an intraday-only strategy would have lost ≈46% of total capital; an overnight-only strategy multiplied it by more than 5x. Sharpe -0.23 intraday vs. 0.80 overnight.
- Most of the sector-level "edge" is just market beta. After regressing each sector's overnight excess return on SPY's overnight retuns most of the remaining alpha is flat or negative. Energy is the only outlier in this regard.
- It's not free lunch. Overnight returns show considerable negative skewness (delta -2.40 vs. intraday skew) and heavy kurtosis values; 44.26 overnight vs. 6.85 intraday, signaling a substantial risk of black-swan events which can be specially catastrophic for leveraged investors. This increased risk is consistent with risk-premium theories as compensation for higher returns.

## **Methodology**
- Sessions: overnight return =(Open_t - Close_t-1) / Close_t-1; intraday return = (Close_t - Open_t) / Open_t, based on historical prices adjusted for splits.
- Risk-free rate: annualized ≈5% (3-month T-bill proxy), compounded to a daily rate. An earlier version of this analysis double counted the risk-free rate by subtracting it from both sessions independently, this has been corrected by time-weighting the daily rate according to session length (17.5/24 for overnight, 6.5/24 for intraday).
- Sharpe ratio: E[Rp - Rf] / σp * √252.
- Jensen's Alpha / Appraisal ratio: OLS regression of Rp - Rf = α + β(Rm - Rf) + ε
run separately per session, with SPY as the market benchmark. Appraisal ratio = (α*252) / (σ_ε * √252).

## **Reproducing this**
pip install -r requirements.txt
python src/overnight_analysis.py

Data is pulled live via yfinance, so results will drift slightly from the committed data file as new trading days are added.

## **Limitations**
- Ten years of data is a small sample for skewness and kurtosis analysis, especially with key events like the Covid-19 pandemic (2020) taking place within the analyzed period, which likely has outsized influence and hasn't been taken into account yet.
- Sector ETF's are not a liquidity sort; They're a convenient, data-rich way to plot the mechanics of the calculation. The actual liquidity-based cross-sectional tests happens in the Chile phase.

## **Next steps**
Extending this framework to the Chilean equity market (IPSA constituents), which, as far as I've researched hasn't been tested through this specific overnight/intraday lens. That phase will use a cross-sectional panel regression (liquidity, size, and sector controls) rather than a single-index comparison, directly motivated by the significance caveat above.

## **License**
MIT — see [LICENCE](https://github.com/Dalex011/Intraday-Overnight-Returns-Asymmetry-Research/blob/main/LICENSE)

### AI Disclosure
This project was developed with the assistance of AI to accelerate code debugging, data visualization structuring, and documentation structuring. All financial logic, core methodologies, and final validations are entirely my own.

---
Thank you for reading this far. Feedback and corrections are welcome via issues.
Kind regards, Dalex.
