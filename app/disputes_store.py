# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Firestore backend integration for the Auto-Negotiator disputes catalog."""

import uuid
from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcoded project ID as string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-8376c9310072"
COLLECTION_NAME = "disputes"

_client: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    """Lazily initializes and returns the Firestore client."""
    global _client
    if _client is None:
        _client = firestore.Client(project=PROJECT_ID)
    return _client


def list_disputes(status_filter: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Lists disputes and negotiation records from Firestore.

    Args:
        status_filter: Optional filter by dispute status (e.g., 'in_progress', 'drafted', 'resolved', 'pending_user_approval').
        limit: Maximum number of disputes to return. Defaults to 10.

    Returns:
        A list of dispute dictionaries with details including ID, title, provider, amount, deadline, and recommended action.
    """
    db = get_db()
    query = db.collection(COLLECTION_NAME)
    if status_filter:
        query = query.where("status", "==", status_filter)
    
    docs = query.limit(limit).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_dispute(dispute_id: str) -> Dict[str, Any]:
    """Retrieves a single dispute by its unique ID.

    Args:
        dispute_id: The ID of the dispute document (e.g., 'disp-001').

    Returns:
        The dispute details dictionary, or an error message if not found.
    """
    db = get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(dispute_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Dispute with ID '{dispute_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def create_or_update_dispute(
    title: str,
    provider: str,
    amount_disputed: float,
    filing_basis: str,
    dispute_id: Optional[str] = None,
    category: str = "general",
    dispute_type: str = "negotiation",
    status: str = "drafted",
    deadline: Optional[str] = None,
    recommended_action: Optional[str] = None,
    potential_annual_savings: Optional[float] = None,
) -> Dict[str, Any]:
    """Creates a new dispute or updates an existing one in the Firestore collection.

    Args:
        title: Short descriptive title of the dispute (e.g. 'Unreturned Equipment Surcharge').
        provider: Name of the company, service, or municipal entity (e.g. 'Comcast Xfinity').
        amount_disputed: The dollar amount being disputed or negotiated.
        filing_basis: The user's factual explanation or evidence for the dispute.
        dispute_id: Optional ID for updating an existing dispute. If not supplied, an ID is generated.
        category: Category of dispute, e.g. 'internet_cable', 'subscription', 'parking_ticket', 'utility'.
        dispute_type: Type of dispute, e.g. 'bogus_fee', 'contract_cancellation', 'rate_negotiation'.
        status: Status string: 'drafted', 'in_progress', 'pending_user_approval', 'resolved', or 'rejected'.
        deadline: Due date or response deadline in YYYY-MM-DD format.
        recommended_action: Proposed next negotiation step or strategy.
        potential_annual_savings: Estimated annual money saved if negotiation succeeds.

    Returns:
        A dictionary with operation confirmation and the recorded dispute details.
    """
    db = get_db()
    if not dispute_id:
        dispute_id = f"disp-{uuid.uuid4().hex[:6]}"

    record = {
        "id": dispute_id,
        "title": title,
        "provider": provider,
        "amount_disputed": float(amount_disputed),
        "filing_basis": filing_basis,
        "category": category,
        "dispute_type": dispute_type,
        "status": status,
        "currency": "USD",
        "deadline": deadline or "",
        "recommended_action": recommended_action or "",
        "potential_annual_savings": float(potential_annual_savings) if potential_annual_savings is not None else float(amount_disputed),
    }

    doc_ref = db.collection(COLLECTION_NAME).document(dispute_id)
    doc_ref.set(record, merge=True)
    return {"status": "success", "dispute": record}
