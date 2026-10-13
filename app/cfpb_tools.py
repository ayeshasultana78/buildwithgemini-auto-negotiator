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

"""CFPB (Consumer Financial Protection Bureau) public API tool for dispute intelligence."""

import os
import urllib.parse
import urllib.request
import json
from typing import Any, Dict, List


CFPB_API_BASE = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"


def lookup_regulatory_complaints(company_or_keyword: str, max_results: int = 3) -> Dict[str, Any]:
    """Queries the official public CFPB Consumer Complaint Database for historical complaints against a company or financial institution.

    This provides real data and leverage during consumer disputes, identifying common issues, regulatory response patterns, and enforcement precedent.

    Args:
        company_or_keyword: Name of the company, bank, or billing topic (e.g. 'Citibank', 'Wells Fargo', 'overdraft fee').
        max_results: Maximum complaint records to return (defaults to 3).

    Returns:
        A dictionary with query stats and a list of recorded complaints including issue type, product category, and corporate response.
    """
    # CFPB is a free public API requiring no key, but an optional key / token can be provided via environment variable
    api_key = os.getenv("CFPB_API_KEY")

    params = {
        "search_term": company_or_keyword,
        "size": max(1, min(max_results, 10)),
    }
    url = f"{CFPB_API_BASE}?{urllib.parse.urlencode(params)}"

    headers = {"User-Agent": "AutoNegotiator-ConsumerAdvocate/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve data from CFPB database: {str(e)}",
            "results": [],
        }

    total_hits = data.get("hits", {}).get("total", {})
    total_count = total_hits.get("value", 0) if isinstance(total_hits, dict) else total_hits

    raw_hits = data.get("hits", {}).get("hits", [])
    complaints: List[Dict[str, Any]] = []

    for hit in raw_hits:
        src = hit.get("_source", {})
        complaints.append({
            "complaint_id": src.get("complaint_id"),
            "company": src.get("company"),
            "product": src.get("product"),
            "sub_product": src.get("sub_product"),
            "issue": src.get("issue"),
            "sub_issue": src.get("sub_issue"),
            "company_response": src.get("company_response"),
            "date_received": src.get("date_received"),
        })

    return {
        "status": "success",
        "search_term": company_or_keyword,
        "total_matched_in_cfpb": total_count,
        "complaints": complaints,
        "negotiation_tip": (
            f"Found {total_count} official CFPB complaint filings for '{company_or_keyword}'. "
            "Citing these patterns demonstrates that the company is under scrutiny for recurring billing and customer service failures."
        ),
    }
