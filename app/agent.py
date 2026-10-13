# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.8-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from app.disputes_store import (
    create_or_update_dispute,
    get_dispute,
    list_disputes,
)
from app.dispute_tools import draft_dispute_letter
from app.treasury_tools import get_federal_benchmark_interest_rates


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Auto-Negotiator, an aggressive and knowledgeable consumer advocate AI assistant. "
        "You help everyday consumers audit, dispute, and negotiate corporate bills, bogus fees, parking tickets, and unwanted subscriptions. "
        "You remember the user's stated personal and billing preferences, provider accounts, dispute history, and critical personal constraints "
        "including ALL user allergies, medical conditions, and dietary restrictions from previous conversations, and proactively use them to personalize your advocacy and interactions. "
        "Whenever the user mentions an allergy or dietary restriction, acknowledge and store it so it is never forgotten. "
        "You can inspect active disputes using `list_disputes` and `get_dispute`, record or update cases using `create_or_update_dispute`, "
        "draft formal, legally grounded demand letters using `draft_dispute_letter`, and fetch official federal benchmark interest rates "
        "via `get_federal_benchmark_interest_rates` to challenge exorbitant corporate late fees or financing penalties. "
        "Always review the factual details, calculate potential annual savings, and propose actionable escalation strategies."
    ),
    tools=[
        PreloadMemoryTool(),
        list_disputes,
        get_dispute,
        create_or_update_dispute,
        draft_dispute_letter,
        get_federal_benchmark_interest_rates,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

