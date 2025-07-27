# TCAS Dashboard (Flask + Pandas + Typhoon AI)

เว็บแอปสำหรับวิเคราะห์และแสดง **ค่าใช้จ่ายต่อภาคการศึกษา** ของหลักสูตรวิศวกรรมคอมพิวเตอร์จากมหาวิทยาลัยทั่วไทย  
ข้อมูลมาจาก [MyTCAS API](https://mytcas.com) วิเคราะห์ข้อความภาษาไทยด้วย LLM (Typhoon) และแสดงผลผ่าน Dashboard สวย ๆ ด้วย Flask

---

## ตัวอย่างหน้าจอ Dashboard

> แสดงข้อมูลแบบกราฟและตาราง พร้อมจัดอันดับตามค่าใช้จ่าย

![ตัวอย่างหน้าจอ Dashboard](templates/template.jpeg)
![ตัวอย่างหน้าจอ Dashboard](templates/template2.jpeg)

---

## ใน repo นี้จะมีการลองกรองข้อมูลทั้ง 2 แบบ ทั้งแบบ regex และ llm แต่แบบที่ใช้นำไปแสดง dashboard คือ จาก llm 

## โครงสร้างไฟล์

| ไฟล์ / โฟลเดอร์ | หน้าที่ |
|------------------|----------|
| `app.py` | Flask app สำหรับแสดง Dashboard |
| `data/` | รวมไฟล์ `.csv` และ `.xlsx` ที่ clean แล้วด้วย regex และ Typhoon |
| `scripts/` | รวม notebook และ python script สำหรับ scraping/cleaning |
| `scraping_typhoon.py` | สคริปต์หลักสำหรับดึงข้อมูลจาก API และวิเคราะห์ข้อความด้วย Typhoon |
| `scrap_regex.ipynb` | วิเคราะห์ข้อความด้วย regex-only (แบบไม่ใช้ LLM) |
| `templates/` | HTML template (`dashboard.html`, template images ฯลฯ) |
| `experimental/` | **โฟลเดอร์สำหรับทดลองกรองสาขาอื่น ๆ ในวิศวกรรม** เช่น วิศวกรรมไฟฟ้า, โยธา ฯลฯ ด้วย Typhoon (ใช้ logic เดียวกับคอมพิวเตอร์) |
| `.env` | เก็บ `TYPHOON_API_KEY` (ไม่ push ขึ้น repo) |
| `.env.example` | ตัวอย่างไฟล์ `.env` สำหรับตั้งค่า |
| `.gitignore` | รายการไฟล์ที่ไม่ต้อง track เช่น `.env`, `.DS_Store` |
| `requirements.txt` | รายการ dependencies ที่ใช้ในโปรเจกต์ |
| `README.md` | คู่มือใช้งานโปรเจกต์นี้ |

---

## การติดตั้งและใช้งาน

```bash
git clone https://github.com/xooooiz7/TCAS_dashboard.git
cd TCAS_dashboard

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt


# เปิด dashboard
python app.py
# เปิดใน browser: http://127.0.0.1:5000


# ทดสอบดึงข้อมูลเบื้องต้นด้วย Regex-only
jupyter notebook scrap_regex.ipynb

# หรือวิเคราะห์ด้วย Typhoon AI
cp .env.example .env
# แล้วใส่ API Key ของคุณ:
# TYPHOON_API_KEY=YOUR_TYPHOON_API_KEY

python scraping_typhoon.py

