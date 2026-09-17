# AAPL 2024 시계열 데이터 분석

애플(AAPL) 2024년 일별 종가(252 거래일)를 이동평균·변동성·시계열 분해로 분석한 프로젝트입니다.

전체 분석 내용(질문/데이터설명/인사이트/결론/한계점/AI 사용 로그)은 **[REPORT.md](./REPORT.md)** 를 확인하세요.

## 폴더 구성

| 파일 | 설명 |
|---|---|
| `REPORT.md` | 최종 분석 리포트 (필수 항목 + 보너스 2건 포함) |
| `analyze.py` | 이동평균·변동성 계산, chart1·chart2 생성 |
| `decompose.py` | 시계열 분해(보너스), chart3 생성 |
| `dashboard.html` | 인터랙티브 대시보드(보너스, 서버 없이 브라우저로 바로 실행) |
| `aapl_daily_2024.csv` | 원본 데이터(Date, Close, High, Low, Open, Volume) |
| `aapl_daily_2024_processed.csv` | MA20·DailyReturn·Volatility20 컬럼이 추가된 가공 데이터 |
| `chart1_price_ma.png` / `chart2_volatility.png` / `chart3_decomposition.png` | 시각화 결과물 |
| `requirements.txt` | 의존 라이브러리 목록 |

## 빠른 실행

```bash
pip install -r requirements.txt
python analyze.py       # chart1, chart2, 가공 CSV 생성
python decompose.py     # chart3(시계열 분해) 생성
```

`dashboard.html`은 별도 설치 없이 브라우저로 열면 바로 동작합니다. 배포된 버전은 REPORT.md 11번 섹션 링크 참고.

## 데이터 출처

공개 시장 데이터 2차 가공 자료 (HuggingFace 게시 데이터셋). 1차 거래소 원문이 아님을 REPORT.md에 명시했습니다. 투자 조언이 아닌 교육용 분석 자료입니다.