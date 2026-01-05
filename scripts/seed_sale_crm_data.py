from datetime import datetime, timedelta
from decimal import Decimal

from app.db.sale_crm_database import SaleCrmSessionLocal
from app.erp_tools.modules.sales_crm.models import (
    Role, User, Address,
    Brand, Product, ProductVariant,
    Payment, Order, OrderDetail,
    Review, ImgReview,
    Voucher, VoucherDetail, VoucherConstraint
)

def seed_sale_crm():
    db = SaleCrmSessionLocal()
    try:
        # ======================
        # ROLE
        # ======================
        customer_role = Role(role_name="customer")
        staff_role = Role(role_name="staff")
        db.add_all([customer_role, staff_role])
        db.commit()

        # ======================
        # USER
        # ======================
        users = [
            User(
                role_id=customer_role.id,
                username=f"user{i}",
                email=f"user{i}@mail.com",
                phone=f"09000000{i}",
                password="hashed_password"
            )
            for i in range(1, 6)
        ]
        db.add_all(users)
        db.commit()

        # ======================
        # ADDRESS
        # ======================
        addresses = [
            Address(
                user_id=users[i].id,
                city="Hà Nội",
                district="Cầu Giấy",
                ward="Dịch Vọng",
                street_address=f"Số {i+1} Trần Thái Tông",
                is_default=True
            )
            for i in range(5)
        ]
        db.add_all(addresses)
        db.commit()

        # ======================
        # BRAND
        # ======================
        brands = [
            Brand(name="Apple", description="Thiết bị Apple"),
            Brand(name="Samsung", description="Thiết bị Samsung"),
            Brand(name="Xiaomi", description="Thiết bị Xiaomi"),
            Brand(name="Sony", description="Thiết bị Sony"),
            Brand(name="Dell", description="Laptop Dell"),
        ]
        db.add_all(brands)
        db.commit()

        # ======================
        # PRODUCT
        # ======================
        products = [
            Product(
                brand_id=brands[i].id,
                name=f"Sản phẩm {i+1}",
                description="Sản phẩm demo",
                avg_rating=Decimal("4.5"),
                total_sold=10 * (i + 1),
                total_stock=100,
                is_active=True
            )
            for i in range(5)
        ]
        db.add_all(products)
        db.commit()

        # ======================
        # PRODUCT VARIANT
        # ======================
        variants = []
        for p in products:
            for j in range(2):
                variants.append(
                    ProductVariant(
                        product_id=p.id,
                        name=f"{p.name} - Bản {j+1}",
                        stock=50,
                        sold=10,
                        original_price=Decimal("10000000"),
                        discount_amount=Decimal("500000"),
                        discount_percent=Decimal("5")
                    )
                )
        db.add_all(variants)
        db.commit()

        # ======================
        # PAYMENT
        # ======================
        payments = [
            Payment(
                amount=Decimal("15000000"),
                payment_status="PAID",
                payment_method="COD",
                transaction_id=f"TXN{i}"
            )
            for i in range(1, 6)
        ]
        db.add_all(payments)
        db.commit()

        # ======================
        # ORDER
        # ======================
        orders = [
            Order(
                user_id=users[i].id,
                payment_id=payments[i].id,
                order_status="Đang xử lý" if i % 2 == 0 else "Đã giao",
                payment_method="COD",
                shipping_address=addresses[i].street_address
            )
            for i in range(5)
        ]
        db.add_all(orders)
        db.commit()

        # ======================
        # ORDER DETAIL
        # ======================
        order_details = []
        for o in orders:
            order_details.append(
                OrderDetail(
                    order_id=o.id,
                    product_variant_id=variants[0].id,
                    quantity=1,
                    price=Decimal("14500000")
                )
            )
        db.add_all(order_details)
        db.commit()

        # ======================
        # REVIEW
        # ======================
        reviews = [
            Review(
                product_id=products[i].id,
                user_id=users[i].id,
                content="Sản phẩm rất tốt",
                rating=5
            )
            for i in range(5)
        ]
        db.add_all(reviews)
        db.commit()

        # ======================
        # IMG REVIEW
        # ======================
        img_reviews = [
            ImgReview(
                review_id=reviews[i].id,
                image_url=f"https://img.demo/review_{i}.jpg"
            )
            for i in range(5)
        ]
        db.add_all(img_reviews)
        db.commit()

        # ======================
        # VOUCHER
        # ======================
        voucher = Voucher(
            name="SALE10",
            description="Giảm 10%",
            discount_type="PERCENT",
            discount_value=Decimal("10"),
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        db.add(voucher)
        db.commit()

        voucher_detail = VoucherDetail(
            voucher_id=voucher.id,
            code="SALE10",
            usage_limit=100,
            used_count=0,
            is_active=True
        )
        db.add(voucher_detail)

        voucher_constraint = VoucherConstraint(
            voucher_id=voucher.id,
            min_order_amount=Decimal("1000000"),
            max_discount_amount=Decimal("2000000"),
            is_new_customer_only=False
        )
        db.add(voucher_constraint)
        db.commit()

        print("✅ Seed dữ liệu Sale & CRM thành công!")

    except Exception as e:
        db.rollback()
        print("❌ Lỗi seed dữ liệu:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_sale_crm()
