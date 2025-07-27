import requests
from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv


# Initialize Typhoon Model Client
load_dotenv(override=True)

TYPHOON_API_KEY = os.getenv('TYPHOON_API_KEY')

client = OpenAI(
    api_key=TYPHOON_API_KEY,
    base_url="https://api.opentyphoon.ai/v1"
)

# โหลดข้อมูลหลักสูตร
json_url = 'https://my-tcas.s3.ap-southeast-1.amazonaws.com/mytcas/courses.json'
response = requests.get(json_url)

# รายการเก็บข้อมูลไว้สร้าง CSV
records = []

if response.status_code == 200:
    data = response.json()
    count = 0

    for course in data:
        # ตรวจสอบเฉพาะวิศวกรรมคอมพิวเตอร์
        program_name = course.get('program_name_th', '').lower()
        field_name = course.get('field_name_th', '').lower()
        faculty_name = course.get('faculty_name_th', '').lower()

        if ('วิศวกรรมคอมพิวเตอร์' in program_name or 
            'วิศวกรรมคอมพิวเตอร์' in field_name or 
            'วิศวกรรมคอมพิวเตอร์' in faculty_name):

            count += 1

            # ดึงข้อมูลหลักสูตร
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
            response = client.chat.completions.create(
                model="typhoon-v2.1-12b-instruct",
                messages=[
                    {"role": "system", "content": "ตอบเฉพาะรูปแบบค่าใช้จ่ายที่สั่งเท่านั้น ห้ามตอบอย่างอื่น"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=100,
            )

            filtered_cost = response.choices[0].message.content.strip()

            # เก็บข้อมูลลงตาราง
            records.append({
                "หลักสูตร": program,
                "มหาวิทยาลัย": university,
                "คณะ": faculty,
                "ค่าใช้จ่าย (ต่อภาค)": filtered_cost,
                "ค่าใช้จ่ายตามเว็บ": cost
            })

            # แสดงใน terminal
            print(f"หลักสูตร: {program}")
            print(f"มหาวิทยาลัย: {university}")
            print(f"คณะ: {faculty}")
            print(filtered_cost)
            print(f'ค่าใช้จ่ายตามเว็บ : {cost}')
            print("-" * 50)

    # สร้างและบันทึก CSV
    df = pd.DataFrame(records)
    df.to_csv("data_clean_typhoon.csv", index=False, encoding='utf-8-sig')
    print(f"\nบันทึกไฟล์เรียบร้อย: cs_engineering_costs.csv")
    print(f"จำนวนหลักสูตรวิศวกรรมคอมพิวเตอร์ทั้งหมด: {count} หลักสูตร")

else:
    print(f"โหลด JSON ไม่สำเร็จ: {response.status_code}")
