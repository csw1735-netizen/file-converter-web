from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st


ENCODINGS = ["utf-8-sig", "utf-8", "cp949", "euc-kr", "latin-1"]
DELIMITERS = {
    "자동 감지": None,
    "쉼표 (, )": ",",
    "탭 (Tab)": "\t",
    "세미콜론 (; )": ";",
    "파이프 (| )": "|",
    "공백": r"\s+",
}


def safe_name(name: str, fallback: str = "data") -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", name).strip(" ._")
    return cleaned[:100] or fallback


def detect_encoding(raw: bytes) -> str:
    for encoding in ENCODINGS[:-1]:
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "latin-1"


def detect_delimiter(text: str) -> str:
    sample = text[:10000]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;|").delimiter
    except csv.Error:
        return ","


def read_delimited(raw: bytes, encoding: str, delimiter: str | None) -> pd.DataFrame:
    text = raw.decode(encoding)
    actual_delimiter = delimiter or detect_delimiter(text)
    return pd.read_csv(
        io.StringIO(text),
        sep=actual_delimiter,
        engine="python",
        keep_default_na=False,
    )


def read_excel(raw: bytes) -> dict[str, pd.DataFrame]:
    return pd.read_excel(io.BytesIO(raw), sheet_name=None, dtype=object)


def dataframe_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def workbook_to_zip(sheets: dict[str, pd.DataFrame], stem: str) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for sheet_name, df in sheets.items():
            filename = f"{safe_name(stem)}_{safe_name(sheet_name, 'sheet')}.csv"
            archive.writestr(filename, dataframe_to_csv(df))
    return output.getvalue()


def parse_uploaded_file(uploaded_file, encoding: str, delimiter: str | None):
    raw = uploaded_file.getvalue()
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return read_excel(raw)
    return {safe_name(Path(uploaded_file.name).stem): read_delimited(raw, encoding, delimiter)}


st.set_page_config(page_title="파일 변환 도구", page_icon="🔄", layout="wide")
st.title("파일 변환 도구")
st.caption("Excel·CSV·TXT 파일을 표준 CSV 파일로 변환합니다.")

uploaded_files = st.file_uploader(
    "파일을 이곳에 끌어 놓거나 클릭해서 선택하세요",
    type=["xlsx", "xlsm", "xls", "csv", "txt", "tsv"],
    accept_multiple_files=True,
)

with st.expander("CSV/TXT 읽기 설정", expanded=False):
    encoding_choice = st.selectbox("문자 인코딩", ["자동 감지"] + ENCODINGS)
    delimiter_label = st.selectbox("열 구분자", list(DELIMITERS))

if uploaded_files:
    parsed_files: list[tuple[Any, dict[str, pd.DataFrame]]] = []
    for uploaded_file in uploaded_files:
        raw = uploaded_file.getvalue()
        encoding = detect_encoding(raw) if encoding_choice == "자동 감지" else encoding_choice
        try:
            sheets = parse_uploaded_file(uploaded_file, encoding, DELIMITERS[delimiter_label])
            parsed_files.append((uploaded_file, sheets))
        except Exception as error:
            st.error(f"{uploaded_file.name} 파일을 읽지 못했습니다: {error}")

    for uploaded_file, sheets in parsed_files:
        stem = Path(uploaded_file.name).stem
        st.subheader(uploaded_file.name)
        selected_sheet = st.selectbox(
            "미리 볼 시트",
            list(sheets),
            key=f"preview_{uploaded_file.name}_{uploaded_file.size}",
        )
        df = sheets[selected_sheet]
        st.dataframe(df.head(100), use_container_width=True, height=320)
        st.caption(f"{len(df):,}행 × {len(df.columns):,}열 · 미리보기는 최대 100행")

        if len(sheets) == 1:
            st.download_button(
                "CSV 내려받기",
                dataframe_to_csv(df),
                file_name=f"{safe_name(stem)}.csv",
                mime="text/csv",
                key=f"csv_{uploaded_file.name}_{uploaded_file.size}",
                use_container_width=True,
            )
        else:
            st.download_button(
                "모든 시트를 CSV ZIP으로 내려받기",
                workbook_to_zip(sheets, stem),
                file_name=f"{safe_name(stem)}_csv.zip",
                mime="application/zip",
                key=f"zip_{uploaded_file.name}_{uploaded_file.size}",
                use_container_width=True,
            )

        st.divider()
