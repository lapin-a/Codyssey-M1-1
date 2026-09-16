import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv('aapl_daily_2024.csv', parse_dates=['Date']).sort_values('Date').reset_index(drop=True)

# 관찰(근거) 1: 이동평균 (20일)
df['MA20'] = df['Close'].rolling(window=20).mean()

# 관찰(근거) 2: 일별 수익률 및 변동성(20일 롤링 표준편차)
df['DailyReturn'] = df['Close'].pct_change()
df['Volatility20'] = df['DailyReturn'].rolling(window=20).std()

# 가장 변동성 컸던 구간 top5
top_vol = df.nlargest(5, 'Volatility20')[['Date', 'Close', 'Volatility20']]
print('=== 변동성 상위 5개 구간(20일 기준) ===')
print(top_vol.to_string(index=False))

print()
print('=== 연간 요약 ===')
print('연초(1/2) 종가:', round(df.iloc[0]['Close'], 2))
print('연말(12/31) 종가:', round(df.iloc[-1]['Close'], 2))
print('연간 변화율(%):', round((df.iloc[-1]['Close'] / df.iloc[0]['Close'] - 1) * 100, 1))
print('최고가:', df['Close'].max(), '(', df.loc[df['Close'].idxmax(), 'Date'].date(), ')')
print('최저가:', df['Close'].min(), '(', df.loc[df['Close'].idxmin(), 'Date'].date(), ')')

# 시각화 1: 종가 + 이동평균 (한글 폰트 미설치 환경이라 라벨은 영문으로)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['Date'], df['Close'], label='Close Price', linewidth=1)
ax.plot(df['Date'], df['MA20'], label='20-day MA', linewidth=1.5)
ax.set_title('AAPL 2024 Daily Close Price & 20-day Moving Average')
ax.set_xlabel('Date')
ax.set_ylabel('Price (USD)')
ax.legend()
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig('chart1_price_ma.png', dpi=120)

# 시각화 2: 변동성
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(df['Date'], df['Volatility20'], color='darkred', linewidth=1)
ax2.set_title('AAPL 2024 20-day Rolling Volatility (std of daily returns)')
ax2.set_xlabel('Date')
ax2.set_ylabel('Volatility')
fig2.autofmt_xdate()
fig2.tight_layout()
fig2.savefig('chart2_volatility.png', dpi=120)

df.to_csv('aapl_daily_2024_processed.csv', index=False)
print()
print('저장 완료: chart1_price_ma.png, chart2_volatility.png, aapl_daily_2024_processed.csv')
