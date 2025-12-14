from __future__ import annotations
import os
import requests
from typing import Any, Dict, List, Optional

class ModelLoader:
    """
    A class to handle the loading and inference with the local llama.cpp server.
    This implementation uses a mock response if the server is unavailable or if
    a specific environment variable is set for testing.
    """
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("LLAMA_CPP_URL")
        # Check for mock mode environment variable
        self.is_mock = os.getenv("SIA_MOCK_LLM", "False").lower() in ('true', '1', 't')

    def _mock_completion(self, prompt: str, **kwargs) -> str:
        """Provides a deterministic mock response for testing."""
        print("--- MOCK LLM INFERENCE ---")
        if "plan the following" in prompt.lower():
            return "Plan: 1. Retrieve data. 2. Analyze data. 3. Formulate response."
        elif "summarize" in prompt.lower():
            return "Summary: The user is testing the SIA system's mock LLM functionality."
        elif "respond to the user" in prompt.lower():
            return f"Hello! I am the Strategic Insider Assistant (SIA). Your query was: '{prompt[:50]}...'. I am currently running in mock mode."
        else:
            return f"Mock response for prompt: {prompt[:50]}..."

    def get_completion(self, prompt: str, **kwargs) -> str:
        """
        Sends a request to the llama.cpp server for text completion.
        """
        if self.is_mock or not self.url:
            return self._mock_completion(prompt, **kwargs)

        headers = {"Content-Type": "application/json"}
        payload = {
            "prompt": prompt,
            "n_predict": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7),
            "stop": kwargs.get("stop", ["\n", "User:", "Assistant:"]),
            "stream": False,
            **kwargs
        }

        try:
            # The llama.cpp completion endpoint is typically /completion
            completion_url = self.url.replace("/completion", "") + "/completion"
            response = requests.post(completion_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("content", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"LLM server connection failed: {e}. Falling back to mock response.")
            return self._mock_completion(prompt, **kwargs)

    def get_embedding(self, text: str) -> List[float]:
        """
        Sends a request to the llama.cpp server for text embedding.
        For this mock, we return a list of zeros, as the actual embedding logic
        is handled by a deterministic function in orchestration/retrieval.py.
        """
        # This is a placeholder for a real implementation that would query the /embedding endpoint.
        print("--- WARNING: Real embedding not implemented. Using mock. ---")
        return [0.0] * 384

    def get_model_info(self) -> Dict[str, Any]:
        """
        Retrieves information about the loaded model.
        """
        if self.is_mock or not self.url:
            return {"model": "mock-sia-llm", "context_size": 8192, "mock_mode": True}

        # NOTE: Real implementation would query the /model endpoint.
        return {"model": "unknown-llama-cpp-model", "context_size": 8192, "mock_mode": False}

# Global instance for easy access
LLM_CLIENT = ModelLoader()
