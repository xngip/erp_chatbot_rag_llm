import re
from datetime import datetime

from app.erp_tools.modules.hrm.tools import (
    get_employee_profile,
    get_employee_department,
    get_employee_position,
    get_today_attendance,
    get_attendance_history,
    get_late_ot_summary,
    get_work_shift,
    get_labor_contract,
    get_payslip,
    get_payslip_detail,
    get_salary_history
)

# =====================================================
# ENTITY
# =====================================================
def extract_month_year(text: str):
    month = None
    year = datetime.now().year

    m = re.search(r"tháng\s*(\d{1,2})", text.lower())
    y = re.search(r"năm\s*(\d{4})", text.lower())

    if m:
        month = int(m.group(1))
    if y:
        year = int(y.group(1))

    return month, year


# =====================================================
# RULE
# =====================================================
def hrm_router(
    query: str,
    employee_id: int = 1
):
    q = query.lower()

    # 1️ HỒ SƠ
    if "hồ sơ" in q or "thông tin nhân viên" in q:
        return get_employee_profile(employee_id)

    # 2️ PHÒNG BAN
    if "phòng" in q:
        return get_employee_department(employee_id)

    # 3️ CHỨC VỤ
    if "chức vụ" in q or "vị trí" in q:
        return get_employee_position(employee_id)

    # 4️ CHẤM CÔNG HÔM NAY
    if "hôm nay" in q or "check in" in q:
        return get_today_attendance(employee_id)

    # 5️ LỊCH SỬ CHẤM CÔNG
    if "lịch sử chấm công" in q:
        return get_attendance_history(employee_id)

    # 6️ ĐI MUỘN / OT
    if "đi muộn" in q or "tăng ca" in q or "ot" in q:
        month, year = extract_month_year(q)
        if month:
            return get_late_ot_summary(employee_id, month, year)

    # 7️ CA LÀM
    if "ca làm" in q:
        return get_work_shift(employee_id)

    # 8️ HỢP ĐỒNG
    if "hợp đồng" in q:
        return get_labor_contract(employee_id)

    # 9️ LƯƠNG
    if "lịch sử lương" in q:
        return get_salary_history(employee_id)

    if "chi tiết lương" in q:
        month, year = extract_month_year(q)
        if month:
            payslip = get_payslip(employee_id, month, year)
            if payslip and isinstance(payslip, dict):
                return {
                    "summary": payslip,
                    "details": get_payslip_detail(payslip["id"])
                }

    if "lương" in q:
        month, year = extract_month_year(q)
        if month:
            return get_payslip(employee_id, month, year)

    return None
