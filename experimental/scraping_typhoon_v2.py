import requests
import os
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv

# ====== รายการสาขาวิศวกรรมที่ต้องการค้นหา ======
search_terms = [
    "วิศวกรรมโยธา",
    "วิศวกรรมคอมพิวเตอร์",
    "วิศวกรรมเคมี",
]

load_dotenv(override=True)

TYPHOON_API_KEY = os.getenv('TYPHOON_API_KEY')

client = OpenAI(
    api_key=TYPHOON_API_KEY,
    base_url="https://api.opentyphoon.ai/v1"
)
# ====== โหลดข้อมูลจาก TCAS JSON ======
json_url = 'https://my-tcas.s3.ap-southeast-1.amazonaws.com/mytcas/courses.json'
response = requests.get(json_url)

if response.status_code != 200:
    print(f"❌ โหลด JSON ไม่สำเร็จ: {response.status_code}")
    exit()

data = response.json()

# ====== วนลูปแต่ละสาขา ======
for search_term in search_terms:
    print(f"\n🔎 กำลังค้นหา: {search_term}")
    records = []
    count = 0

    for course in data:
        fields = [
            course.get('program_name_th', '').lower(),
            course.get('field_name_th', '').lower(),
            course.get('faculty_name_th', '').lower()
        ]
        if any(search_term.lower() in field for field in fields):
            count += 1

            program = course.get('program_name_th', 'ไม่พบชื่อหลักสูตร')
            university = course.get('university_name_th', 'ไม่พบชื่อมหาวิทยาลัย')
            faculty = course.get('faculty_name_th', 'ไม่พบคณะ')
            cost = course.get('cost', 'ไม่พบข้อมูลค่าใช้จ่าย')

            prompt = f"""
            ข้อความนี้คือข้อมูลค่าใช้จ่ายของหลักสูตร:\n\"{cost}\"\n

            ให้วิเคราะห์และตอบกลับเฉพาะในรูปแบบนี้:
            ค่าใช้จ่าย: X บาท ต่อภาคการศึกษา

            กฎการวิเคราะห์:
            1. ให้ใช้ตรรกะและความเข้าใจภาษาธรรมชาติในการวิเคราะห์ข้อความทั้งหมด
            2. ให้ถือว่าคำว่า 'ภาคการศึกษาละ', 'เทอมละ', 'ต่อเทอม', 'ต่อภาค', 'ภาคละ' มีความหมายเดียวกันว่า 'ต่อภาคการศึกษา'
            3. ถ้ามีหลายระดับ เช่น 'สายวิทยาศาสตร์ 15,000 / สายสังคม 12,000' ให้เลือก 'สายวิทยาศาสตร์' หรือราคาที่สูงกว่า
            4. ถ้ามีค่าใช้จ่ายภาคฤดูร้อนด้วย ให้มองข้ามและไม่เอาค่านั้นมาใช้
            5. ถ้าข้อความมีทั้งค่าใช้จ่ายตลอดหลักสูตรและต่อภาค ให้เลือกเฉพาะค่าใช้จ่ายต่อภาคการศึกษา
            6. ถ้าข้อความมีแค่ตัวเลขเดียว หรือใช้คำเช่น 'ค่าเรียนทั้งหมด', 'ค่าเล่าเรียนรวม', '4 ปี', หรือ '8 ภาคการศึกษา' ให้ถือว่าเป็น 'ตลอดหลักสูตร' และให้หาร 8 เพื่อหาค่าใช้จ่ายต่อภาค
            7. ถ้าไม่มีข้อมูลชัดเจน หรือลิงก์เว็บไซต์ เช่น 'ดูที่...', 'https://...' ให้ตอบว่า:\nค่าใช้จ่าย: ไม่พบข้อมูลต่อภาคการศึกษา
            8. ห้ามตอบเกินหรือผิดจากรูปแบบนี้เด็ดขาด
            """

            try:
                chat_response = client.chat.completions.create(
                    model="typhoon-v2.1-12b-instruct",
                    messages=[
                        {"role": "system", "content": "ตอบเฉพาะรูปแบบค่าใช้จ่ายที่สั่งเท่านั้น ห้ามตอบอย่างอื่น"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=100,
                )

                filtered_cost = chat_response.choices[0].message.content.strip()
            except Exception as e:
                filtered_cost = "ค่าใช้จ่าย: ไม่พบข้อมูลต่อภาคการศึกษา"
                print(f"⚠️ เกิดข้อผิดพลาด Typhoon: {e}")

            records.append({
                "หลักสูตร": program,
                "มหาวิทยาลัย": university,
                "คณะ": faculty,
                "ค่าใช้จ่าย (ต่อภาค)": filtered_cost,
                "ค่าใช้จ่ายตามเว็บ": cost
            })

            print(f"✅ {program} | {university} | {filtered_cost}")

    # ====== สร้างไฟล์ CSV ถ้าพบข้อมูล ======
    if count > 0:
        filename = f"{search_term}.csv"
        df = pd.DataFrame(records)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"📁 บันทึกไฟล์เรียบร้อย: {filename} ({count} หลักสูตร)")
    else:
        print(f"❌ ไม่พบหลักสูตรที่เกี่ยวข้องกับ: {search_term}")
