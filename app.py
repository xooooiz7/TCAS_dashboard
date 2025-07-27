from flask import Flask, render_template
import pandas as pd
import re
import os

app = Flask(__name__)

# ==== ดึงเลขจากข้อความ ====
def extract_numeric_baht(text):
    try:
        matches = re.findall(r'ค่าใช้จ่าย:\s*([\d,]+)\s*บาท', str(text))
        if matches:
            numbers = [int(m.replace(',', '')) for m in matches]
            return sum(numbers) // len(numbers)
    except:
        pass
    return None

# ==== โหลดและเตรียมข้อมูล ====
def load_data():
    df = pd.read_csv("data/data_clean_typhoon.csv")

    # คำนวณราคา
    df["ราคา (บาท)"] = df["ค่าใช้จ่าย (ต่อภาค)"].apply(extract_numeric_baht)
    df["ราคา (บาท, แสดงผล)"] = df["ราคา (บาท)"].apply(
        lambda x: f"{x:,.0f} บาท" if pd.notnull(x) and float(x) > 0 else "ไม่พบ"
    )

    # สร้างชื่อย่อกรณีชื่อมหาวิทยาลัยยาวเกิน
    df["ชื่อย่อ"] = df["มหาวิทยาลัย"].apply(lambda x: x if len(x) <= 25 else x[:22] + "...")
    return df

@app.route('/')
def index():
    df = load_data()

    # จัดอันดับแพงสุด 5 อันดับ (ไว้กรองฝั่ง JS)
    df_sorted = df.sort_values("ราคา (บาท)", ascending=False)

    # ส่งข้อมูลเป็น list of dicts
    data_records = df_sorted.to_dict(orient="records")

    return render_template("dashboard.html", data=data_records)

if __name__ == '__main__':
    app.run(debug=True)
