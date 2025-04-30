import os
import json
import streamlit as st
import pandas as pd

from utils.check_integration import checker
from services.slack import send_slack_message

# ===== 定数 =====
TITLE = "勤怠管理アプリ"
UPLOAD_LABEL = "科学大の業務報告ファイルをアップロードしてください"
ALLOWED_EXTENSIONS = ["xlsx"]
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "location_workreport.json")

# ===== ヘルパー関数 =====
@st.cache_data
def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_excel_sheet(file, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(file, sheet_name=sheet_name, index_col=0)

def check_and_display_errors(df_report, df_timetable):
    errors = checker(df_report, df_timetable)
    if errors:
        st.error("エラーが見つかりました:")
        for error in errors:
            st.error(error)
        return False
    else:
        st.success("エラーは見つかりませんでした。")
        return True

# ===== Streamlit UI =====
st.title(TITLE)

work_file = st.file_uploader(UPLOAD_LABEL, type=ALLOWED_EXTENSIONS)

# 設定ファイル読み込みと保存
config = load_config(CONFIG_PATH)
st.session_state["config"] = config

REPORT = config["sheet_info"]["REPORT"]
TIMETABLE = config["sheet_info"]["TIMETABLE"]

if work_file:
    df_report = load_excel_sheet(work_file, REPORT)
    df_timetable = load_excel_sheet(work_file, TIMETABLE)
else:
    st.warning("業務報告ファイルをアップロードしてください")

if "check_passed" not in st.session_state:
    st.session_state["check_passed"] = False


if st.button("確認する") and work_file:
    passed = check_and_display_errors(df_report, df_timetable)
    st.session_state["check_passed"] = passed

if st.session_state["check_passed"]:
    if st.button("Slackに送信", key="slack", icon=":material/send:"):
        with st.spinner("Slackに送信中です..."):
            response = send_slack_message(f"Excel処理結果をお送りします", xlsx_data=work_file.read())

        if not response:
            st.error("Slackへの送信に失敗しました", icon="🚫")
        else:
            st.success("Slackに送信しました", icon="✅")
            st.balloons()

