from datetime import date
from sqlalchemy import func
from app.db.hrm_database import HrmSessionLocal

from app.erp_tools.modules.hrm.models import (
    Employee,
    Department,
    Position,
    WorkShift,
    AttendanceLog,
    TimesheetDaily,
    LaborContract,
    PayrollPeriod,
    Payslip,
    PayslipDetail,
    SalaryRule
)

# =====================================================
# 1. HỒ SƠ NHÂN VIÊN
# =====================================================
def get_employee_profile(employee_id: int):
    db = HrmSessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            return {"message": "Không tìm thấy nhân viên"}

        return {
            "employee_code": emp.employee_code,
            "full_name": emp.full_name,
            "phone": emp.phone,
            "email_company": emp.email_company,
            "status": emp.status,
            "join_date": emp.join_date,
        }
    finally:
        db.close()


# =====================================================
# 2. PHÒNG BAN
# =====================================================
def get_employee_department(employee_id: int):
    db = HrmSessionLocal()
    try:
        row = (
            db.query(Employee, Department)
            .join(Department, Employee.department_id == Department.id)
            .filter(Employee.id == employee_id)
            .first()
        )
        if not row:
            return {"message": "Không có thông tin phòng ban"}

        _, dept = row
        return {
            "department_code": dept.code,
            "department_name": dept.name,
            "description": dept.description
        }
    finally:
        db.close()


# =====================================================
# 3. CHỨC VỤ
# =====================================================
def get_employee_position(employee_id: int):
    db = HrmSessionLocal()
    try:
        row = (
            db.query(Employee, Position)
            .join(Position, Employee.position_id == Position.id)
            .filter(Employee.id == employee_id)
            .first()
        )
        if not row:
            return {"message": "Không có thông tin chức vụ"}

        _, pos = row
        return {
            "position_title": pos.title,
            "salary_range": {
                "min": float(pos.base_salary_range_min) if pos.base_salary_range_min else None,
                "max": float(pos.base_salary_range_max) if pos.base_salary_range_max else None,
            }
        }
    finally:
        db.close()


# =====================================================
# 4. CHẤM CÔNG HÔM NAY
# =====================================================
def get_today_attendance(employee_id: int):
    db = HrmSessionLocal()
    today = date.today()

    try:
        row = (
            db.query(TimesheetDaily)
            .filter(
                TimesheetDaily.employee_id == employee_id,
                TimesheetDaily.date == today
            )
            .first()
        )

        if not row:
            return {"message": "Hôm nay chưa có dữ liệu chấm công"}

        return {
            "date": today,
            "check_in": row.check_in_time,
            "check_out": row.check_out_time,
            "late_minutes": row.late_minutes,
            "ot_hours": row.ot_hours
        }
    finally:
        db.close()


# =====================================================
# 5. LỊCH SỬ CHẤM CÔNG
# =====================================================
def get_attendance_history(employee_id: int, limit: int = 10):
    db = HrmSessionLocal()
    try:
        rows = (
            db.query(TimesheetDaily)
            .filter(TimesheetDaily.employee_id == employee_id)
            .order_by(TimesheetDaily.date.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "date": r.date,
                "check_in": r.check_in_time,
                "check_out": r.check_out_time,
                "status": r.status
            }
            for r in rows
        ]
    finally:
        db.close()


# =====================================================
# 6. ĐI MUỘN / OT THEO THÁNG
# =====================================================
def get_late_ot_summary(employee_id: int, month: int, year: int):
    db = HrmSessionLocal()
    try:
        rows = (
            db.query(
                func.sum(TimesheetDaily.late_minutes),
                func.sum(TimesheetDaily.ot_hours)
            )
            .filter(
                TimesheetDaily.employee_id == employee_id,
                func.extract("month", TimesheetDaily.date) == month,
                func.extract("year", TimesheetDaily.date) == year
            )
            .first()
        )

        return {
            "month": month,
            "year": year,
            "total_late_minutes": rows[0] or 0,
            "total_ot_hours": float(rows[1] or 0)
        }
    finally:
        db.close()


# =====================================================
# 7. CA LÀM VIỆC
# =====================================================
def get_work_shift(employee_id: int):
    return {
        "message": "Nhân viên chưa được gán ca làm việc cố định"
    }


# =====================================================
# 8. HỢP ĐỒNG LAO ĐỘNG
# =====================================================
def get_labor_contract(employee_id: int):
    db = HrmSessionLocal()
    try:
        c = (
            db.query(LaborContract)
            .filter(LaborContract.employee_id == employee_id)
            .order_by(LaborContract.start_date.desc())
            .first()
        )

        if not c:
            return {"message": "Không có hợp đồng lao động"}

        return {
            "contract_number": c.contract_number,
            "contract_type": c.contract_type,
            "start_date": c.start_date,
            "end_date": c.end_date,
            "basic_salary": float(c.basic_salary),
            "status": c.status
        }
    finally:
        db.close()


# =====================================================
# 9. BẢNG LƯƠNG THÁNG
# =====================================================
def get_payslip(employee_id: int, month: int, year: int):
    db = HrmSessionLocal()
    try:
        row = (
            db.query(Payslip, PayrollPeriod)
            .join(PayrollPeriod, Payslip.payroll_period_id == PayrollPeriod.id)
            .filter(
                Payslip.employee_id == employee_id,
                PayrollPeriod.month == month,
                PayrollPeriod.year == year
            )
            .first()
        )

        if not row:
            return {"message": "Chưa có bảng lương tháng này"}

        p, period = row
        return {
            "month": period.month,
            "year": period.year,
            "gross_salary": float(p.gross_salary),
            "net_salary": float(p.net_salary),
            "status": p.status
        }
    finally:
        db.close()


# =====================================================
# 10. CHI TIẾT LƯƠNG
# =====================================================
def get_payslip_detail(payslip_id: int):
    db = HrmSessionLocal()
    try:
        rows = (
            db.query(PayslipDetail, SalaryRule)
            .join(SalaryRule, PayslipDetail.salary_rule_id == SalaryRule.id)
            .filter(PayslipDetail.payslip_id == payslip_id)
            .all()
        )

        return [
            {
                "rule_name": r.name,
                "rule_type": r.type,
                "amount": float(d.amount)
            }
            for d, r in rows
        ]
    finally:
        db.close()


# =====================================================
# 11. LỊCH SỬ LƯƠNG
# =====================================================
def get_salary_history(employee_id: int, limit: int = 6):
    db = HrmSessionLocal()
    try:
        rows = (
            db.query(Payslip, PayrollPeriod)
            .join(PayrollPeriod, Payslip.payroll_period_id == PayrollPeriod.id)
            .filter(Payslip.employee_id == employee_id)
            .order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "month": period.month,
                "year": period.year,
                "net_salary": float(p.net_salary)
            }
            for p, period in rows
        ]
    finally:
        db.close()
