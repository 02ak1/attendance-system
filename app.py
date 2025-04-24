import streamlit as st
import pandas as pd
from main import checker


# タイトルの設定
st.title("勤怠管理アプリ")

# ファイルアップロード機能
work_file = st.file_uploader("科学大の業務報告ファイルをアップロードしてください", type=["xlsx"])

if st.button("確認する"):
    if work_file:
        errors=checker(work_file)
        
        hase_error = len(errors) > 0
        if hase_error:
            st.error("エラーが見つかりました:")
            for error in errors:
                st.error(error)
        else:
            st.success("エラーは見つかりませんでした。")

    else:
        st.warning("両方のファイルをアップロードしてください")


    
    