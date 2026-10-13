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

import base64
import uuid
from typing import Any, Dict

import google.auth
from google.auth.transport.requests import Request
from google.cloud import storage
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import requests

GCS_BUCKET_NAME = "auto-negotiator-assets-8376c931"
MODEL_ID = "gemini-omni-flash-preview"
REGION = "global"


def generate_dispute_victory_video(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates a short animated celebration or victory badge video for a resolved consumer dispute or negotiation milestone using Google's Omni model (gemini-omni-flash-preview).

    The video is saved as a session artifact and uploaded to the public Cloud Storage bucket.

    Args:
        prompt: Detailed description of the dispute victory or negotiation outcome video (e.g., 'Cinematic 3D animation of a consumer tearing up an unfair broadband cancellation bill with a golden savings stamp').
        tool_context: Injected ADK ToolContext used to save session artifacts.

    Returns:
        A dictionary containing the public video URL, artifact filename, and metadata.
    """
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not credentials.valid:
        credentials.refresh(Request())

    url = f"https://aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{REGION}/interactions"

    enhanced_prompt = (
        f"{prompt.strip()}. Cinematic video celebrating a consumer dispute victory or savings milestone."
    )

    request_body = {
        "model": MODEL_ID,
        "input": [
            {
                "type": "text",
                "text": enhanced_prompt,
            }
        ],
        "response_format": [
            {
                "type": "video",
                "aspect_ratio": "16:9",
                "duration": "4s",
            }
        ],
        "generation_config": {
            "video_config": {
                "task": "text_to_video"
            }
        },
    }

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=request_body, timeout=120)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to generate video with {MODEL_ID}: HTTP {response.status_code} - {response.text}"
        )

    res_json = response.json()
    video_bytes = None

    for step in res_json.get("steps", []):
        if step.get("type") == "model_output":
            for content in step.get("content", []):
                if content.get("type") == "video" and content.get("data"):
                    video_bytes = base64.b64decode(content["data"])
                    break
        if video_bytes:
            break

    if not video_bytes:
        raise RuntimeError(
            f"No video data returned from {MODEL_ID}. Full response: {res_json}"
        )

    filename = f"victory_{uuid.uuid4().hex[:8]}.mp4"

    # 1. Save artifact to ADK ToolContext
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
        custom_metadata={"prompt": prompt, "model": MODEL_ID},
    )

    # 2. Upload to public Cloud Storage bucket
    storage_client = storage.Client(project=project)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"videos/{filename}")
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/videos/{filename}"

    return {
        "status": "success",
        "video_url": public_url,
        "artifact_filename": filename,
        "model": MODEL_ID,
        "message": f"Successfully generated video and published to {public_url}",
    }
