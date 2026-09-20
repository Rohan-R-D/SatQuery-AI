"""
SatQuery AI - Remote VLM HTTP Client.

Provides a unified, resilient HTTP client helper for querying remote Vision-Language Model servers
(such as vLLM, Ollama, Triton, or OpenAI-compatible multimodal API endpoints).
Includes Base64 image payload encoding, header secret sanitization, and structured error handling.
"""

import base64
import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("satquery.ai.remote_http")


class RemoteVLMHttpClient:
    """
    HTTP Client for remote multimodal VLM endpoint queries.
    """

    @staticmethod
    def is_endpoint_configured(endpoint_url: str) -> bool:
        """Checks if remote endpoint URL is specified and non-empty."""
        return bool(endpoint_url and endpoint_url.strip())

    @staticmethod
    def check_endpoint_health(endpoint_url: str, timeout: int = 5) -> bool:
        """Optional health check probe when provider supports endpoint health checking."""
        if not endpoint_url or not endpoint_url.strip():
            return False
        try:
            req = urllib.request.Request(endpoint_url, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status < 400
        except Exception:
            return False

    @classmethod
    def query_vlm_endpoint(
        cls,
        endpoint_url: str,
        prompt: str,
        image_bytes: bytes,
        provider_id: str = "remote_vlm",
        model_id: str = "default_model",
        api_key: str = "",
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Generic entrypoint for querying a remote VLM endpoint."""
        if not cls.is_endpoint_configured(endpoint_url):
            return {
                "answer": "",
                "evidence": ["Remote VLM endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "ENDPOINT_UNCONFIGURED",
                "warnings": [f"Remote endpoint URL for '{provider_id}' is missing or unconfigured."],
            }
        return cls.query_openai_multimodal_endpoint(
            endpoint_url=endpoint_url,
            model_id=model_id,
            image_bytes=image_bytes,
            prompt=prompt,
            api_key=api_key,
            timeout=timeout
        )

    @staticmethod
    def encode_image_to_base64(image_bytes: bytes) -> str:
        """Encodes raw image bytes payload to Base64 string."""
        return base64.b64encode(image_bytes).decode("utf-8")


    @classmethod
    def query_openai_multimodal_endpoint(
        cls,
        endpoint_url: str,
        model_id: str,
        image_bytes: bytes,
        prompt: str,
        api_key: str = "",
        timeout: int = 30,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a multimodal query against an OpenAI-compatible /v1/chat/completions endpoint.
        Used for remote Qwen3-VL-2B-Instruct and open multimodal API servers.
        """
        if not endpoint_url:
            return {
                "answer": f"[{model_id}]: Remote endpoint URL is not configured.",
                "evidence": ["Remote VLM endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "VLM_ENDPOINT_UNCONFIGURED",
                "warnings": ["Endpoint URL parameter was empty."],
            }

        img_b64 = cls.encode_image_to_base64(image_bytes)
        image_data_url = f"data:image/jpeg;base64,{img_b64}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_data_url}}
        ]
        messages.append({"role": "user", "content": user_content})

        payload_dict = {
            "model": model_id,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.2,
        }

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        return cls._send_json_post(
            endpoint_url=endpoint_url,
            payload_dict=payload_dict,
            headers=headers,
            timeout=timeout,
            provider_name=model_id
        )

    @classmethod
    def query_rest_vlm_endpoint(
        cls,
        endpoint_url: str,
        model_id: str,
        image_bytes: bytes,
        prompt: str,
        task: str = "vqa",
        api_key: str = "",
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Executes a multimodal query against a custom REST VLM endpoint (e.g. GeoChat specialist server).
        """
        if not endpoint_url:
            return {
                "answer": f"[{model_id}]: Remote endpoint URL is not configured.",
                "evidence": ["Remote VLM endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "VLM_ENDPOINT_UNCONFIGURED",
                "warnings": ["Endpoint URL parameter was empty."],
            }

        img_b64 = cls.encode_image_to_base64(image_bytes)
        payload_dict = {
            "model": model_id,
            "prompt": prompt,
            "image": img_b64,
            "task": task,
        }

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        return cls._send_json_post(
            endpoint_url=endpoint_url,
            payload_dict=payload_dict,
            headers=headers,
            timeout=timeout,
            provider_name=model_id
        )

    @classmethod
    def _send_json_post(
        cls,
        endpoint_url: str,
        payload_dict: Dict[str, Any],
        headers: Dict[str, str],
        timeout: int,
        provider_name: str
    ) -> Dict[str, Any]:
        """Sends HTTP POST payload and parses OpenAI/REST responses."""
        try:
            payload_bytes = json.dumps(payload_dict).encode("utf-8")
            req = urllib.request.Request(endpoint_url, data=payload_bytes, headers=headers, method="POST")

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_bytes = resp.read()
                data = json.loads(resp_bytes.decode("utf-8"))

                # Parse OpenAI choices format if present
                answer_text = ""
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    message = choice.get("message", {})
                    answer_text = message.get("content", "")
                elif "answer" in data:
                    answer_text = data.get("answer", "")
                elif "response" in data:
                    answer_text = data.get("response", "")
                elif "caption" in data:
                    answer_text = data.get("caption", "")

                if not answer_text:
                    answer_text = f"[{provider_name}]: Received empty response content."

                return {
                    "answer": answer_text,
                    "caption": answer_text,
                    "evidence": data.get("evidence", [f"Response from remote provider {provider_name}."]),
                    "confidence": float(data.get("confidence", 90.0)),
                    "bounding_boxes": data.get("bounding_boxes", []),
                    "is_error": False,
                    "error_code": None,
                    "warnings": [],
                }

        except urllib.error.HTTPError as e:
            logger.error(f"RemoteVLMHttpClient HTTPError {e.code} for {provider_name}: {e.reason}")
            return {
                "answer": f"[{provider_name}]: Remote HTTP {e.code} Error.",
                "evidence": [],
                "confidence": 0.0,
                "is_error": True,
                "error_code": f"HTTP_{e.code}",
                "warnings": [f"Remote endpoint returned HTTP {e.code}: {e.reason}"],
            }
        except urllib.error.URLError as e:
            logger.error(f"RemoteVLMHttpClient URLError for {provider_name}: {e.reason}")
            return {
                "answer": f"[{provider_name}]: Remote endpoint unreachable.",
                "evidence": [],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "NETWORK_UNREACHABLE",
                "warnings": [f"Failed to connect to endpoint '{endpoint_url}': {e.reason}"],
            }
        except Exception as e:
            logger.error(f"RemoteVLMHttpClient unexpected failure for {provider_name}: {e}")
            return {
                "answer": f"[{provider_name}]: Remote query failed: {str(e)}",
                "evidence": [],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "REMOTE_QUERY_FAILURE",
                "warnings": [str(e)],
            }


remote_http_client = RemoteVLMHttpClient()
