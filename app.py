import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="Cashflow Pro V39", layout="wide")

st.markdown("""
<style>
    /* ---------------------- CSS FIXES ---------------------- */
    
    /* บังคับสีตัวอักษรในกล่องให้เป็นสีเข้ม (แก้ปัญหามองไม่เห็นใน Dark Mode) */
    .dash-box, .stat-card {
        color: #333333 !important; /* สีเทาเข้มเกือบดำ */
    }
    
    .dash-label {
        font-size: 14px;
        color: #555555 !important;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .dash-value {
        font-size: 24px;
        font-weight: 800;
        color: #000000 !important; /* สีดำสนิท */
    }
    
    h3, h4 {
        color: #000000 !important; /* หัวข้อในการ์ดก็ต้องดำ */
        margin: 0;
        padding: 5px 0;
    }

    /* ------------------------------------------------------- */

    .player-header { background-color: #fff3cd; border-left: 10px solid #ffc107; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .ph-name { font-size: 28px; font-weight: bold; color: #333; margin: 0; }
    .ph-job { font-size: 18px; color: #666; font-style: italic; }

    .dashboard-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
    .dash-box { flex: 1; background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #ccc; min-width: 160px; }
    
    .box-passive { border-color: #0d6efd; }
    .box-total-inc { border-color: #0dcaf0; }
    .box-expense { border-color: #dc3545; }
    .box-flow { border-color: #198754; background-color: #e8f5e9; }
    
    .txt-passive { color: #0d6efd !important; } 
    .txt-inc { color: #0dcaf0 !important; } 
    .txt-exp { color: #dc3545 !important; } 
    .txt-flow { color: #198754 !important; font-size: 32px; } 

    .input-area { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; color: #333; }
    
    /* Headers & Tables */
    .header-blue { background-color: #4472c4; color: white !important; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    .header-orange { background-color: #ed7d31; color: white !important; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    .header-green { background-color: #70ad47; color: white !important; padding: 8px; text-align: center; font-weight: bold; border-radius: 5px 5px 0 0; }
    
    .stat-card { background-color: #ffffff; padding: 15px; border: 2px solid #ddd; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    
    .stDataFrame { border: 1px solid #ddd; }
    
    /* Fast Track */
    .ft-header { background: linear-gradient(90deg, #FFD700, #B8860B); color: white; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px; }
    .ft-title { font-size: 42px; font-weight: 900; text-transform: uppercase; text-shadow: 2px 2px 4px #000; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ---
ASSET_TYPES = [
    "บ้านเช่า", "คอนโดมิเนียม", "ตึกแถว 1 คูหา", "ตึกแถว 2 คูหา", "ตึกแถว 4 คูหา",
    "อพาร์ทเม้นท์ 12 ห้อง", "อพาร์ทเม้นท์ 24 ห้อง", "อพาร์ทเม้นท์ 60 ห้อง",
    "ที่ดิน 10 ไร่", "ที่ดิน 100 ตารางวา", "บริษัทซอฟต์แวร์", "บริษัทผลิตตัวนำไฟฟ้า", 
    "กิจการเกสต์เฮ้าส์", "กิจการล้างรถ", "กิจการตู้เครื่องดื่ม", "กิจการตู้เกม", 
    "หุ้นส่วนร่วมลงทุน", "อื่นๆ"
]
STOCK_TYPES = ["หุ้นยาจำกัด", "หุ้นเอนเตอร์เทนเม้น", "หุ้นโฮมอิเล็กทรอนิกส์", "กองทุนรวม", "OK4U (หุ้นซิ่ง)"]

TX_RAT_RACE = [
    "🟢 รับเงินเดือน (Payday)", "🎁 การ์ดโอกาส / ปรับปรุง (เพิ่ม-ลด CF)",
    "🏢 ซื้อทรัพย์สิน/ธุรกิจ", "📉 ขายทรัพย์สิน", "📈 ซื้อหุ้น", "📉 ขายหุ้น",
    "🥇 ซื้อ/ขาย ทองคำ", "🛍️ รายจ่าย/ซื้อความสุข", "👶 มีลูก",
    "🙏 บริจาคการกุศล (10%)", "⚠️ ตกงาน (จ่าย 100% รายจ่าย)", "🏦 กู้เงิน/จ่ายหนี้"
]

TX_FAST_TRACK = ["🟢 Cash Flow (รับเงิน)", "🏢 ซื้อกิจการ (ลงทุน)", "🛍️ ซื้อความสุข", "🙏 บริจาคการกุศล (1M)", "⚖️ ถูกฟ้อง (เสีย 50%)", "🔍 ตรวจสอบภาษี (เสีย 50%)", "💔 หย่า (หมดตัว!)"]

# ฐานข้อมูลอาชีพ (ครบ 31 อาชีพ)
PROFESSIONS = {
    "แพทย์ (Doctor)": {"salary": 132000, "tax": 32000, "savings": 35000, "child_cost": 7000, "expenses": {"ผ่อนบ้าน": 19000, "กู้เรียน": 7000, "ผ่อนรถ": 3000, "บัตรเครดิต": 2000, "อื่นๆ": 20000}, "liabilities": {"หนี้บ้าน": 2020000, "หนี้กู้เรียน": 1500000, "หนี้รถ": 190000, "หนี้บัตรเครดิต": 100000}},
    "นักบิน (Pilot)": {"salary": 95000, "tax": 20000, "savings": 25000, "child_cost": 4000, "expenses": {"ผ่อนบ้าน": 10000, "กู้เรียน": 0, "ผ่อนรถ": 3000, "บัตรเครดิต": 7000, "อื่นๆ": 20000}, "liabilities": {"หนี้บ้าน": 900000, "หนี้กู้เรียน": 0, "หนี้รถ": 150000, "หนี้บัตรเครดิต": 220000}},
    "ทนายความ (Lawyer)": {"salary": 75000, "tax": 18000, "savings": 20000, "child_cost": 4000, "expenses": {"ผ่อนบ้าน": 11000, "กู้เรียน": 3000, "ผ่อนรถ": 2000, "บัตรเครดิต": 2000, "อื่นๆ": 15000}, "liabilities": {"หนี้บ้าน": 1150000, "หนี้กู้เรียน": 780000, "หนี้รถ": 110000, "หนี้บัตรเครดิต": 70000}},
    "วิศวกร (Engineer)": {"salary": 49000, "tax": 10000, "savings": 4000, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 7000, "กู้เรียน": 1000, "ผ่อนรถ": 2000, "บัตรเครดิต": 2000, "อื่นๆ": 10000}, "liabilities": {"หนี้บ้าน": 750000, "หนี้กู้เรียน": 120000, "หนี้รถ": 70000, "หนี้บัตรเครดิต": 50000}},
    "ผู้จัดการ (Manager)": {"salary": 46000, "tax": 9000, "savings": 4000, "child_cost": 3000, "expenses": {"ผ่อนบ้าน": 7000, "กู้เรียน": 1000, "ผ่อนรถ": 1000, "บัตรเครดิต": 2000, "อื่นๆ": 1000}, "liabilities": {"หนี้บ้าน": 750000, "หนี้กู้เรียน": 120000, "หนี้รถ": 60000, "หนี้บัตรเครดิต": 40000}},
    "ครูประถม (Teacher)": {"salary": 33000, "tax": 5000, "savings": 4000, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 5000, "กู้เรียน": 1000, "ผ่อนรถ": 1000, "บัตรเครดิต": 2000, "อื่นๆ": 7000}, "liabilities": {"หนี้บ้าน": 500000, "หนี้กู้เรียน": 120000, "หนี้รถ": 50000, "หนี้บัตรเครดิต": 40000}},
    "พยาบาล (Nurse)": {"salary": 31000, "tax": 6000, "savings": 5000, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 4000, "กู้เรียน": 1000, "ผ่อนรถ": 1000, "บัตรเครดิต": 2000, "อื่นๆ": 6000}, "liabilities": {"หนี้บ้าน": 470000, "หนี้กู้เรียน": 60000, "หนี้รถ": 50000, "หนี้บัตรเครดิต": 40000}},
    "ตำรวจ (Police)": {"salary": 30000, "tax": 6000, "savings": 5000, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 4000, "กู้เรียน": 0, "ผ่อนรถ": 1000, "บัตรเครดิต": 1000, "อื่นๆ": 7000}, "liabilities": {"หนี้บ้าน": 460000, "หนี้กู้เรียน": 0, "หนี้รถ": 50000, "หนี้บัตรเครดิต": 30000}},
    "เลขานุการ (Secretary)": {"salary": 25000, "tax": 5000, "savings": 7000, "child_cost": 1000, "expenses": {"ผ่อนบ้าน": 4000, "กู้เรียน": 0, "ผ่อนรถ": 1000, "บัตรเครดิต": 1000, "อื่นๆ": 6000}, "liabilities": {"หนี้บ้าน": 380000, "หนี้กู้เรียน": 0, "หนี้รถ": 40000, "หนี้บัตรเครดิต": 30000}},
    "พนักงานขับรถบรรทุก (Driver)": {"salary": 25000, "tax": 5000, "savings": 7500, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 4000, "กู้เรียน": 0, "ผ่อนรถ": 1000, "บัตรเครดิต": 1000, "อื่นๆ": 6000}, "liabilities": {"หนี้บ้าน": 380000, "หนี้กู้เรียน": 0, "หนี้รถ": 40000, "หนี้บัตรเครดิต": 30000}},
    "ช่างเครื่องยนต์ (Mechanic)": {"salary": 20000, "tax": 4000, "savings": 7000, "child_cost": 1000, "expenses": {"ผ่อนบ้าน": 3000, "กู้เรียน": 0, "ผ่อนรถ": 1000, "บัตรเครดิต": 1000, "อื่นๆ": 4000}, "liabilities": {"หนี้บ้าน": 310000, "หนี้กู้เรียน": 0, "หนี้รถ": 30000, "หนี้บัตรเครดิต": 30000}},
    "พนักงานทำความสะอาด (Janitor)": {"salary": 16000, "tax": 3000, "savings": 6000, "child_cost": 1000, "expenses": {"ผ่อนบ้าน": 2000, "กู้เรียน": 0, "ผ่อนรถ": 1000, "บัตรเครดิต": 1000, "อื่นๆ": 3000}, "liabilities": {"หนี้บ้าน": 200000, "หนี้กู้เรียน": 0, "หนี้รถ": 40000, "หนี้บัตรเครดิต": 3000}},
    "โปรแกรมเมอร์ (Programmer)": {"salary": 65000, "tax": 12000, "savings": 10000, "child_cost": 3000, "expenses": {"ผ่อนบ้าน": 9000, "กู้เรียน": 3000, "ผ่อนรถ": 4000, "บัตรเครดิต": 3000, "อื่นๆ": 12000}, "liabilities": {"หนี้บ้าน": 1200000, "หนี้กู้เรียน": 400000, "หนี้รถ": 600000, "หนี้บัตรเครดิต": 60000}},
    "YouTuber/Streamer": {"salary": 80000, "tax": 15000, "savings": 20000, "child_cost": 4000, "expenses": {"ผ่อนบ้าน": 12000, "กู้เรียน": 0, "ผ่อนรถ": 5000, "บัตรเครดิต": 5000, "อื่นๆ": 25000}, "liabilities": {"หนี้บ้าน": 1500000, "หนี้กู้เรียน": 0, "หนี้รถ": 700000, "หนี้บัตรเครดิต": 100000}},
    "นักบัญชี (Accountant)": {"salary": 45000, "tax": 8000, "savings": 5000, "child_cost": 2500, "expenses": {"ผ่อนบ้าน": 7000, "กู้เรียน": 2000, "ผ่อนรถ": 2000, "บัตรเครดิต": 1500, "อื่นๆ": 8000}, "liabilities": {"หนี้บ้าน": 800000, "หนี้กู้เรียน": 250000, "หนี้รถ": 300000, "หนี้บัตรเครดิต": 40000}},
    "ทหาร (Soldier)": {"salary": 28000, "tax": 4500, "savings": 5000, "child_cost": 1500, "expenses": {"ผ่อนบ้าน": 3500, "กู้เรียน": 0, "ผ่อนรถ": 1500, "บัตรเครดิต": 1500, "อื่นๆ": 6000}, "liabilities": {"หนี้บ้าน": 400000, "หนี้กู้เรียน": 0, "หนี้รถ": 200000, "หนี้บัตรเครดิต": 35000}},
    "นักการเมือง (Politician)": {"salary": 115000, "tax": 25000, "savings": 30000, "child_cost": 6000, "expenses": {"ผ่อนบ้าน": 18000, "กู้เรียน": 0, "ผ่อนรถ": 8000, "บัตรเครดิต": 10000, "อื่นๆ": 35000}, "liabilities": {"หนี้บ้าน": 3500000, "หนี้กู้เรียน": 0, "หนี้รถ": 1200000, "หนี้บัตรเครดิต": 500000}},
    "เซลล์แมน (Salesman)": {"salary": 40000, "tax": 6000, "savings": 6000, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 5000, "กู้เรียน": 1000, "ผ่อนรถ": 4000, "บัตรเครดิต": 3000, "อื่นๆ": 8000}, "liabilities": {"หนี้บ้าน": 600000, "หนี้กู้เรียน": 100000, "หนี้รถ": 50000, "หนี้บัตรเครดิต": 80000}},
    "อัยการ (Prosecutor)": {"salary": 90000, "tax": 22000, "savings": 20000, "child_cost": 5000, "expenses": {"ผ่อนบ้าน": 15000, "กู้เรียน": 4000, "ผ่อนรถ": 4000, "บัตรเครดิต": 3000, "อื่นๆ": 15000}, "liabilities": {"หนี้บ้าน": 2500000, "หนี้กู้เรียน": 500000, "หนี้รถ": 800000, "หนี้บัตรเครดิต": 100000}},
    "นักเต้น (Dancer)": {"salary": 28000, "tax": 3000, "savings": 4000, "child_cost": 1500, "expenses": {"ผ่อนบ้าน": 4000, "กู้เรียน": 1000, "ผ่อนรถ": 1000, "บัตรเครดิต": 2000, "อื่นๆ": 8000}, "liabilities": {"หนี้บ้าน": 500000, "หนี้กู้เรียน": 150000, "หนี้รถ": 100000, "หนี้บัตรเครดิต": 50000}},
    "Project Manager": {"salary": 75000, "tax": 15000, "savings": 12000, "child_cost": 3500, "expenses": {"ผ่อนบ้าน": 12000, "กู้เรียน": 2000, "ผ่อนรถ": 5000, "บัตรเครดิต": 4000, "อื่นๆ": 10000}, "liabilities": {"หนี้บ้าน": 1800000, "หนี้กู้เรียน": 300000, "หนี้รถ": 700000, "หนี้บัตรเครดิต": 90000}},
    "ทันตแพทย์ (Dentist)": {"salary": 110000, "tax": 28000, "savings": 30000, "child_cost": 6000, "expenses": {"ผ่อนบ้าน": 18000, "กู้เรียน": 10000, "ผ่อนรถ": 4000, "บัตรเครดิต": 3000, "อื่นๆ": 18000}, "liabilities": {"หนี้บ้าน": 1900000, "หนี้กู้เรียน": 2000000, "หนี้รถ": 250000, "หนี้บัตรเครดิต": 150000}},
    "นักวิทยาศาสตร์ข้อมูล (Data Scientist)": {"salary": 70000, "tax": 14000, "savings": 15000, "child_cost": 4000, "expenses": {"ผ่อนบ้าน": 10000, "กู้เรียน": 3000, "ผ่อนรถ": 3000, "บัตรเครดิต": 2000, "อื่นๆ": 12000}, "liabilities": {"หนี้บ้าน": 1000000, "หนี้กู้เรียน": 400000, "หนี้รถ": 200000, "หนี้บัตรเครดิต": 50000}},
    "สถาปนิก (Architect)": {"salary": 45000, "tax": 8000, "savings": 5000, "child_cost": 2500, "expenses": {"ผ่อนบ้าน": 7000, "กู้เรียน": 2000, "ผ่อนรถ": 3000, "บัตรเครดิต": 2000, "อื่นๆ": 8000}, "liabilities": {"หนี้บ้าน": 750000, "หนี้กู้เรียน": 250000, "หนี้รถ": 180000, "หนี้บัตรเครดิต": 60000}},
    "เภสัชกร (Pharmacist)": {"salary": 55000, "tax": 10000, "savings": 10000, "child_cost": 3000, "expenses": {"ผ่อนบ้าน": 8000, "กู้เรียน": 4000, "ผ่อนรถ": 3000, "บัตรเครดิต": 2000, "อื่นๆ": 10000}, "liabilities": {"หนี้บ้าน": 850000, "หนี้กู้เรียน": 600000, "หนี้รถ": 150000, "หนี้บัตรเครดิต": 40000}},
    "แอร์โฮสเตส (Flight Attendant)": {"salary": 60000, "tax": 11000, "savings": 10000, "child_cost": 3000, "expenses": {"ผ่อนบ้าน": 9000, "กู้เรียน": 2000, "ผ่อนรถ": 4000, "บัตรเครดิต": 5000, "อื่นๆ": 15000}, "liabilities": {"หนี้บ้าน": 950000, "หนี้กู้เรียน": 200000, "หนี้รถ": 300000, "หนี้บัตรเครดิต": 120000}},
    "พ่อครัว/เชฟ (Chef)": {"salary": 35000, "tax": 5500, "savings": 4000, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 6000, "กู้เรียน": 2000, "ผ่อนรถ": 2000, "บัตรเครดิต": 2000, "อื่นๆ": 7000}, "liabilities": {"หนี้บ้าน": 600000, "หนี้กู้เรียน": 200000, "หนี้รถ": 100000, "หนี้บัตรเครดิต": 50000}},
    "กราฟิกดีไซเนอร์ (Graphic Designer)": {"salary": 28000, "tax": 4500, "savings": 3000, "child_cost": 1500, "expenses": {"ผ่อนบ้าน": 5000, "กู้เรียน": 2000, "ผ่อนรถ": 1500, "บัตรเครดิต": 1500, "อื่นๆ": 6000}, "liabilities": {"หนี้บ้าน": 500000, "หนี้กู้เรียน": 150000, "หนี้รถ": 80000, "หนี้บัตรเครดิต": 30000}},
    "นักการตลาด (Marketer)": {"salary": 32000, "tax": 6000, "savings": 4000, "child_cost": 2000, "expenses": {"ผ่อนบ้าน": 5500, "กู้เรียน": 2000, "ผ่อนรถ": 2000, "บัตรเครดิต": 2000, "อื่นๆ": 7000}, "liabilities": {"หนี้บ้าน": 550000, "หนี้กู้เรียน": 150000, "หนี้รถ": 120000, "หนี้บัตรเครดิต": 40000}},
    "พ่อค้าออนไลน์ (Online Seller)": {"salary": 50000, "tax": 5000, "savings": 8000, "child_cost": 2500, "expenses": {"ผ่อนบ้าน": 7000, "กู้เรียน": 0, "ผ่อนรถ": 4000, "บัตรเครดิต": 6000, "อื่นๆ": 15000}, "liabilities": {"หนี้บ้าน": 700000, "หนี้กู้เรียน": 0, "หนี้รถ": 400000, "หนี้บัตรเครดิต": 200000}},
    "ข้าราชการ (Civil Servant)": {"salary": 22000, "tax": 1000, "savings": 3000, "child_cost": 1500, "expenses": {"ผ่อนบ้าน": 4000, "กู้เรียน": 1000, "ผ่อนรถ": 1500, "บัตรเครดิต": 1500, "อื่นๆ": 6000}, "liabilities": {"หนี้บ้าน": 400000, "หนี้กู้เรียน": 100000, "หนี้รถ": 100000, "หนี้บัตรเครดิต": 30000}}
}

# --- 3. LOGIC ---
class Player:
    def __init__(self, name, job):
        self.name = name
        self.job = job
        stats = PROFESSIONS.get(job, PROFESSIONS.get("ครูประถม (Teacher)", list(PROFESSIONS.values())[0]))
        self.salary = stats["salary"]
        self.cash = stats["savings"]
        self.gold = 0
        self.child_cost = stats["child_cost"]
        self.assets = []
        self.stocks = []
        self.children = 0
        self.expenses = stats["expenses"].copy()
        self.expenses["ภาษี"] = stats["tax"]
        self.expenses["เลี้ยงดูบุตร"] = 0
        self.expenses["ดอกเบี้ยกู้"] = 0
        self.liabilities = stats["liabilities"].copy()
        self.liabilities["หนี้ธนาคาร"] = 0
        self.ledger = []
        self.log("เริ่มเกม", stats["savings"], 0)
        self.in_fast_track = False
        self.fast_track_cf = 0
        self.ft_initial_cf = 0

    @property
    def passive_income(self): return sum(a.get('Cashflow', 0) for a in self.assets)
    @property
    def total_expenses(self): return sum(self.expenses.values())
    @property
    def total_income(self): return self.salary + self.passive_income
    @property
    def monthly_cashflow(self): return self.total_income - self.total_expenses
    
    def check_escape(self): return self.passive_income > self.total_expenses

    def go_fast_track(self):
        self.in_fast_track = True
        self.fast_track_cf = self.passive_income * 100 
        self.ft_initial_cf = self.fast_track_cf
        self.cash += self.fast_track_cf 
        self.log(">>> เข้าสู่ FAST TRACK! <<<", self.fast_track_cf, 0)

    def log(self, item, inc, exp):
        self.ledger.append({"เวลา": datetime.now().strftime("%H:%M:%S"),"รายการ": item,"รับ": inc,"จ่าย": exp,"คงเหลือ": self.cash})

    # ACTIONS
    def receive_payday(self):
        amt = self.monthly_cashflow; self.cash += amt; self.log("รับเงินเดือน", amt, 0); return f"💰 รับเงินเดือนแล้ว {amt:,} บาท"
    
    def buy_asset(self, name, cost, down, flow):
        if self.cash >= down:
            self.cash -= down; loan = cost - down
            if loan > 0: self.liabilities[f"หนี้ ({name})"] = loan
            self.assets.append({"รายการ": name, "ราคา": cost, "เงินดาวน์": down, "Cashflow": flow, "หนี้": loan})
            self.log(f"ซื้อ {name}", 0, down); return True, "✅ ซื้อสำเร็จ"
        return False, "❌ เงินไม่พอ"

    def sell_asset(self, idx, sale_price):
        if 0 <= idx < len(self.assets):
            asset = self.assets[idx]
            debt_key = f"หนี้ ({asset['รายการ']})"
            debt = self.liabilities.get(debt_key, 0)
            get = sale_price - debt
            self.cash += get
            if debt_key in self.liabilities: del self.liabilities[debt_key]
            self.assets.pop(idx)
            self.log(f"ขาย {asset['รายการ']}", get, 0); return True, f"✅ ได้เงิน {get:,}"
        return False, "❌ ผิดพลาด"

    def update_asset_cf(self, idx, added_cf):
        if 0 <= idx < len(self.assets):
            self.assets[idx]['Cashflow'] += added_cf
            self.log(f"ปรับปรุง CF", 0, 0); return True, "✅ เรียบร้อย"
        return False, "❌ ผิดพลาด"

    def buy_stock(self, sym, price, qty):
        cost = price * qty
        if self.cash >= cost:
            self.cash -= cost; found = False
            for s in self.stocks:
                if s['symbol'] == sym: s['qty'] += qty; s['last_price'] = price; found = True
            if not found: self.stocks.append({"symbol": sym, "qty": qty, "cost": price, "last_price": price})
            self.log(f"ซื้อหุ้น {sym}", 0, cost); return True, "✅ สำเร็จ"
        return False, "❌ เงินไม่พอ"

    def sell_stock(self, sym, price, qty):
        for i, s in enumerate(self.stocks):
            if s['symbol'] == sym and s['qty'] >= qty:
                get = price * qty; self.cash += get; s['qty'] -= qty
                if s['qty'] == 0: self.stocks.pop(i)
                self.log(f"ขายหุ้น {sym}", get, 0); return True, f"✅ ได้เงิน {get:,}"
        return False, "❌ หุ้นไม่พอ"

    def buy_gold(self, cost):
        if self.cash >= cost: self.cash -= cost; self.gold += cost; self.log("ซื้อทอง", 0, cost); return True, "✅ สำเร็จ"
        return False, "❌ เงินไม่พอ"
    
    def sell_gold(self, amt):
        if self.gold >= amt: self.cash += amt; self.gold -= amt; self.log("ขายทอง", amt, 0); return True, "✅ สำเร็จ"
        return False, "❌ ทองไม่พอ"

    def expense_event(self, name, amount):
        if self.cash >= amount: self.cash -= amount; self.log(name, 0, amount); return True, "💸 จ่ายแล้ว"
        return False, "❌ เงินไม่พอจ่าย"

    def donate_rat_race(self):
        amt = int(self.total_income * 0.10)
        if self.cash >= amt: self.cash -= amt; self.log("บริจาค", 0, amt); return True, f"🙏 บริจาค {amt:,}"
        return False, "❌ เงินไม่พอ"

    def unemployed_rat_race(self):
        amt = self.total_expenses
        if self.cash >= amt: self.cash -= amt; self.log("ตกงาน", 0, amt); return True, f"⚠️ จ่าย {amt:,}"
        return False, "❌ เงินไม่พอ"

    def take_loan(self, amt):
        self.cash += amt; self.liabilities["หนี้ธนาคาร"] += amt; self.expenses["ดอกเบี้ยกู้"] += int(amt*0.1)
        self.log("กู้เงิน", amt, 0); return "✅ กู้สำเร็จ"

    def pay_debt(self, name, amt):
        if self.cash >= amt:
            self.cash -= amt
            if name == "หนี้ธนาคาร": 
                self.liabilities[name] -= amt
                if self.liabilities[name] <= 0: self.liabilities[name] = 0
                self.expenses["ดอกเบี้ยกู้"] = int(self.liabilities[name] * 0.1)
            else:
                del self.liabilities[name]
                if "บ้าน" in name: self.expenses.pop("ผ่อนบ้าน",None)
                elif "รถ" in name: self.expenses.pop("ผ่อนรถ",None)
                elif "บัตร" in name: self.expenses.pop("บัตรเครดิต",None)
            self.log(f"ปลดหนี้ {name}", 0, amt); return True, "✅ หมดหนี้"
        return False, "❌ เงินไม่พอ"

    def ft_payday(self): self.cash += self.fast_track_cf; self.log("รับเงิน FT", self.fast_track_cf, 0)
    def ft_buy(self, n, c, f):
        if self.cash >= c: self.cash-=c; self.fast_track_cf+=f; self.log(f"ลงทุน FT: {name}", 0, cost); return True, f"✅ สำเร็จ (CF +{flow:,})"
        return False, "❌ เงินไม่พอ"
    def ft_charity(self):
        if self.cash >= 1000000: self.cash-=1000000; self.log("บริจาค FT",0,1000000); return True, "🙏 สำเร็จ"
        return False, "❌ เงินไม่พอ"
    def ft_bad_event(self, t):
        l = self.cash if t=="หย่า" else int(self.cash/2); self.cash-=l; self.log(t,0,l); return f"📉 เสีย {l:,}"

# --- 4. SESSION ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.players = []

# --- 5. SETUP ---
if not st.session_state.game_started:
    st.title("🎲 Cashflow Setup")
    num = st.number_input("จำนวนผู้เล่น", 1, 6, 1)
    with st.form("setup"):
        cols = st.columns(3)
        for i in range(num):
            with cols[i%3]:
                st.markdown(f"**P{i+1}**")
                n = st.text_input(f"ชื่อ", f"P{i+1}", key=f"n{i}")
                j = st.selectbox(f"อาชีพ", list(PROFESSIONS.keys()), key=f"j{i}")
                st.session_state[f"temp_p{i}"] = (n, j)
        if st.form_submit_button("🚀 เริ่มเกม"):
            for i in range(num):
                n_val = st.session_state.get(f"temp_p{i}", (f"P{i+1}", list(PROFESSIONS.keys())[0]))[0]
                j_val = st.session_state.get(f"temp_p{i}", (f"P{i+1}", list(PROFESSIONS.keys())[0]))[1]
                st.session_state.players.append(Player(n_val, j_val))
            st.session_state.game_started = True
            st.rerun()

# --- 6. MAIN APP ---
else:
    with st.sidebar:
        st.header("Menu")
        menu = st.radio("เลือกหน้าจอ", ["🎮 เล่นเกม (Action)", "📊 ดูภาพรวม (Dashboard)"])
        st.divider()
        if menu == "🎮 เล่นเกม (Action)":
            st.header("Control")
            p_idx = st.radio("ผู้เล่น", range(len(st.session_state.players)), format_func=lambda i: st.session_state.players[i].name)
            p = st.session_state.players[p_idx]
            st.divider()
            if st.button("🎲 ทอยเต๋า"): st.success(f"แต้ม: {random.randint(1,6)}")
            if st.button("❌ รีเซ็ต"): st.session_state.clear(); st.rerun()

    # ================= RAT RACE =================
    if menu == "🎮 เล่นเกม (Action)":
        if not p.in_fast_track:
            st.markdown(f"""<div class="player-header"><div class="ph-name">👤 {p.name}</div><div class="ph-job">💼 อาชีพ: {p.job}</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="dashboard-container">
                <div class="dash-box box-passive"><div class="dash-label">รายได้ทรัพย์สิน</div><div class="dash-value txt-passive">{p.passive_income:,.0f}</div></div>
                <div class="dash-box box-total-inc"><div class="dash-label">รายรับรวม</div><div class="dash-value txt-inc">{p.total_income:,.0f}</div></div>
                <div class="dash-box box-expense"><div class="dash-label">รายจ่ายรวม</div><div class="dash-value txt-exp">{p.total_expenses:,.0f}</div></div>
                <div class="dash-box box-flow"><div class="dash-label">Cashflow</div><div class="dash-value txt-flow">{p.monthly_cashflow:,.0f}</div></div>
            </div>
            """, unsafe_allow_html=True)

            if p.check_escape():
                st.success("🎉 ยินดีด้วย! รายได้ทรัพย์สิน > รายจ่ายแล้ว!")
                if st.button("🚀 ไปสู่ FAST TRACK", type="primary"): p.go_fast_track(); st.rerun()

            st.markdown("### 📝 บันทึกรายการ")
            with st.container():
                st.markdown('<div class="input-area">', unsafe_allow_html=True)
                tx_type = st.selectbox("ทำรายการ", TX_RAT_RACE)

                if "รับเงินเดือน" in tx_type:
                    if st.button("💰 รับเงิน"): msg=p.receive_payday(); st.success(msg); st.rerun()
                elif "การ์ดโอกาส" in tx_type:
                    if p.assets:
                        opts=[f"{i}: {a['รายการ']} (CF: {a['Cashflow']:,})" for i,a in enumerate(p.assets)]
                        sel=st.selectbox("เลือกทรัพย์สิน",opts); idx=int(sel.split(":")[0])
                        c1,c2=st.columns(2)
                        with c1:
                            add_cf=st.number_input("เพิ่ม/ลด CF",value=0,step=500)
                            if st.button("ปรับ CF"): ok,m=p.update_asset_cf(idx,add_cf); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                        with c2:
                            spr=st.number_input("ราคาขาย",0,step=10000)
                            if st.button("ขาย"): ok,m=p.sell_asset(idx,spr); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                    else: st.warning("ไม่มีทรัพย์สิน")
                elif "ซื้อทรัพย์สิน" in tx_type:
                    c1,c2,c3,c4 = st.columns(4)
                    nm = c1.selectbox("ชื่อ", ASSET_TYPES); pr = c2.number_input("ราคาเต็ม",0,step=10000)
                    d = c3.number_input("ดาวน์",0,step=5000); cf = c4.number_input("CF",0,step=100)
                    loan_disp = max(0, pr - d); st.caption(f"ยอดกู้: {loan_disp:,}")
                    if st.button("บันทึกซื้อ"): ok,m=p.buy_asset(nm,pr,d,cf); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "ซื้อหุ้น" in tx_type:
                    c1,c2,c3 = st.columns(3)
                    sym = c1.selectbox("หุ้น", STOCK_TYPES); pr = c2.number_input("ราคา/หุ้น", 1)
                    mx = int(p.cash/pr) if pr>0 else 0; st.caption(f"ซื้อได้สูงสุด: {mx}")
                    qt = c3.number_input("จำนวน", 100, step=100)
                    st.info(f"รวม: {pr*qt:,}")
                    if st.button("ซื้อหุ้น"): ok,m=p.buy_stock(sym,pr,qt); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "ขายหุ้น" in tx_type:
                    if p.stocks:
                        sym = st.selectbox("หุ้น", set([s['symbol'] for s in p.stocks]))
                        has = sum([s['qty'] for s in p.stocks if s['symbol']==sym]); st.info(f"มี {has}")
                        
                        st.caption("พอร์ตของคุณ:")
                        df_s_mini = pd.DataFrame([{"หุ้น":s['symbol'], "ทุน":s['cost'], "ราคาล่าสุด":s.get('last_price',s['cost'])} for s in p.stocks if s['symbol']==sym])
                        st.dataframe(df_s_mini, hide_index=True)

                        c1,c2=st.columns(2); pr=c1.number_input("ราคาขาย",1); qt=c2.number_input("จำนวน",1,has,has)
                        st.success(f"รับเงิน: {pr*qt:,}")
                        if st.button("ขายหุ้น"): ok,m=p.sell_stock(sym,pr,qt); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                    else: st.warning("ไม่มีหุ้น")
                elif "รายจ่าย" in tx_type:
                    n = st.text_input("รายการ"); c = st.number_input("ราคา",0,step=100)
                    if st.button("จ่าย"): ok,m=p.expense_event(n,c); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "บริจาค" in tx_type:
                    if st.button("บริจาค 10%"): ok,m=p.donate_rat_race(); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "ตกงาน" in tx_type:
                    if st.button("จ่ายค่าใช้จ่ายรวม"): ok,m=p.unemployed_rat_race(); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "กู้เงิน" in tx_type:
                    act = st.radio("เลือก", ["กู้", "จ่ายหนี้"])
                    if act == "กู้":
                        amt = st.number_input("ยอดกู้",0,step=1000)
                        if st.button("กู้"): m=p.take_loan(amt); st.success(m); st.rerun()
                    else:
                        d = st.selectbox("หนี้", list(p.liabilities.keys()))
                        if d:
                            v = p.liabilities[d]; st.write(f"ยอด: {v:,}")
                            # Partial Payment Input
                            if d == "หนี้ธนาคาร":
                                pay_amt = st.number_input("ระบุยอดจ่าย (ผ่อนได้)", 1, v, v)
                            else:
                                st.caption("ต้องจ่ายเต็มจำนวน")
                                pay_amt = v
                            if st.button("ชำระ"): ok,m=p.pay_debt(d,pay_amt); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "ทองคำ" in tx_type:
                    mode = st.radio("เลือก", ["ซื้อ", "ขาย"])
                    val = st.number_input("มูลค่า", 0, step=1000)
                    if st.button("ยืนยัน"): 
                        if mode=="ซื้อ": ok,m=p.buy_gold(val)
                        else: ok,m=p.sell_gold(val)
                        (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "มีลูก" in tx_type:
                    if st.button("มีลูก"): 
                        if p.children < 3: p.children+=1; p.expenses["เลี้ยงดูบุตร"]=p.children*p.child_cost; st.success("ยินดีด้วย!"); st.rerun()
                        else: st.error("ครบแล้ว")

                st.markdown('</div>', unsafe_allow_html=True)

            # [ADDED BACK] TABLES ON ACTION SCREEN
            st.markdown("---")
            l, r = st.columns([5, 5])
            with l:
                st.markdown('<div class="blue-header">บัญชีรายรับ-รายจ่าย</div>', unsafe_allow_html=True)
                if p.ledger: st.dataframe(pd.DataFrame(p.ledger).iloc[::-1], hide_index=True, use_container_width=True, height=400)
            with r:
                st.markdown('<div class="green-header">ทรัพย์สิน (Assets)</div>', unsafe_allow_html=True)
                st.markdown(f"""<div class="asset-summary-box"><div>💵 เงินสด: {p.cash:,}</div><div style="color:#d4af37;">🥇 ทองคำ: {p.gold:,}</div></div>""", unsafe_allow_html=True)
                
                t1, t2 = st.tabs(["อสังหา/ธุรกิจ", "หุ้น/กองทุน"])
                with t1:
                    if p.assets: 
                        df_assets = pd.DataFrame(p.assets)
                        # Ensure keys exist
                        if 'เงินดาวน์' not in df_assets.columns: df_assets['เงินดาวน์'] = 0
                        if 'หนี้' not in df_assets.columns: df_assets['หนี้'] = 0
                        st.dataframe(df_assets[['รายการ','เงินดาวน์','ราคา','Cashflow','หนี้']], hide_index=True)
                    else: st.caption("-ว่าง-")
                with t2:
                    if p.stocks: 
                        df_stocks = pd.DataFrame([{"หุ้น":s['symbol'], "จำนวน":s['qty'], "ทุนเฉลี่ย":s['cost'], "ราคาล่าสุด":s.get('last_price',s['cost'])} for s in p.stocks])
                        st.dataframe(df_stocks, hide_index=True)
                    else: st.caption("-ว่าง-")
                
                st.markdown('<div class="blue-header" style="background:#dc3545; margin-top:10px;">หนี้สิน (Liabilities)</div>', unsafe_allow_html=True)
                if p.liabilities: st.dataframe(pd.DataFrame(list(p.liabilities.items()), columns=['รายการ','คงเหลือ']), hide_index=True)

        # Fast Track Action
        else:
            st.markdown(f"""<div class="ft-header"><div class="ft-title">🚀 FAST TRACK</div></div>""", unsafe_allow_html=True)
            prog = min(1.0, (p.fast_track_cf - p.ft_initial_cf) / 500000)
            st.progress(prog, f"เป้าหมาย +500,000 ({p.fast_track_cf:,.0f})")
            if p.fast_track_cf >= p.ft_initial_cf + 500000: st.balloons(); st.success("WINNER!"); st.stop()
            
            st.markdown("### ⚡ ทำรายการ")
            with st.container():
                st.markdown('<div class="input-area">', unsafe_allow_html=True)
                ft = st.selectbox("รายการ", TX_FAST_TRACK)
                if "Cash Flow" in ft:
                    if st.button("💰 รับเงิน"): p.ft_payday(); st.success("เรียบร้อย"); st.rerun()
                elif "ซื้อกิจการ" in ft:
                    c1,c2,c3 = st.columns(3); n=c1.text_input("ชื่อ"); co=c2.number_input("ลงทุน",0,step=100000); cf=c3.number_input("CF",0,step=10000)
                    if st.button("ลงทุน"): ok,m=p.ft_buy(n,co,cf); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "บริจาค" in ft:
                    if st.button("บริจาค 1M"): ok,m=p.ft_charity(); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                elif "ถูกฟ้อง" in ft or "ตรวจสอบ" in ft:
                    if st.button("จ่าย"): m=p.ft_bad_event("Bad Luck"); st.error(m); st.rerun()
                elif "หย่า" in ft:
                    if st.button("จ่าย"): m=p.ft_bad_event("หย่า"); st.error(m); st.rerun()
                elif "ซื้อความสุข" in ft:
                    n=st.text_input("รายการ"); c=st.number_input("ราคา",0,step=10000)
                    if st.button("จ่าย"): ok,m=p.expense_event(n,c); (st.success(m) if ok else st.error(m)) and st.rerun() if ok else None
                st.markdown('</div>', unsafe_allow_html=True)

    # ================= DASHBOARD =================
    elif menu == "📊 ดูภาพรวม (Dashboard)":
        st.title("📊 สรุปสถานะผู้เล่นทุกคน")
        
        for i, pl in enumerate(st.session_state.players):
            st.markdown(f"### 👤 {pl.name} ({pl.job})")
            
            # [UPDATED] Show 4-Box Summary like Action Screen
            st.markdown(f"""
            <div class="dashboard-container">
                <div class="dash-box box-passive"><div class="dash-label">รายได้ทรัพย์สิน</div><div class="dash-value txt-passive">{pl.passive_income:,.0f}</div></div>
                <div class="dash-box box-total-inc"><div class="dash-label">รายรับรวม</div><div class="dash-value txt-inc">{pl.total_income:,.0f}</div></div>
                <div class="dash-box box-expense"><div class="dash-label">รายจ่ายรวม</div><div class="dash-value txt-exp">{pl.total_expenses:,.0f}</div></div>
                <div class="dash-box box-flow"><div class="dash-label">Cashflow</div><div class="dash-value txt-flow">{pl.monthly_cashflow:,.0f}</div></div>
            </div>
            """, unsafe_allow_html=True)

            c_left, c_mid, c_right = st.columns([1, 1, 1])
            
            with c_left:
                st.markdown('<div class="header-blue">หนี้สิน (Liabilities)</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(list(pl.liabilities.items()), columns=['รายการ', 'คงเหลือ']), hide_index=True, use_container_width=True)

            with c_mid:
                st.markdown('<div class="header-orange">เงินสด & หุ้น</div>', unsafe_allow_html=True)
                st.markdown(f"""<div class="stat-card"><h3>เงินสดคงเหลือ</h3><h1>{pl.cash:,}</h1></div>""", unsafe_allow_html=True)
                if pl.stocks:
                    df_s = pd.DataFrame([{"หุ้น":s['symbol'], "จำนวน":s['qty'], "ทุน":s['cost'], "ราคาล่าสุด":s.get('last_price', s['cost'])} for s in pl.stocks])
                    st.dataframe(df_s, hide_index=True, use_container_width=True)
                else: st.info("ไม่มีหุ้น")

            with c_right:
                st.markdown('<div class="header-green">ทรัพย์สิน (Assets)</div>', unsafe_allow_html=True)
                if pl.assets:
                    df_a = pd.DataFrame(pl.assets)
                    cols = ['รายการ', 'Cashflow']
                    if 'หนี้' in df_a.columns: cols.append('หนี้')
                    st.dataframe(df_a[cols], hide_index=True, use_container_width=True)
                else: st.info("ไม่มีอสังหาฯ")
            
            st.divider()
