"""
corp_code_matcher.py

DART 기업개황목록(xlsx)과 OpenDART corpCode.xml을 매칭해서
corp_code(공시 API 호출용 고유번호)를 붙이는 스크립트.

AI/LLM을 전혀 사용하지 않는 규칙 기반(rule-based) 매칭입니다.
사용 라이브러리: pandas, openpyxl, xml.etree.ElementTree (표준 라이브러리)

매칭 우선순위:
  1) 종목코드(stock_code) 일치 — 상장사에 한해 가장 신뢰도 높은 매칭
  2) 공시회사명(corp_name) 일치 — 나머지 비상장/코넥스 법인 등
     - 동명이인(corp_name 중복)이 있으면 modify_date가 가장 최신인 항목을 채택하고
       'ambiguous' 컬럼에 True로 표시

사용법:
  python corp_code_matcher.py <기업개황목록.xlsx> <CORPCODE.xml> <출력파일.xlsx>
"""

import sys
import xml.etree.ElementTree as ET
import pandas as pd


def load_corpcode(xml_path: str) -> pd.DataFrame:
    """CORPCODE.xml을 파싱해서 DataFrame으로 반환한다."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    records = []
    for corp in root.findall("list"):
        records.append({
            "corp_code": corp.findtext("corp_code"),
            "corp_name": corp.findtext("corp_name"),
            "corp_eng_name": corp.findtext("corp_eng_name"),
            "stock_code": (corp.findtext("stock_code") or "").strip(),
            "modify_date": corp.findtext("modify_date"),
        })
    return pd.DataFrame(records)


def load_business_list(xlsx_path: str) -> pd.DataFrame:
    """기업개황목록.xlsx을 읽는다. 식별번호 컬럼은 반드시 문자열로 읽어야
    앞자리 0이 잘리거나 '1234.0' 같은 부동소수점 표기가 생기는 걸 막는다."""
    dtype_map = {"법인등록번호": str, "사업자등록번호": str, "종목코드": str}
    return pd.read_excel(xlsx_path, dtype=dtype_map)


def match_corp_code(biz_df: pd.DataFrame, corp_df: pd.DataFrame) -> pd.DataFrame:
    biz_df = biz_df.copy()
    biz_df["종목코드_clean"] = biz_df["종목코드"].astype(str).str.strip()
    biz_df.loc[biz_df["종목코드_clean"].isin(["nan", ""]), "종목코드_clean"] = ""

    biz_df["corp_code"] = pd.NA
    biz_df["match_method"] = pd.NA

    # 1단계: 종목코드 매칭 (상장사, 종목코드는 유일값이라 가장 정확)
    corp_by_stock = (
        corp_df[corp_df["stock_code"] != ""]
        .drop_duplicates("stock_code", keep="last")
    )
    stock_map = dict(zip(corp_by_stock["stock_code"], corp_by_stock["corp_code"]))

    stock_matched = biz_df["종목코드_clean"].map(stock_map)
    biz_df.loc[stock_matched.notna(), "corp_code"] = stock_matched
    biz_df.loc[stock_matched.notna(), "match_method"] = "종목코드"

    # 2단계: 남은 행은 공시회사명 매칭
    remaining = biz_df["corp_code"].isna()

    # 동명이인(corp_name 중복)이면 최신 modify_date 채택
    corp_by_name = corp_df.sort_values("modify_date").drop_duplicates(
        "corp_name", keep="last"
    )
    name_map = dict(zip(corp_by_name["corp_name"], corp_by_name["corp_code"]))
    dup_names = set(corp_df[corp_df.duplicated("corp_name", keep=False)]["corp_name"])

    name_matched = biz_df.loc[remaining, "공시회사명"].map(name_map)
    biz_df.loc[remaining, "corp_code"] = name_matched
    biz_df.loc[remaining & biz_df["corp_code"].notna(), "match_method"] = "공시회사명"

    # 동명이인으로 인해 불확실한 매칭 표시
    biz_df["ambiguous"] = (
        biz_df["공시회사명"].isin(dup_names) & (biz_df["match_method"] == "공시회사명")
    )

    return biz_df.drop(columns=["종목코드_clean"])


def main():
    if len(sys.argv) != 4:
        print("사용법: python corp_code_matcher.py <기업개황목록.xlsx> <CORPCODE.xml> <출력파일.xlsx>")
        sys.exit(1)

    biz_path, xml_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    corp_df = load_corpcode(xml_path)
    biz_df = load_business_list(biz_path)
    result = match_corp_code(biz_df, corp_df)

    total = len(result)
    matched = result["corp_code"].notna().sum()
    unmatched = total - matched
    ambiguous = result["ambiguous"].sum()

    print(f"전체: {total}")
    print(f"매칭 성공: {matched} ({matched / total * 100:.2f}%)")
    print(f"매칭 실패: {unmatched}")
    print(f"동명이인으로 불확실한 매칭: {ambiguous}")

    result.to_excel(out_path, index=False)
    print(f"저장 완료: {out_path}")


if __name__ == "__main__":
    main()