import sys
import os
from datetime import date, datetime, time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.db.hrm_database import HrmSessionLocal
from app.erp_tools.modules.hrm.models import (
    Department, Position, Employee,
    WorkShift, TimesheetDaily, AttendanceLog,
    LaborContract, PayrollPeriod,
    Payslip, PayslipDetail, SalaryRule
)

def main():
    db = HrmSessionLocal()

    try:
        # =========================
        # DEPARTMENT
        # =========================
        dep_it = Department(code="IT", name="Công nghệ thông tin")
        dep_hr = Department(code="HR", name="Nhân sự")
        db.add_all([dep_it, dep_hr])
        db.commit()

        # =========================
        # POSITION
        # =========================
        pos_dev = Position(
            title="Backend Developer",
            base_salary_range_min=15000000,
            base_salary_range_max=30000000
        )
        pos_hr = Position(
            title="HR Executive",
            base_salary_range_min=10000000,
            base_salary_range_max=20000000
        )
        db.add_all([pos_dev, pos_hr])
        db.commit()

        # =========================
        # EMPLOYEE
        # =========================
        emp1 = Employee(
            user_id=1,
            employee_code="EMP001",
            full_name="Nguyễn Văn A",
            department_id=dep_it.id,
            position_id=pos_dev.id,
            gender="MALE",
            phone="090000001",
            email_company="a.nguyen@company.com",
            status="ACTIVE",
            join_date=date(2023, 1, 10)
        )

        emp2 = Employee(
            user_id=2,
            employee_code="EMP002",
            full_name="Trần Thị B",
            department_id=dep_hr.id,
            position_id=pos_hr.id,
            gender="FEMALE",
            phone="090000002",
            email_company="b.tran@company.com",
            status="ACTIVE",
            join_date=date(2023, 3, 1)
        )

        db.add_all([emp1, emp2])
        db.commit()

        # =========================
        # WORK SHIFT
        # =========================
        shift_day = WorkShift(
            shift_name="Hành chính",
            start_time=time(8, 0),
            end_time=time(17, 0),
            break_start_time=time(12, 0),
            break_end_time=time(13, 0)
        )
        db.add(shift_day)
        db.commit()

        # =========================
        # TIMESHEET DAILY
        # =========================
        ts1 = TimesheetDaily(
            employee_id=emp1.id,
            date=date.today(),
            work_shift_id=shift_day.id,
            check_in_time=time(8, 5),
            check_out_time=time(17, 0),
            late_minutes=5,
            ot_hours=1.5,
            status="PRESENT",
            working_day_count=1
        )
        db.add(ts1)
        db.commit()

        # =========================
        # ATTENDANCE LOG
        # =========================
        log1 = AttendanceLog(
            employee_id=emp1.id,
            check_time=datetime.now(),
            confidence_score=0.98,
            device_id="CAM01"
        )
        db.add(log1)
        db.commit()

        # =========================
        # LABOR CONTRACT
        # =========================
        contract = LaborContract(
            employee_id=emp1.id,
            contract_number="HD001",
            contract_type="FIXED",
            start_date=date(2023, 1, 10),
            end_date=date(2025, 1, 10),
            basic_salary=20000000,
            status="ACTIVE"
        )
        db.add(contract)
        db.commit()

        # =========================
        # PAYROLL
        # =========================
        period = PayrollPeriod(
            name="Tháng 12/2025",
            month=12,
            year=2025,
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 31),
            standard_working_days=22,
            status="CLOSED"
        )
        db.add(period)
        db.commit()

        payslip = Payslip(
            payroll_period_id=period.id,
            employee_id=emp1.id,
            total_working_days=22,
            total_ot_hours=10,
            gross_salary=25000000,
            total_deduction=2000000,
            net_salary=23000000,
            status="FINAL"
        )
        db.add(payslip)
        db.commit()

        # =========================
        # SALARY RULE
        # =========================
        rule_basic = SalaryRule(
            code="BASIC",
            name="Lương cơ bản",
            type="ALLOWANCE",
            formula="BASE_SALARY"
        )
        rule_tax = SalaryRule(
            code="TAX",
            name="Thuế TNCN",
            type="DEDUCTION",
            formula="10%"
        )
        db.add_all([rule_basic, rule_tax])
        db.commit()

        # =========================
        # PAYSLIP DETAIL
        # =========================
        detail1 = PayslipDetail(
            payslip_id=payslip.id,
            salary_rule_id=rule_basic.id,
            amount=20000000
        )
        detail2 = PayslipDetail(
            payslip_id=payslip.id,
            salary_rule_id=rule_tax.id,
            amount=2000000
        )
        db.add_all([detail1, detail2])
        db.commit()

        print("✅ HRM seed data inserted successfully.")

    except Exception as e:
        db.rollback()
        print("❌ Seed error:", e)

    finally:
        db.close()

if __name__ == "__main__":
    main()
