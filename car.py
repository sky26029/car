import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path

# 頁面設定
st.set_page_config(page_title="汽車客戶資料表", layout="wide")
st.title("🚗 汽車客戶資料管理系統")

# Excel 存檔路徑（固定名稱）
desktop = Path.home() / "Desktop"
excel_path = desktop / "汽車客戶資料.xlsx"

# 嘗試讀取現有資料
@st.cache_data(ttl=300)
def load_data():
    if excel_path.exists():
        try:
            df = pd.read_excel(excel_path)
            return df
        except Exception as e:
            st.error(f"讀取資料失敗: {e}")
    # 沒檔案回傳空表
    return pd.DataFrame(columns=[
        "姓名", "電話", "車牌", "車型", "本次保養日期", "本次里程",
        "下次保養日期", "下次保養里程", "維修明細", "總金額", "備註"
    ])

# 載入資料
if "customers" not in st.session_state:
    st.session_state.customers = load_data()

# 儲存函式（覆寫檔案）
def save_data(df):
    try:
        df.to_excel(excel_path, index=False)
        st.success(f"📁 資料已儲存到桌面：{excel_path}")
    except Exception as e:
        st.error(f"儲存資料失敗: {e}")

# ===== 新增客戶表單 =====
with st.expander("➕ 新增客戶資料"):
    with st.form("new_customer_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("姓名")
        phone = col2.text_input("電話")
        plate = col3.text_input("車牌")
        model = col1.text_input("車型")
        note = col2.text_input("備註")

        # 本次保養日期
        today = datetime.today()
        service_date = col3.date_input("本次保養日期", value=today)

        # 本次里程
        mileage = col1.number_input("本次里程 (公里)", min_value=0, step=1)

        # 下次保養日期與里程
        next_service_date = service_date + relativedelta(months=6)
        next_mileage = mileage + 5000

        st.markdown(f"**下次保養日期：** {next_service_date.strftime('%Y-%m-%d')}")
        st.markdown(f"**下次保養里程：** {next_mileage} 公里")

        # 維修項目與價錢（最多 20 筆）
        st.markdown("### 🛠 維修項目與價錢（最多 20 筆）")
        repairs = []
        total_price = 0

        for i in range(1, 21):
            c1, c2 = st.columns([2, 1])
            item = c1.text_input(f"項目 {i}", key=f"item_{i}")
            price = c2.number_input(f"價錢 {i}", min_value=0, step=100, key=f"price_{i}")
            if item.strip() != "":
                repairs.append(f"{item} (${price})")
                total_price += price

        submit = st.form_submit_button("新增資料")
        if submit:
            if name.strip() and plate.strip():
                new_row = {
                    "姓名": name.strip(),
                    "電話": phone.strip(),
                    "車牌": plate.strip(),
                    "車型": model.strip(),
                    "本次保養日期": service_date.strftime("%Y-%m-%d"),
                    "本次里程": mileage,
                    "下次保養日期": next_service_date.strftime("%Y-%m-%d"),
                    "下次保養里程": next_mileage,
                    "維修明細": ", ".join(repairs),
                    "總金額": total_price,
                    "備註": note.strip()
                }
                st.session_state.customers = pd.concat(
                    [st.session_state.customers, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                save_data(st.session_state.customers)
                st.success("✅ 客戶資料已新增")
            else:
                st.warning("⚠️ 請至少輸入『姓名』與『車牌』")

# ===== 搜尋功能 =====
search_keyword = st.text_input("🔍 搜尋姓名、車牌或維修項目：")

if search_keyword.strip():
    df_filtered = st.session_state.customers[
        st.session_state.customers["姓名"].str.contains(search_keyword, case=False, na=False) |
        st.session_state.customers["車牌"].str.contains(search_keyword, case=False, na=False) |
        st.session_state.customers["維修明細"].str.contains(search_keyword, case=False, na=False)
    ]
else:
    df_filtered = st.session_state.customers

# ===== 顯示表格 =====
st.subheader("📋 客戶資料列表")
if df_filtered.empty:
    st.info("目前沒有符合條件的資料。")
else:
    st.dataframe(df_filtered, use_container_width=True)

    st.markdown("### ✏️ 編輯或 🗑 刪除客戶資料")
    for i, row in df_filtered.iterrows():
        with st.expander(f"🧾 {row['姓名']}（{row['車牌']}）"):
            edit_col1, edit_col2, edit_col3 = st.columns(3)
            new_name = edit_col1.text_input("姓名", value=row["姓名"], key=f"name_{i}")
            new_phone = edit_col2.text_input("電話", value=row["電話"], key=f"phone_{i}")
            new_plate = edit_col3.text_input("車牌", value=row["車牌"], key=f"plate_{i}")
            new_model = edit_col1.text_input("車型", value=row["車型"], key=f"model_{i}")
            new_note = edit_col2.text_input("備註", value=row["備註"], key=f"note_{i}")
            new_service_date = edit_col3.date_input("本次保養日期", value=pd.to_datetime(row["本次保養日期"]), key=f"service_date_{i}")
            new_mileage = edit_col1.number_input("本次里程", value=int(row["本次里程"]), step=100, key=f"mileage_{i}")

            # 自動計算下次日期與里程
            next_service_date = new_service_date + relativedelta(months=6)
            next_mileage = new_mileage + 5000
            st.markdown(f"**下次保養日期：** {next_service_date.strftime('%Y-%m-%d')}")
            st.markdown(f"**下次保養里程：** {next_mileage} 公里")

            # 維修明細和金額
            new_repairs = st.text_area("維修明細 (格式：項目 ($金額), 用逗號分隔)", value=row["維修明細"], key=f"repairs_{i}")
            new_total = st.number_input("總金額", value=int(row["總金額"]), step=100, key=f"total_{i}")

            col_save, col_delete = st.columns(2)
            if col_save.button("💾 儲存修改", key=f"save_{i}"):
                st.session_state.customers.loc[i] = {
                    "姓名": new_name.strip(),
                    "電話": new_phone.strip(),
                    "車牌": new_plate.strip(),
                    "車型": new_model.strip(),
                    "本次保養日期": new_service_date.strftime("%Y-%m-%d"),
                    "本次里程": new_mileage,
                    "下次保養日期": next_service_date.strftime("%Y-%m-%d"),
                    "下次保養里程": next_mileage,
                    "維修明細": new_repairs.strip(),
                    "總金額": new_total,
                    "備註": new_note.strip()
                }
                save_data(st.session_state.customers)
                st.success(f"✅ 資料已更新：{new_name}（{new_plate}）")

            if col_delete.button("🗑 刪除此筆資料", key=f"delete_{i}"):
                st.session_state.customers.drop(i, inplace=True)
                st.session_state.customers.reset_index(drop=True, inplace=True)
                save_data(st.session_state.customers)
                st.warning(f"🗑 資料已刪除：{row['姓名']}（{row['車牌']}）")
                st.experimental_rerun()
