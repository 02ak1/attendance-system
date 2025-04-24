import streamlit as st
import pandas as pd
from main import checker
import json

# タイトルの設定
st.title("勤怠管理アプリ")

# ファイルアップロード機能
work_file = st.file_uploader("科学大の業務報告ファイルをアップロードしてください", type=["xlsx"])
# JSONファイルの読み込み
with open("location_workreport.json", encoding="utf-8") as f:
    config = json.load(f)

REPORT     = config["sheet_info"]["REPORT"]
TIMETABLE  = config["sheet_info"]["TIMETABLE"]

if work_file:
    # Excelファイルの読み込み
    df_report    = pd.read_excel(work_file, sheet_name=REPORT,    index_col=0)
    df_timetable = pd.read_excel(work_file, sheet_name=TIMETABLE, index_col=0)
    st.write(df_timetable)
else:
    st.warning("業務報告ファイルをアップロードしてください")


if st.button("確認する"):
    if work_file:
        errors=checker(df_report, df_timetable)
        
        hase_error = len(errors) > 0
        if hase_error:
            st.error("エラーが見つかりました:")
            for error in errors:
                st.error(error)
        else:
            st.success("エラーは見つかりませんでした。")

    else:
        st.warning("両方のファイルをアップロードしてください")


    
    