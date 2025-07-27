from flask import Flask, render_template, request
import pandas as pd
import re

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
def load_data(search_terms=None):
    # อ่านข้อมูลจากหลายไฟล์ CSV
    df1 = pd.read_csv("วิศวกรรมโยธา.csv")
    df2 = pd.read_csv("วิศวกรรมคอมพิวเตอร์.csv")
    df3 = pd.read_csv("วิศวกรรมเคมี.csv")

    # รวมข้อมูลทั้งหมด
    df = pd.concat([df1, df2, df3], ignore_index=True)

    # คำนวณราคา
    df["ราคา (บาท)"] = df["ค่าใช้จ่าย (ต่อภาค)"].apply(extract_numeric_baht)
    df["ราคา (บาท, แสดงผล)"] = df["ราคา (บาท)"].apply(
        lambda x: f"{x:,.0f} บาท" if pd.notnull(x) and float(x) > 0 else "ไม่พบ"
    )

    # สร้างชื่อย่อกรณีชื่อมหาวิทยาลัยยาวเกิน
    df["ชื่อย่อ"] = df["มหาวิทยาลัย"].apply(lambda x: x if len(x) <= 25 else x[:22] + "...")

    # ถ้ามีการค้นหาตามสาขา (filter)
    if search_terms:
        df = df[df['หลักสูตร'].str.contains('|'.join(search_terms), case=False, na=False)]

    return df

@app.route('/', methods=['GET', 'POST'])
def index():
    # รับค่าจาก form ค้นหาหลักสูตร (default เป็น 'วิศวกรรมคอมพิวเตอร์')
    search_terms = request.form.getlist('search_terms') or ['วิศวกรรมคอมพิวเตอร์']

    # โหลดข้อมูลที่กรองตามสาขาที่ค้นหา
    df = load_data(search_terms)

    # จัดอันดับแพงสุด 5 อันดับ (ไว้กรองฝั่ง JS)
    df_sorted = df.sort_values("ราคา (บาท)", ascending=False)

    # ส่งข้อมูลเป็น list of dicts
    data_records = df_sorted.to_dict(orient="records")

    return render_template("dashboard_2.html", data=data_records, search_terms=search_terms)

if __name__ == '__main__':
    app.run(debug=True)
