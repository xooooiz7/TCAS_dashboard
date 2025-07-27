# TCAS Dashboard (Flask + Pandas + Typhoon AI)

เว็บแอปสำหรับวิเคราะห์และแสดง **ค่าใช้จ่ายต่อภาคการศึกษา** ของหลักสูตรวิศวกรรมคอมพิวเตอร์จากมหาวิทยาลัยทั่วไทย  
ข้อมูลมาจาก [MyTCAS API](https://mytcas.com) วิเคราะห์ข้อความภาษาไทยด้วย LLM (Typhoon) และแสดงผลผ่าน Dashboard สวย ๆ ด้วย Flask

---

## 📁 โครงสร้างไฟล์

| ไฟล์ / โฟลเดอร์ | หน้าที่ |
|------------------|----------|
| `app.py` | Flask app สำหรับแสดง Dashboard |
| `scraping_typhoon.py` | สคริปต์ดึงข้อมูลจาก API + วิเคราะห์ด้วย Typhoon |
| `scrap_regex.ipynb` | การดึงและประมวลผลข้อความเบื้องต้นด้วย regex-only |
| `courses_data.csv` / `.xlsx` | ไฟล์ raw data ที่เก็บหลัง scrape |
| `cs_engineering_costs.csv` | ไฟล์ที่ใช้แสดงบน Dashboard |
| `templates/` | HTML template (`dashboard.html`) |
| `v2/` | (ยังไม่ทราบหน้าที่แน่ชัด) |
| `.env` | เก็บ `TYPHOON_API_KEY` ไม่ push |
| `.env.example` | Template ของ `.env` สำหรับแชร์ให้คนอื่น |
| `.gitignore` | Ignore `.env`, `__pycache__`, etc. |
| `requirements.txt` | รายชื่อ dependencies |
| `README.md` | คู่มือโปรเจกต์นี้ |

---

## ⚙️ การติดตั้งและรัน

```bash
git clone https://github.com/xooooiz7/TCAS_dashboard.git
cd TCAS_dashboard

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# แล้วแก้ .env ใส่ API key 
# TYPHOON_API_KEY= YOUR_TYPHOON_API_KEY

scrap_regex.ipynb     # ทดลองดึงข้อมูล + วิเคราะห์ด้วย Regex Only
python scraping_typhoon.py     # ทดลองดึงข้อมูล + วิเคราะห์ด้วย Typhoon
python app.py                  # เปิด dashboard ที่ http://127.0.0.1:5000
