import random
from sqlmodel import Session
from db import engine
from models import Customer, Plan, CustomerPlan, Transaction, StatusEnum

# -----------------------------
# Datos base
# -----------------------------
names = [
    "Carlos", "Ana", "Luis", "Maria", "Pedro",
    "Sofia", "Jorge", "Lucia", "Miguel", "Elena"
]

descriptions = [
    "Compra en tienda",
    "Pago de servicio",
    "Transferencia",
    "Suscripción",
    "Pago en línea",
    "Compra de producto",
    "Recarga",
    "Pago mensual"
]

plan_names = [
    ("Basic", 100),
    ("Standard", 200),
    ("Premium", 300),
    ("VIP", 500)
]

# -----------------------------
# Seed function
# -----------------------------
def seed():
    with Session(engine) as session:

        print("🚀 Iniciando seed...")

        # -----------------------------
        # 1. Crear Customers
        # -----------------------------
        customers = []
        for i in range(10):
            customer = Customer(
                name=names[i],
                email=f"user{i}@test.com",
                age=random.randint(18, 60),
                description="Usuario generado automáticamente"
            )
            customers.append(customer)

        session.add_all(customers)
        session.commit()

        for c in customers:
            session.refresh(c)

        print("✅ Customers creados")

        # -----------------------------
        # 2. Crear Plans
        # -----------------------------
        plans = []
        for name, price in plan_names:
            plan = Plan(
                name=name,
                price=price,
                description=f"Plan {name}"
            )
            plans.append(plan)

        session.add_all(plans)
        session.commit()

        for p in plans:
            session.refresh(p)

        print("✅ Plans creados")

        # -----------------------------
        # 3. Asignar planes a customers
        # -----------------------------
        customer_plans = []

        for customer in customers:
            num_plans = random.choice([1, 2])
            selected_plans = random.sample(plans, num_plans)

            if num_plans == 1:
                cp = CustomerPlan(
                    customer_id=customer.id,
                    plan_id=selected_plans[0].id,
                    status=StatusEnum.ACTIVE
                )
                customer_plans.append(cp)

            else:
                cp_active = CustomerPlan(
                    customer_id=customer.id,
                    plan_id=selected_plans[0].id,
                    status=StatusEnum.ACTIVE
                )
                cp_inactive = CustomerPlan(
                    customer_id=customer.id,
                    plan_id=selected_plans[1].id,
                    status=StatusEnum.INACTIVE
                )
                customer_plans.extend([cp_active, cp_inactive])

        session.add_all(customer_plans)
        session.commit()

        print("✅ Planes asignados a customers")

        # -----------------------------
        # 4. Crear Transactions
        # -----------------------------
        transactions = []

        for _ in range(100):
            transaction = Transaction(
                amount=random.randint(10, 1000),
                description=random.choice(descriptions),
                customer_id=random.choice(customers).id
            )
            transactions.append(transaction)

        session.add_all(transactions)
        session.commit()

        print("✅ 100 transacciones creadas")

        print("🎉 Seed completado con éxito")


# -----------------------------
# Ejecutar
# -----------------------------
if __name__ == "__main__":
    seed()