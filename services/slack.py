import streamlit as st
from slack_sdk import WebClient
import tempfile


def send_slack_message(message: str, xlsx_data: str | None = None) -> dict | None:
    """Slackにテキストメッセージを投稿し、xlsxを添付（files.upload 対応済み）"""
    TOKEN = st.secrets["slack"]["bot_token"]
    CHANNEL_ID= st.secrets["slack"]["channel_id"]
    client = WebClient(token=TOKEN)

    try:
        # メッセージ送信
        response = client.chat_postMessage(
            channel=CHANNEL_ID,
            text=message,
        )
        thread_ts = response["ts"]
        # print(f"Message sent to channel {CHANNEL_ID} with thread timestamp: {thread_ts}")

        # xlsx添付（必要に応じて）
        if xlsx_data:
            filename = "テスト.xlsx"
            title = "テスト"
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx", mode="wb") as tmp_file:
                tmp_file.write(xlsx_data)
                tmp_file_path = tmp_file.name

            with open(tmp_file_path, "rb") as file_content:
                upload_response = client.files_upload_v2(
                    channel=CHANNEL_ID,
                    file=file_content,
                    filename=filename,
                    thread_ts=thread_ts,
                    title=title,
                    initial_comment="📎 XLSXを添付します"
                )

        return response

    except Exception as e:
        st.error(f"Slack送信エラー: {e}")
        return None