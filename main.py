import streamlit as st
import pandas as pd
import requests
import xmltodict

df_illustrators = pd.read_csv("illustrators.csv")
df_illustrators = df_illustrators.rename(columns={"Unnamed: 0":"user_id"})
df_illustrators["exp_scaled"] = (df_illustrators["expectation"] - df_illustrators["expectation"].min()) / (df_illustrators["expectation"].max() - df_illustrators["expectation"].min())

df_tag = pd.read_csv("tags.csv")
df_tag = df_tag.rename(columns={"Unnamed: 0": "tag"})
df_tag["exp_scaled"] = (df_tag["expectation"] - df_tag["expectation"].min()) / (df_tag["expectation"].max() - df_tag["expectation"].min())

user_input = st.text_input("イラストIDを入力してください:", "")
if user_input:
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "cookie": "target=illust; nicosid=1732339878.931490987; user_session=user_session_119191665_06e32f00c2fa32b162c36f090cf477bafa9f791f213788e2a1d1323d7c0f07ed; user_session_secure=MTE5MTkxNjY1OlJxaW9UaXU5Nmo4QTg1TVRuUFRIUC54QUxSaEwuWlQyUlFzekxpNTRtMnU; common-header-oshirasebox-new-allival=false",
        "priority": "u=0, i",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    illust_id = int(user_input)

    # タグデータ取得
    response = requests.get(f"https://seiga.nicovideo.jp/ajax/illust/tag/list?id={illust_id}", headers=headers)
    response = response.json()
    tags = list(map(lambda x: x["name"], response["tag_list"]))

    # イラストデータ取得
    response = requests.get(f"https://seiga.nicovideo.jp/api/illust/info?id={illust_id}", headers=headers)
    data = xmltodict.parse(response.text)["response"]["image"]
    image_title = data["title"]
    user_id = int(data["user_id"])
    thumbnail_url = data["thumbnail_url"]

    st.subheader(image_title)
    st.image(thumbnail_url)

    df_user = df_illustrators[df_illustrators["user_id"] == user_id]

    if len(df_user) == 0:
        st.info("このユーザーはデータに存在しませんでした")
    else:
        row = df_user.iloc[0]
        col1, col2, col3 = st.columns([2, 4, 1])
        col1.markdown("**ユーザーの強さ**")
        col2.progress(row["exp_scaled"])
        col3.write(int(row["exp_scaled"]*100))

    # タグのステータス表示
    for i, row in df_tag[df_tag["tag"].isin(tags)].iterrows():
        col1, col2, col3 = st.columns([2, 4, 1])
        col1.write(row["tag"])
        col2.progress(row["exp_scaled"])
        col3.write(int(row["exp_scaled"]*100))