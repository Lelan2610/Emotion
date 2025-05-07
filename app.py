coords = map_data.get("last_clicked")

if coords and emotion:
    if st.sidebar.button("📩 Gửi cảm xúc"):
        local_time = convert_to_user_timezone(coords["lat"], coords["lng"])
        
        new_row = {
            "lat": coords["lat"],
            "lon": coords["lng"],
            "emotion": emotion,
            "note": note,
            "user": user_name,
            "timestamp": local_time
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("✅ Đã ghi nhận cảm xúc!")
