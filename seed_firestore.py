#!/usr/bin/env python3
"""Seed script for the Auto-Negotiator disputes and playbooks in Firestore."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-8376c9310072"
COLLECTION_NAME = "disputes"

SEED_DISPUTES = [
    {
        "id": "disp-001",
        "title": "Unreturned Equipment Surcharge",
        "provider": "Comcast Xfinity",
        "category": "internet_cable",
        "dispute_type": "bogus_fee",
        "account_last4": "4821",
        "amount_disputed": 120.00,
        "currency": "USD",
        "status": "in_progress",
        "deadline": "2026-10-25",
        "filing_basis": "Returned router at UPS Store on Sept 14 (tracking receipt #1Z99999). Agent charged fee erroneously.",
        "recommended_action": "Demand immediate fee waiver citing UPS return tracking number and FTC consumer billing guidelines.",
        "potential_annual_savings": 120.00,
    },
    {
        "id": "disp-002",
        "title": "Post-Cancellation Renewal Fee",
        "provider": "Planet Fitness",
        "category": "subscription",
        "dispute_type": "contract_cancellation",
        "account_last4": "9312",
        "amount_disputed": 59.99,
        "currency": "USD",
        "status": "pending_user_approval",
        "deadline": "2026-10-20",
        "filing_basis": "Cancellation letter delivered in person with 30-day notice on Aug 20. Billed for September and October unauthorized.",
        "recommended_action": "Submit formal demand letter referencing signed cancellation receipt; issue credit card chargeback warning.",
        "potential_annual_savings": 240.00,
    },
    {
        "id": "disp-003",
        "title": "Street Cleaning Ticket During Public Holiday",
        "provider": "City Parking Bureau",
        "category": "parking_ticket",
        "dispute_type": "statutory_defense",
        "account_last4": "0000",
        "amount_disputed": 75.00,
        "currency": "USD",
        "status": "drafted",
        "deadline": "2026-10-18",
        "filing_basis": "Ticket issued on Indigenous Peoples' Day / Columbus Day when street sweeping enforcement was officially suspended per city code.",
        "recommended_action": "Submit photographic proof and reference Municipal Traffic Code Section 14-B holiday parking exemption.",
        "potential_annual_savings": 75.00,
    },
    {
        "id": "disp-004",
        "title": "Expired Promotional Rate Hike",
        "provider": "AT&T Fiber",
        "category": "internet_cable",
        "dispute_type": "rate_negotiation",
        "account_last4": "1158",
        "amount_disputed": 40.00,
        "currency": "USD",
        "status": "resolved",
        "deadline": "2026-09-30",
        "filing_basis": "Promo expired increasing monthly bill from $55 to $95. Competitor Sonic Fiber offers equivalent speed at $50/mo.",
        "recommended_action": "Retention department match request with competitor offer leverage.",
        "potential_annual_savings": 480.00,
    },
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    batch = db.batch()

    for item in SEED_DISPUTES:
        doc_id = item["id"]
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        batch.set(doc_ref, item)
        print(f"Queued seed item: {doc_id} - {item['title']} ({item['provider']})")

    batch.commit()
    print(f"Successfully seeded {len(SEED_DISPUTES)} documents into '{COLLECTION_NAME}' collection!")


if __name__ == "__main__":
    seed()
