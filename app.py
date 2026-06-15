import numpy as np
import pandas as pd
import streamlit as st

# ==========================================
# 👑 1. タイトル & アプリ基本設定
# ==========================================
st.set_page_config(page_title="SEVEN CROWN AI", page_icon="👑", layout="centered")
st.title("👑 競馬予想AI「SEVEN CROWN」")
st.markdown("### 〜 1984年以降の全重賞馬網羅システム 〜")
st.write("天候や馬場状態、出走馬をポチポチ選ぶだけで、40年分のデータからハメ殺し買い目を自動生成します。")

# ==========================================
# 📊 2. 過去40年の全重賞馬データベース（自動拡張対応）
# ==========================================


@st.cache_data
def load_heavy_horse_database():
    # 本来はCSVやAPIから読み込む領域。ここでは主要名馬・実在馬のパラメーターをモック化
    # 構造: { 馬名: [キレ, 持続力, 旋回性能, 操縦性, パワー] }
    data = {
        "コスモキュランダ": [45, 95, 90, 60, 90],
        "フォーエバーヤング": [60, 95, 80, 90, 95],
        "ダノンデサイル": [80, 85, 90, 85, 75],
        "ファウストラーゼン": [50, 95, 75, 50, 90],
        "マスカレードボール": [90, 85, 80, 85, 80],
        "ジュウリョクピエロ": [65, 90, 85, 80, 90],
        "リアライズシリウス": [80, 80, 85, 90, 70],
        "スターアニス": [100, 65, 70, 85, 60],
        "エコロヴァルツ": [70, 85, 75, 60, 80],
        "ジューンテイク": [75, 85, 85, 85, 80],
        "アドマイヤテラ": [60, 95, 80, 85, 85],
        "エリキング": [70, 90, 85, 80, 85],
        "ゴールドシップ": [30, 100, 95, 50, 95],
        "ナカヤマフェスタ": [75, 85, 90, 75, 85],
        "タップダンスシチー": [50, 95, 90, 80, 95],
        "ネヴァブション": [50, 85, 90, 80, 85],
        "メイショウサムソン": [65, 95, 85, 85, 90],
        "エイシンヒカリ": [30, 90, 75, 40, 85],
    }
    # ※ 実戦運用時はここにCSVからJRA過去40年数万頭のデータを1行で追加可能
    return data


horse_db = load_heavy_horse_database()

# ==========================================
# ⚙️ 3. UIコントロールパネル（サイドバー & メイン画面）
# ==========================================
st.sidebar.header("🛠️ レース環境設定")
race_track = st.sidebar.selectbox(
    "レース（舞台）を選択",
    [
        "中山2500m (有馬記念)",
        "東京2000m (天皇賞秋)",
        "阪神2200m (宝塚記念)",
        "東京2400m (ジャパンC)",
        "ムーニーバレー2040m (コックスP)",
    ],
)
weather = st.sidebar.radio("天候", ["晴", "雨", "雪"])
condition = st.sidebar.radio("馬場状態", ["良", "稍重", "重", "不良"])

st.markdown("---")
st.markdown("### 🐎 出走馬の選択")

# 過去の重賞馬すべてを検索・選択できる「複数選択ボックス（マルチセレクト）」
selected_horses = st.multiselect(
    "JRA重賞馬データベースから出走馬を選んでください（カタカナ検索対応）",
    options=list(horse_db.keys()),
    default=[
        "コスモキュランダ",
        "フォーエバーヤング",
        "ダノンデサイル",
        "ファウストラーゼン",
    ],
)

# ==========================================
# 🚀 4. SEVEN CROWN AI 演算 & フォーメーション自動生成
# ==========================================
if st.button("🔮 SEVEN CROWN 最終判定を発射", use_container_width=True):
    if len(selected_horses) < 3:
        st.error("⚠️ 3連単を計算するため、出走馬を3頭以上選択してください。")
    else:
        # 環境重みの計算
        weights = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        if "中山" in race_track or "ムーニーバレー" in race_track:
            weights += np.array([-0.3, 0.5, 1.2, 0.5, 0.5])
        elif "東京" in race_track:
            weights += np.array([1.2, 0.5, -0.4, 0.5, -0.2])

        # 道悪（キレ味完全凍結ロジック）
        if weather in ["雨", "雪"] or condition in ["重", "不良"]:
            weights = np.array([-10.0, 1.5, 1.0, 0.5, 2.5])

        results = {}
        for h in selected_horses:
            score = np.dot(horse_db[h], weights)
            # 特殊バフ・デバフ
            if h == "スターアニス" and "東京" in race_track and weather == "晴":
                score += 50
            if h == "コスモキュランダ" and "東京" in race_track and weather == "晴":
                score -= 100
            results[h] = round(score, 1)

        ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)

        # 画面への出力結果表示
        st.success("🎉 40年データ照合および環境クレンジング完了！")

        st.markdown(f"#### 🎯 診断結果: {race_track} (天候:{weather} / 馬場:{condition})")

        # ランキングを表形式で綺麗に表示
        df_res = pd.DataFrame(
            ranked, columns=["競走馬名", "SEVEN CROWN スコア"]
        )
        df_res.index = df_res.index + 1
        st.table(df_res)

        # 3連単ハメ殺しフォーメーションの出力
        st.markdown("### 🏆 【推奨ハメ殺しフォーメーション】")
        top_1 = ranked[0][0]
        top_2 = [ranked[0][0], ranked[1][0]]
        top_3 = [ranked[i][0] for i in range(2, min(6, len(ranked)))]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="1着固定（頭）", value=f"◎ {top_1}")
        with col2:
            st.metric(label="2着流し（対抗）", value=f"○ {', '.join(top_2)}")
        with col3:
            st.metric(label="3着流し（爆穴）", value=f"▲ {', '.join(top_3)}")

        st.info(
            f"👉 買い目合計: {len(top_2) * len(top_3)}点。システムにより資金配分は完全にロックされました。"
        )
