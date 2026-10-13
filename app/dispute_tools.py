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

"""Dispute action tools for the Auto-Negotiator agent."""

import datetime
from typing import Any, Dict, Optional
from app.disputes_store import create_or_update_dispute, get_dispute


def draft_dispute_letter(
    provider: str,
    dispute_reason: str,
    amount: float,
    account_number: str = "XXXX-XXXX",
    evidence_details: str = "Attached receipts and documentation",
    dispute_id: Optional[str] = None,
    urgency_days: int = 14,
) -> Dict[str, Any]:
    """Generates a formal consumer dispute / negotiation demand letter and saves or updates the dispute record.

    Args:
        provider: Target organization or business (e.g. 'Comcast Xfinity', 'Planet Fitness', 'City Parking Bureau').
        dispute_reason: Summary of why the charge or fee is disputed (e.g. 'Unreturned equipment fee for returned item', 'Post-cancellation billing').
        amount: Dollar amount in dispute.
        account_number: Relevant customer account, citation, or reference number.
        evidence_details: Specific evidence, tracking numbers, or facts (e.g. 'UPS drop-off receipt #1Z999 on 09/14').
        dispute_id: Optional ID of an existing dispute document in Firestore. If provided, the draft updates that record.
        urgency_days: Number of calendar days given for resolution before escalation. Defaults to 14.

    Returns:
        A dictionary containing the generated formal letter text, escalation notices, and dispute record ID.
    """
    today_str = datetime.date.today().isoformat()
    deadline_date = (datetime.date.today() + datetime.timedelta(days=urgency_days)).isoformat()

    # Determine legal/regulatory leverage based on provider type
    provider_lower = provider.lower()
    if any(k in provider_lower for k in ["cable", "internet", "comcast", "xfinity", "at&t", "verizon", "spectrum"]):
        statute_warning = "Federal Communications Commission (FCC) Consumer Complaints and FTC Fair Credit Billing Act"
    elif any(k in provider_lower for k in ["gym", "fitness", "subscription", "recurring"]):
        statute_warning = "FTC Restore Online Shoppers' Confidence Act (ROSCA) and State Automatic Renewal Laws (ARL)"
    elif any(k in provider_lower for k in ["parking", "traffic", "city", "citation"]):
        statute_warning = "Municipal Administrative Adjudication Code and Due Process Hearing Rights"
    else:
        statute_warning = "Consumer Financial Protection Bureau (CFPB) guidelines and FTC Section 5 Unfair/Deceptive Practices"

    letter_text = f"""[FORMAL NOTICE OF DISPUTE AND DEMAND FOR CORRECTION]

Date: {today_str}
To: Dispute & Billing Resolution Department, {provider}
Re: Disputed Charge of ${amount:.2f} | Account/Ref: {account_number}

To Whom It May Concern,

I am writing to formally dispute the charge of ${amount:.2f} assessed against my account regarding: {dispute_reason}.

STATEMENT OF FACTS & EVIDENCE:
{evidence_details}

DEMAND & RESOLUTION:
Under prevailing consumer protection standards, including {statute_warning}, I request:
1. Immediate removal/refund of the disputed amount (${amount:.2f}).
2. Written confirmation that this matter has been resolved with zero negative reporting to credit bureaus.

Please provide written response and resolution by {deadline_date} ({urgency_days} calendar days). If this unauthorized or erroneous charge is not remedied within this timeframe, I reserve the right to escalate this formal complaint directly to regulatory authorities ({statute_warning}) and initiate an adverse merchant chargeback.

Sincerely,
Consumer Advocate on behalf of Account Holder
"""

    # Persist or update in Firestore
    saved_record = create_or_update_dispute(
        title=f"Dispute: {provider} - ${amount:.2f}",
        provider=provider,
        amount_disputed=amount,
        filing_basis=f"{dispute_reason}. Evidence: {evidence_details}",
        dispute_id=dispute_id,
        category="formal_dispute",
        dispute_type="billing_error",
        status="drafted",
        deadline=deadline_date,
        recommended_action=f"Deliver formal letter. Escalate to {statute_warning} if unpaid by {deadline_date}.",
        potential_annual_savings=amount,
    )

    return {
        "status": "success",
        "dispute_id": saved_record["dispute"]["id"],
        "deadline": deadline_date,
        "escalation_regulator": statute_warning,
        "letter": letter_text,
    }
