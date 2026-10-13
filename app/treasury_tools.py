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

"""US Treasury Fiscal Data public API integration for benchmark rates & late-fee interest disputes."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List


API_BASE_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"
)


def get_federal_benchmark_interest_rates(security_type: str = "Treasury Bills") -> Dict[str, Any]:
    """Fetches official federal benchmark interest rates from the US Department of the Treasury Fiscal Data public API.

    This provides real authoritative financial benchmark data to contest exorbitant corporate late payment penalties,
    finance charges, and usurious billing fees during negotiations.

    Args:
        security_type: Security benchmark description ('Treasury Bills', 'Treasury Notes', 'Treasury Bonds'). Defaults to 'Treasury Bills'.

    Returns:
        A dictionary with the latest benchmark interest rate, effective date, and negotiation leverage guidance.
    """
    # Read optional API key from environment variable if configured
    api_key = os.getenv("FISCAL_DATA_API_KEY")

    query_params = {
        "sort": "-record_date",
        "filter": f"security_desc:eq:{security_type}",
        "page[size]": 3,
    }
    url = f"{API_BASE_URL}?{urllib.parse.urlencode(query_params)}"

    headers = {"User-Agent": "AutoNegotiator-FiscalBenchmark/1.0"}
    if api_key:
        headers["X-API-KEY"] = api_key

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve data from US Treasury Fiscal Data API: {str(e)}",
            "data": [],
        }

    records: List[Dict[str, Any]] = []
    for item in data.get("data", []):
        records.append({
            "security": item.get("security_desc"),
            "rate_percent": float(item.get("avg_interest_rate_amt", 0.0)),
            "effective_date": item.get("record_date"),
        })

    latest_rate = records[0]["rate_percent"] if records else None
    latest_date = records[0]["effective_date"] if records else None

    return {
        "status": "success",
        "security_type": security_type,
        "latest_rate_percent": latest_rate,
        "effective_date": latest_date,
        "recent_history": records,
        "negotiation_leverage": (
            f"Official US Treasury {security_type} rate is currently {latest_rate}% (as of {latest_date}). "
            "Corporate late fees equivalent to 20-30%+ APR significantly exceed federal benchmark borrowing rates "
            "and can be challenged as unconscionable punitive charges rather than reasonable administrative costs."
        ),
    }
