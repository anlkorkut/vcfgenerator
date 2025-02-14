'''
model_wrapper.py code file.
'''

import requests
import json
import os
from logger import init

logger = init(__name__)

class ModelWrapper:
    def __init__(self):
        self.API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        # Get token from environment variable
        self.token = os.getenv('HF_TOKEN')
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def single_shot_completion(
        self,
        system_prompt: str,
        content_prompt: str,
        model: str = None,  # Not used but kept for compatibility
        temperature: float = 0.1,
        timeout: float = 60.0
    ) -> str:
        """Gets the model response for the given input."""
        if not self.token:
            logger.error("No Hugging Face token found. Please set HF_TOKEN environment variable.")
            return "{}"

        # Format prompt for Mistral
        prompt = f"""<s>[INST] {system_prompt}

{content_prompt} [/INST]
"""
        # Log the complete request details
        logger.info("=== API Request Details ===")
        logger.info(f"System Prompt:\n{system_prompt}")
        logger.info(f"Content Prompt:\n{content_prompt}")
        logger.info(f"Full Formatted Prompt:\n{prompt}")

        try:
            # Make request to Hugging Face API
            logger.info("Sending request to Hugging Face API...")
            response = requests.post(
                self.API_URL,
                headers=self.headers,
                json={"inputs": prompt, "parameters": {"temperature": temperature}},
                timeout=timeout
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("=== API Response ===")
                logger.info(f"Raw API Response:\n{json.dumps(result, indent=2)}")

                # Extract the generated text
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Extract the part after [/INST]
                    if '[/INST]' in generated_text:
                        generated_text = generated_text.split('[/INST]')[1].strip()

                    logger.info(f"Processed Response:\n{generated_text}")
                    return generated_text

            elif response.status_code == 429:
                logger.error("Rate limit exceeded. Please wait before making more requests.")
                logger.error(f"Response details: {response.text}")
                return "{}"
            else:
                logger.error(f"API Error: {response.status_code}")
                logger.error(f"Response details: {response.text}")
                return "{}"

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return "{}"  # Return empty JSON on error