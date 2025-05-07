import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import os

st.set_page_config(page_title="Bản đồ cảm xúc đô thị", layout="wide")

st.title("🗺️ Bản đồ cảm xúc đô thị")
st.markdown("Gắn cảm xúc của bạn tại một địa điểm trên bản đồ, cùng chia sẻ trải nghiệm với cộng đồng.")

# File dữ liệu
DATA_PATH = "emotion_data.csv"

# Nếu file chưa có thì tạo mới
if not os.path.exists(DATA_PATH):
    df = pd.DataFrame(columns=["lat", "lon", "emotion", "note", "timestamp"])
    df.to_csv(DATA_PATH, index=False)
else:
    df = pd.read_csv(DATA_PATH)

# --- Sidebar nhập liệu ---
st.sidebar.header("📍 Gửi cảm xúc của bạn")
emotion = st.sidebar.selectbox("Cảm xúc", ["😊 Vui", "😢 Buồn", "😨 Sợ", "😠 Tức giận", "😌 Thoải mái"])
note = st.sidebar.text_input("Ghi chú (tùy chọn)")
st.sidebar.markdown("*Bấm vào bản đồ để chọn vị trí.*")

# --- Bản đồ ---
m = folium.Map(location=[10.762622, 106.660172], zoom_start=12)

# Hiển thị các cảm xúc đã có
for _, row in df.iterrows():
    popup_text = f"{row['emotion']} lúc {row['timestamp'][:16]}<br>{row['note']}"
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup_text,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Hiển thị bản đồ tương tác
map_data = st_folium(m, width=700, height=500)
coords = map_data.get("last_clicked")

# Gửi cảm xúc mới
if coords and emotion:
    if st.sidebar.button("📩 Gửi cảm xúc"):
        new_row = {
            "lat": coords["lat"],
            "lon": coords["lng"],
            "emotion": emotion,
            "note": note,
            "timestamp": datetime.datetime.now().isoformat()
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("✅ Đã ghi nhận cảm xúc!")

# --- Hiển thị dữ liệu ---
with st.expander("📊 Dữ liệu cảm xúc cộng đồng"):
    st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
