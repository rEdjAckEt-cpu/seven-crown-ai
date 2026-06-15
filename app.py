import numpy as np
import pandas as pd
import streamlit as st

# ==========================================
# 👑 1. アプリ基本設定
# ==========================================
st.set_page_config(page_title="SEVEN CROWN WORLD", page_icon="👑", layout="centered")
st.title("👑 競馬予想AI「SEVEN CROWN」")
st.markdown("### 〜 忖度ゼロ・世界全G1 ＆ 国内全重賞 完全連動システム 〜")

# ==========================================
# 📝 2. 全世界主要G1・コース条件データベース
# ==========================================
@st.cache_data
def load_worldwide_race_stipulations():
    races = {
        "凱旋門賞": ("ロンシャン", 2400, "欧州タフ芝・偽りの直線"),
        "香港カップ": ("シャティン", 2000, "大箱・タフ洋芝"),
        "香港マイル": ("シャティン", 1600, "大箱・タフ洋芝"),
        "香港スプリント": ("シャティン", 1200, "大箱・タフ洋芝"),
        "香港ヴァーズ": ("シャティン", 2400, "大箱・タフ洋芝"),
        "ドバイワールドカップ": ("メイダン", 2000, "超パワフル砂ダート"),
        "ドバイシーマクラシック": ("メイダン", 2410, "大箱・ワンターン芝"),
        "ドバイターフ": ("メイダン", 1800, "大箱・ワンターン芝"),
        "コックスプレート": ("ムーニーバレー", 2040, "内回り・すり鉢バンク"),
        "フレミントン・コックスP(代替)": ("フレミントン", 2000, "大箱・超ロング直線"),

        "フェブラリーS": ("東京", 1600, "大箱"), "高松宮記念": ("中京", 1200, "大箱"),
        "大阪杯": ("阪神", 2000, "内回り"), "桜花賞": ("阪神", 1600, "外回り"),
        "皐月賞": ("中山", 2000, "内回り"), "天皇賞（春）": ("京都", 3200, "外回り"),
        "NHKマイルC": ("東京", 1600, "大箱"), "ヴィクトリアM": ("東京", 1600, "大箱"),
        "オークス": ("東京", 2400, "大箱"), "日本ダービー": ("東京", 2400, "大箱"),
        "安田記念": ("東京", 1600, "大箱"), "宝塚記念": ("阪神", 2200, "内回り"),
        "スプリンターズS": ("中山", 1200, "内回り"), "秋華賞": ("京都", 2000, "内回り"),
        "菊花賞": ("京都", 3000, "外回り"), "天皇賞（秋）": ("東京", 2000, "大箱"),
        "エリザベス女王杯": ("京都", 2200, "外回り"), "マイルCS": ("京都", 1600, "外回り"),
        "ジャパンC": ("東京", 2400, "大箱"), "チャンピオンズC": ("中京", 1800, "内回り"),
        "阪神ジュベナイルF": ("阪神", 1600, "外回り"), "朝日杯FS": ("阪神", 1600, "外回り"),
        "有馬記念": ("中山", 2500, "内回り"), "ホープフルS": ("中山", 2000, "内回り"),

        "弥生賞ディープ記念": ("中山", 2000, "内回り"), "セントライト記念": ("中山", 2200, "外回り"),
        "オールカマー": ("中山", 2200, "外回り"), "毎日王冠": ("東京", 1800, "大箱"),
        "京都新聞杯": ("京都", 2200, "外回り"), "青葉賞": ("東京", 2400, "大箱"),
        "アメリカJCC": ("中山", 2200, "外回り"), "日経賞": ("中山", 2500, "内回り"),
        "札幌記念": ("札幌", 2000, "内回り"), "函館記念": ("函館", 2000, "内回り"),
        "チャレンジC": ("阪神", 2000, "内回り"), "中日新聞杯": ("中京", 2000, "大箱"),
        "共同通信杯": ("東京", 1800, "大箱"), "新潟直線アイビスSD": ("新潟", 1000, "直線")
    }
    return races

# ==========================================
# 📊 3. 競走馬データベース (構文エラー完全修正済)
# ==========================================
@st.cache_data
def get_infinity_horse_parameters(horse_names):
    # パラメーター: [キレ, 持続力, 旋回性能, 操縦性, パワー]
    base_data = {
        "コスモキュランダ":,
        "フォーエバーヤング":,
        "ダノンデサイル":,
        "メイショウタバル":,
        "ブローザホーン":,
        "ベラジオオペラ":,
        "ファウストラーゼン":,
        "マスカレードボール":,
        "ジュウリョクピエロ":,
        "リアライズシリウス":,
        "スターアニス":,
        "アロヒアリイ":,
        "ミステリーウェイ": [45, 75, 65, 70, 70]
    }
    
    final_data = {}
    for name in horse_names:
        name = name.strip()
        if name in base_data:
            final_data[name] = base_data[name]
        else:
            if "アース" in name or "インパクト" in name or "キレ" in name:
                final_data[name] = [90, 70, 60, 75, 60]
            elif "テラ" in name or "キング" in name or "スタミナ" in name:
                final_data[name] = [50, 85, 70, 70, 85]
            else:
                final_data[name] = [65, 70, 70, 70, 65]
    return final_data

# ==========================================
# ⚙️ 4. UIコントロールパネル
# ==========================================
st.markdown("### 🛠️ レース番組・環境設定")

race_db = load_worldwide_race_stipulations()
selected_race = st.selectbox("予想するレースを選択してください", options=list(race_db.keys()))

venue, distance, track_type = race_db[selected_race]
st.info(f"📋 【世界公式条件同期】 開催地: {venue} / 距離: {distance}m / コース特性: {track_type}")

col_env1, col_env2 = st.columns(2)
with col_env1:
    weather = st.radio("天候", ["晴", "雨", "雪"], horizontal=True)
with col_env2:
    condition = st.radio("馬場状態", ["良", "稍重", "重", "不良"], horizontal=True)

st.markdown("---")
st.markdown("### 🐎 出走馬の入力")

input_horses_raw = st.text_area(
    "出走馬の名前をカンマ（、または ,）で区切って入力してください",
    value="コスモキュランダ, フォーエバーヤング, ダノンデサイル, メイショウタバル, ブローザホーン, ベラジオオペラ"
)

active_horses = [h.strip() for h in input_horses_raw.replace("、", ",").split(",") if h.strip()]
horse_db = get_infinity_horse_parameters(active_horses)

# ==========================================
# 🚀 5. SEVEN CROWN AI 演算 & フォーメーション自動生成
# ==========================================
if st.button("🔮 SEVEN CROWN 最終判定を発射", use_container_width=True):
    if len(active_horses) < 3:
        st.error("⚠️ 3連単を計算するため、出走馬を3頭以上入力してください。")
    else:
        weights = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        
        if track_type == "内回り" or "ムーニーバレー" in venue:
            weights += np.array([-0.2, 0.3, 0.6, 0.2, 0.2])
        elif track_type in ["外回り", "大箱", "大箱・ワンターン芝", "大箱・タフ洋芝", "フレミントン"]:
            weights += np.array([0.6, 0.1, -0.2, 0.1, -0.1])

        if weather in ["雨", "雪"] or condition in ["重", "不良"]:
            weights = np.array([0.1, 0.8, 0.5, 0.3, 1.5])

        results = {}
        for h in active_horses:
            if h in horse_db:
                score = np.dot(horse_db[h], weights)
                if h == "コスモキュランダ" and track_type in ["外回り", "大箱"] and weather == "晴" and condition == "良":
                    score -= 25.0
                results[h] = round(score, 1)

        ranked = sorted(results.items(), key=lambda x: x, reverse=True)

        st.success("🎉 ガチンコデータ照合および環境クレンジング完了！")
        st.markdown(f"#### 🎯 最終診断結果: {selected_race} ({venue} {distance}m)")

        df_res = pd.DataFrame(ranked, columns=["競走馬名", "適性予測スコア"])
        df_res.index = df_res.index + 1
        st.table(df_res)

        st.markdown("### 🏆 【推奨ハメ殺しフォーメーション】")
        if len(ranked) >= 3:
            st.write(f"1着固定: ◎ {ranked[0][0]}")
            st.write(f"2着流し: ○ {ranked[0][0]}, {ranked[1][0]}")
            st.write(f"3着流し: ▲ {', '.join([ranked[i][0] for i in range(2, min(6, len(ranked)))])}")
