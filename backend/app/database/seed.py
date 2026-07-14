import asyncio
from datetime import date, timedelta

from sqlalchemy import func, select

from app.database.init_db import close_db, init_db
from app.database.models import HCP, Interaction
from app.database.session import AsyncSessionFactory


SEED_HCPS = [
    {
        "full_name": "Dr. Anjali Mehta",
        "specialty": "Cardiology",
        "organization": "Fortis Hospital",
        "city": "Mumbai",
        "email": "anjali.mehta@example.test",
        "phone": "+91-90000-00001",
    },
    {
        "full_name": "Dr. Rahul Sharma",
        "specialty": "Endocrinology",
        "organization": "Apollo Hospitals",
        "city": "Delhi",
        "email": "rahul.sharma@example.test",
        "phone": "+91-90000-00002",
    },
    {
        "full_name": "Dr. Rahul Sharma",
        "specialty": "Cardiology",
        "organization": "Max Super Speciality Hospital",
        "city": "Noida",
        "email": "rahul.sharma.noida@example.test",
        "phone": "+91-90000-00003",
    },
    {
        "full_name": "Dr. Priya Nair",
        "specialty": "Neurology",
        "organization": "Manipal Hospital",
        "city": "Bengaluru",
        "email": "priya.nair@example.test",
        "phone": "+91-90000-00004",
    },
    {
        "full_name": "Dr. Arjun Kapoor",
        "specialty": "Oncology",
        "organization": "Tata Memorial Hospital",
        "city": "Mumbai",
        "email": "arjun.kapoor@example.test",
        "phone": "+91-90000-00005",
    },
]


async def seed() -> None:
    await init_db()

    async with AsyncSessionFactory() as db:
        hcp_count = await db.scalar(select(func.count(HCP.id)))
        if not hcp_count:
            db.add_all([HCP(**item) for item in SEED_HCPS])
            await db.commit()

        mehta = (
            await db.execute(
                select(HCP).where(HCP.full_name == "Dr. Anjali Mehta").limit(1)
            )
        ).scalar_one_or_none()

        interaction_count = await db.scalar(select(func.count(Interaction.id)))
        if mehta is not None and not interaction_count:
            db.add_all(
                [
                    Interaction(
                        session_id="seed-session",
                        hcp_id=mehta.id,
                        hcp_name=mehta.full_name,
                        specialty=mehta.specialty,
                        organization=mehta.organization,
                        interaction_date=date.today() - timedelta(days=14),
                        interaction_type="In-person",
                        products_discussed=["CardioPlus"],
                        topics_discussed=["Efficacy", "Dosing"],
                        sentiment="Positive",
                        materials_shared=["Product brochure"],
                        notes="Discussed efficacy and dosing. HCP requested safety data.",
                        follow_up_required=True,
                        follow_up_date=date.today() - timedelta(days=7),
                    ),
                    Interaction(
                        session_id="seed-session",
                        hcp_id=mehta.id,
                        hcp_name=mehta.full_name,
                        specialty=mehta.specialty,
                        organization=mehta.organization,
                        interaction_date=date.today() - timedelta(days=45),
                        interaction_type="Phone",
                        products_discussed=["CardioPlus"],
                        topics_discussed=["Patient access"],
                        sentiment="Neutral",
                        materials_shared=[],
                        notes="HCP asked about patient access and availability.",
                        follow_up_required=False,
                    ),
                ]
            )
            await db.commit()

    print("Database seed completed.")


async def main() -> None:
    try:
        await seed()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
