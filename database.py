from sqlalchemy import create_engine, event, Column, Integer, String, Float, Date, Text, CheckConstraint, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from datetime import date

DATABASE_URL = "sqlite:///shop_app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

@event.listens_for(engine, "connect")
def _set_pragmas(dbapi_conn, _record):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA foreign_keys=ON;")
    cur.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

JOB_TYPES = ["Full Wrap", "Partial Wrap", "Decals", "Signage", "PPF", "Tint", "Other"]
STATUS_OPTIONS = ["Pending", "In Progress", "Completed", "Invoiced", "Paid"]

FOIL_BRANDS = {
    "Oracal": ["651", "970RA", "975", "Vinyl Cast"],
    "3M": ["1080", "2080", "Scotchprint"],
    "Avery": ["SW900", "Dennison"],
    "Hexis": ["Skintac", "Bodyfence"],
    "Arlon": ["3000", "SLX"],
}


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer,     primary_key=True, autoincrement=True)
    name        = Column(String(200), nullable=False)
    phone       = Column(String(50),  nullable=True)
    email       = Column(String(200), nullable=True)

    jobs = relationship("Job", back_populates="customer", foreign_keys="Job.customer_id")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("charge >= 0",            name="ck_job_charge"),
        CheckConstraint("labour_cost >= 0",        name="ck_job_labour"),
        CheckConstraint("material_cost >= 0",      name="ck_job_material"),
        CheckConstraint("subcontractor_cost >= 0", name="ck_job_sub"),
    )

    job_id             = Column(Integer, primary_key=True, autoincrement=True)
    date               = Column(Date,        nullable=False)
    customer_name      = Column(String(200), nullable=False)
    job_type           = Column(String(50),  nullable=False)
    status             = Column(String(20),  nullable=False, default="Pending")
    charge             = Column(Float,       nullable=False, default=0.0)
    labour_cost        = Column(Float,       nullable=False, default=0.0)
    material_cost      = Column(Float,       nullable=False, default=0.0)
    subcontractor_cost = Column(Float,       nullable=False, default=0.0)
    notes              = Column(Text,        nullable=True)
    customer_id        = Column(Integer,     ForeignKey("customers.customer_id", ondelete="SET NULL"), nullable=True)

    customer = relationship("Customer", back_populates="jobs", foreign_keys=[customer_id])

    @property
    def total_cost(self):
        return round(self.labour_cost + self.material_cost + self.subcontractor_cost, 2)

    @property
    def gross_profit(self):
        return round(self.charge - self.total_cost, 2)

    @property
    def margin_pct(self):
        if not self.charge:
            return 0.0
        return round(self.gross_profit / self.charge * 100, 2)


class FoilType(Base):
    __tablename__ = "foil_types"
    __table_args__ = (
        CheckConstraint("unit_weight > 0",  name="ck_unit_weight_positive"),
        CheckConstraint("core_weight >= 0", name="ck_core_weight_non_negative"),
    )

    foil_type_id  = Column(Integer,     primary_key=True, autoincrement=True)
    material_name = Column(String(200), nullable=False, unique=True)
    core_weight   = Column(Float,       nullable=False)
    unit_weight   = Column(Float,       nullable=False)
    created_at    = Column(Date,        nullable=False, default=date.today)
    notes         = Column(Text,        nullable=True)

    rolls = relationship("FoilRoll", back_populates="foil_type", cascade="all, delete-orphan")


class FoilRoll(Base):
    __tablename__ = "foil_rolls"
    __table_args__ = (
        CheckConstraint("current_total_weight >= 0", name="ck_total_weight_non_negative"),
    )

    roll_id              = Column(Integer,     primary_key=True, autoincrement=True)
    foil_type_id         = Column(Integer,     ForeignKey("foil_types.foil_type_id", ondelete="RESTRICT"), nullable=False)
    roll_label           = Column(String(100), nullable=True)
    current_total_weight = Column(Float,       nullable=False)
    calculated_length    = Column(Float,       nullable=False)
    last_checked         = Column(Date,        nullable=False, default=date.today)
    notes                = Column(Text,        nullable=True)

    foil_type = relationship("FoilType", back_populates="rolls")


def run_migrations():
    from sqlalchemy import inspect as sa_inspect
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name        VARCHAR(200) NOT NULL,
                phone       VARCHAR(50),
                email       VARCHAR(200)
            )
        """))
        inspector = sa_inspect(conn)
        existing_cols = [c["name"] for c in inspector.get_columns("jobs")]
        if "customer_id" not in existing_cols:
            conn.execute(text(
                "ALTER TABLE jobs ADD COLUMN customer_id INTEGER REFERENCES customers(customer_id)"
            ))


def init_db():
    Base.metadata.create_all(bind=engine)
    run_migrations()
    print("Database ready.")

if __name__ == "__main__":
    init_db()


def _calculate_length(total_weight, core_weight, unit_weight):
    if unit_weight <= 0:
        raise ValueError("Unit weight must be greater than 0.")
    net = total_weight - core_weight
    if net < 0:
        raise ValueError(f"Total weight ({total_weight}g) is less than core weight ({core_weight}g).")
    return round(net / unit_weight, 4)


def create_job(job_date, customer_name, job_type, charge,
               labour_cost=0.0, material_cost=0.0,
               subcontractor_cost=0.0, status="Pending", notes=None,
               customer_id=None):
    with SessionLocal() as session:
        if customer_id is not None:
            c = session.get(Customer, customer_id)
            if c is None:
                raise ValueError(f"Customer {customer_id} not found.")
            resolved_name = c.name
        else:
            resolved_name = customer_name.strip() if customer_name else ""
        job = Job(
            date=job_date,
            customer_name=resolved_name,
            customer_id=customer_id,
            job_type=job_type,
            status=status,
            charge=float(charge),
            labour_cost=float(labour_cost),
            material_cost=float(material_cost),
            subcontractor_cost=float(subcontractor_cost),
            notes=notes,
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        return job


def read_all_jobs():
    with SessionLocal() as session:
        rows = session.query(Job).order_by(Job.date.desc()).all()
        return [
            {
                "Job_ID":             r.job_id,
                "Date":               r.date,
                "Customer_ID":        r.customer_id,
                "Customer":           r.customer_name,
                "Job_Type":           r.job_type,
                "Status":             r.status,
                "Charge":             r.charge,
                "Labour_Cost":        r.labour_cost,
                "Material_Cost":      r.material_cost,
                "Subcontractor_Cost": r.subcontractor_cost,
                "Total_Cost":         r.total_cost,
                "Gross_Profit":       r.gross_profit,
                "Margin_Pct":         r.margin_pct,
                "Notes":              r.notes,
            }
            for r in rows
        ]


def update_job(job_id, job_date=None, customer_name=None, job_type=None,
               charge=None, labour_cost=None, material_cost=None,
               subcontractor_cost=None, status=None, notes=None,
               customer_id=None):
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found.")
        if job_date           is not None: job.date               = job_date
        if customer_name      is not None: job.customer_name      = customer_name.strip()
        if job_type           is not None: job.job_type           = job_type
        if status             is not None: job.status             = status
        if charge             is not None: job.charge             = float(charge)
        if labour_cost        is not None: job.labour_cost        = float(labour_cost)
        if material_cost      is not None: job.material_cost      = float(material_cost)
        if subcontractor_cost is not None: job.subcontractor_cost = float(subcontractor_cost)
        if notes              is not None: job.notes              = notes
        if customer_id is not None:
            c = session.get(Customer, customer_id)
            if c is None:
                raise ValueError(f"Customer {customer_id} not found.")
            job.customer_id   = customer_id
            job.customer_name = c.name
        session.commit()
        session.refresh(job)
        return job


def delete_job(job_id):
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job is None:
            return False
        session.delete(job)
        session.commit()
        return True


def get_job_options():
    with SessionLocal() as session:
        rows = session.query(Job).order_by(Job.date.desc()).all()
        return [
            {
                "id": r.job_id,
                "display": f"[{r.job_id}] {r.customer_name} — {r.job_type} ({r.date})",
            }
            for r in rows
        ]


def create_customer(name, phone=None, email=None):
    with SessionLocal() as session:
        c = Customer(
            name=name.strip(),
            phone=phone.strip() if phone else None,
            email=email.strip() if email else None,
        )
        session.add(c)
        session.commit()
        session.refresh(c)
        return c


def read_all_customers():
    with SessionLocal() as session:
        rows = session.query(Customer).order_by(Customer.name).all()
        return [
            {
                "Customer_ID": r.customer_id,
                "Name":        r.name,
                "Phone":       r.phone or "",
                "Email":       r.email or "",
            }
            for r in rows
        ]


def update_customer(customer_id, name=None, phone=None, email=None):
    with SessionLocal() as session:
        c = session.get(Customer, customer_id)
        if c is None:
            raise ValueError(f"Customer {customer_id} not found.")
        if name  is not None: c.name  = name.strip()
        if phone is not None: c.phone = phone.strip() if phone.strip() else None
        if email is not None: c.email = email.strip() if email.strip() else None
        session.commit()
        session.refresh(c)
        return c


def delete_customer(customer_id):
    with SessionLocal() as session:
        c = session.get(Customer, customer_id)
        if c is None:
            return False
        linked = session.query(Job).filter(Job.customer_id == customer_id).count()
        if linked > 0:
            raise RuntimeError(f"Cannot delete: {linked} job(s) are linked to this customer.")
        session.delete(c)
        session.commit()
        return True


def get_customer_options():
    with SessionLocal() as session:
        rows = session.query(Customer).order_by(Customer.name).all()
        return [{"id": r.customer_id, "display": r.name} for r in rows]


def get_customer_profile(customer_id):
    with SessionLocal() as session:
        c = session.get(Customer, customer_id)
        if c is None:
            raise ValueError(f"Customer {customer_id} not found.")
        jobs = (
            session.query(Job)
            .filter(Job.customer_id == customer_id)
            .order_by(Job.date.desc())
            .all()
        )
        job_rows = [
            {
                "Job_ID":             j.job_id,
                "Date":               j.date,
                "Job_Type":           j.job_type,
                "Status":             j.status,
                "Charge":             j.charge,
                "Total_Cost":         j.total_cost,
                "Gross_Profit":       j.gross_profit,
                "Margin_Pct":         j.margin_pct,
            }
            for j in jobs
        ]
        return {
            "customer_id": c.customer_id,
            "name":        c.name,
            "phone":       c.phone,
            "email":       c.email,
            "jobs":        job_rows,
            "total_spend": round(sum(j.charge for j in jobs), 2),
            "job_count":   len(jobs),
        }


def create_foil_type(material_name, core_weight, unit_weight, notes=None):
    with SessionLocal() as session:
        ft = FoilType(
            material_name=material_name.strip(),
            core_weight=float(core_weight),
            unit_weight=float(unit_weight),
            notes=notes,
            created_at=date.today(),
        )
        session.add(ft)
        session.commit()
        session.refresh(ft)
        return ft


def read_all_foil_types():
    with SessionLocal() as session:
        rows = session.query(FoilType).order_by(FoilType.material_name).all()
        return [
            {
                "foil_type_id":      r.foil_type_id,
                "Material Name":     r.material_name,
                "Core Weight (g)":   r.core_weight,
                "Unit Weight (g/m)": r.unit_weight,
                "Created":           r.created_at,
                "Notes":             r.notes,
            }
            for r in rows
        ]


def get_foil_type_options():
    with SessionLocal() as session:
        rows = session.query(FoilType.foil_type_id, FoilType.material_name).order_by(FoilType.material_name).all()
        return [{"id": r.foil_type_id, "name": r.material_name} for r in rows]


def delete_foil_type(foil_type_id):
    with SessionLocal() as session:
        ft = session.get(FoilType, foil_type_id)
        if ft is None:
            return False
        session.delete(ft)
        try:
            session.commit()
        except Exception as exc:
            session.rollback()
            raise RuntimeError("Cannot delete: rolls still reference this foil type.") from exc
        return True


def create_foil_roll(foil_type_id, current_total_weight, roll_label=None, notes=None):
    with SessionLocal() as session:
        ft = session.get(FoilType, foil_type_id)
        if ft is None:
            raise ValueError(f"FoilType id={foil_type_id} does not exist.")
        calculated_length = _calculate_length(current_total_weight, ft.core_weight, ft.unit_weight)
        roll = FoilRoll(
            foil_type_id=foil_type_id,
            roll_label=(roll_label.strip() if roll_label else None),
            current_total_weight=float(current_total_weight),
            calculated_length=calculated_length,
            last_checked=date.today(),
            notes=notes,
        )
        session.add(roll)
        session.commit()
        session.refresh(roll)
        return roll


def read_all_foil_rolls():
    with SessionLocal() as session:
        rows = (
            session.query(FoilRoll, FoilType.material_name, FoilType.core_weight, FoilType.unit_weight)
            .join(FoilType, FoilRoll.foil_type_id == FoilType.foil_type_id)
            .order_by(FoilRoll.calculated_length.asc())
            .all()
        )
        return [
            {
                "Roll ID":               r.roll_id,
                "Label":                 r.roll_label or "—",
                "Material":              mat_name,
                "Total Weight (g)":      r.current_total_weight,
                "Core Weight (g)":       core_w,
                "Unit Weight (g/m)":     unit_w,
                "Calculated Length (m)": r.calculated_length,
                "Last Checked":          r.last_checked,
                "Notes":                 r.notes,
                "Low Stock":             r.calculated_length < 5.0,
            }
            for r, mat_name, core_w, unit_w in rows
        ]


def update_foil_roll_weight(roll_id, new_total_weight, notes=None):
    with SessionLocal() as session:
        roll = session.get(FoilRoll, roll_id)
        if roll is None:
            raise ValueError(f"FoilRoll id={roll_id} does not exist.")
        ft = session.get(FoilType, roll.foil_type_id)
        new_length = _calculate_length(new_total_weight, ft.core_weight, ft.unit_weight)
        roll.current_total_weight = float(new_total_weight)
        roll.calculated_length    = new_length
        roll.last_checked         = date.today()
        if notes is not None:
            roll.notes = notes
        session.commit()
        session.refresh(roll)
        return roll


def delete_foil_roll(roll_id):
    with SessionLocal() as session:
        roll = session.get(FoilRoll, roll_id)
        if roll is None:
            return False
        session.delete(roll)
        session.commit()
        return True


def get_roll_options():
    with SessionLocal() as session:
        rows = (
            session.query(FoilRoll.roll_id, FoilRoll.roll_label, FoilType.material_name, FoilRoll.calculated_length)
            .join(FoilType)
            .order_by(FoilRoll.roll_id)
            .all()
        )
        return [
            {
                "id":      r.roll_id,
                "label":   r.roll_label or f"Roll #{r.roll_id}",
                "material":r.material_name,
                "length":  r.calculated_length,
                "display": f"{'[LOW] ' if r.calculated_length < 5 else ''}[{r.roll_id}] {r.roll_label or r.material_name} ({r.calculated_length:.2f}m)",
            }
            for r in rows
        ]