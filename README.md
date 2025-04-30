# 📇 勤務報告書チェッカー

このアプリは、勤務報告書のエラーチェックをして、チェックに合格したファイルを Slack に送信することができる **Streamlit アプリケーション** です。

---



## 🔐 秘密情報の設定

次の内容を `~/.streamlit/secrets.toml` に記述してください：

```toml
[slack]
bot_token = "xoxb-xxxxxxxxxxxxxxxx"
channel_id = "CXXXXXXXX"
```

---

## ▶️ アプリの起動方法

以下のコマンドでツールのインストールとアプリの実行を行います：

```bash
mise install        # mise.toml に記載されたツール (uv) をインストール
mise run init       # クレデンシャルを格納するフォルダが存在しない場合は作成し、uvを用いてパッケージの同期を行う
mise run deploy     # uv 経由で Streamlit アプリを実行
```

---

## ⚡ mise のインストール方法

参考：[Getting Started](https://mise.jdx.dev/getting-started.html)

### Homebrew を使って mise をインストールするには：

```bash
brew install mise
```

### zsh（または他のシェル）にパスを通す：

```bash
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
```

---