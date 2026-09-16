import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

df = pd.read_csv('aapl_daily_2024.csv', parse_dates=['Date']).sort_values('Date').reset_index(drop=True)
df = df.set_index('Date')

# 가정: 거래일 기준 1주(5거래일) 주기로 분해를 시도한다.
# 한계: 주가는 계절과 물리적 인과관계가 뚜렷한 데이터(기온, 판매량 등)와 달리
# 내재적 계절성이 약하다. 여기서는 "혹시 요일 단위 패턴이 있는지" 탐색적으로 살펴보는 용도로만 사용한다.
period = 5
result = seasonal_decompose(df['Close'], model='additive', period=period, extrapolate_trend='freq')

fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
axes[0].plot(result.observed); axes[0].set_ylabel('Observed')
axes[1].plot(result.trend); axes[1].set_ylabel('Trend')
axes[2].plot(result.seasonal); axes[2].set_ylabel('Seasonal (5-day)')
axes[3].plot(result.resid); axes[3].set_ylabel('Residual')
axes[0].set_title('AAPL 2024 Close Price - Additive Decomposition (period=5 trading days)')
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig('chart3_decomposition.png', dpi=120)

print('=== 분해 결과 요약 ===')
print('계절성분(5일 주기) 진폭 범위:', round(result.seasonal.min(), 3), '~', round(result.seasonal.max(), 3))
print('잔차(residual) 표준편차:', round(result.resid.std(), 3))
print('잔차 표준편차 대비 원계열 표준편차 비율:', round(result.resid.std() / df["Close"].std(), 4))
print()
print('저장 완료: chart3_decomposition.png')
