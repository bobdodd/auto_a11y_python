"""
Claude AI client wrapper for API communication
"""

import logging
import base64
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
from anthropic import AsyncAnthropic, Anthropic

logger = logging.getLogger(__name__)


@dataclass
class ClaudeConfig:
    """Claude AI configuration"""
    api_key: str
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 4096
    temperature: float = 1.0
    timeout: int = 60
    
    # Available models
    MODELS = {
        'opus': 'claude-3-opus-20240229',      # Best quality
        'sonnet': 'claude-3-sonnet-20240229',  # Balanced
        'haiku': 'claude-3-haiku-20240307'     # Fastest
    }


class ClaudeClient:
    """Wrapper for Claude AI API client"""
    
    def __init__(self, config: ClaudeConfig):
        """
        Initialize Claude client
        
        Args:
            config: Claude configuration
        """
        self.config = config
        self.async_client = AsyncAnthropic(api_key=config.api_key)
        self.sync_client = Anthropic(api_key=config.api_key)
        self.system_prompt = self._get_system_prompt()
        
        logger.info(f"Claude client initialized with model: {config.model}")
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for accessibility analysis"""
        return """You are a pedantic and thoughtful assistant focused on digital 
        accessibility concerns. You check results in as many ways as possible for 
        accuracy. You are an expert in WCAG 2.1 Level A, AA, and AAA guidelines 
        and modern web accessibility best practices.
        
        When analyzing web pages:
        1. Be precise about accessibility issues
        2. Reference specific WCAG criteria when applicable
        3. Provide actionable recommendations
        4. Consider different disability types (visual, motor, cognitive, auditory)
        5. Focus on barriers that prevent users from accessing content or functionality
        6. Always respond with valid JSON when requested"""
    
    async def analyze_with_image(
        self,
        image_data: bytes,
        prompt: str,
        image_format: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Analyze an image with a text prompt
        
        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            image_format: MIME type of image
            
        Returns:
            Analysis results as dictionary
        """
        try:
            # Detect actual image format from magic bytes
            if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                actual_format = "image/png"
            elif image_data[:2] == b'\xff\xd8':
                actual_format = "image/jpeg"
            else:
                actual_format = image_format  # Use provided format as fallback
            
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Send request to Claude
            message = await self.async_client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": actual_format,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            # Extract and parse response
            response_text = message.content[0].text
            
            # Parse response - extract JSON from text
            try:
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end + 1]
                    return json.loads(json_str)
                else:
                    return {'raw_response': response_text}
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from Claude response")
                return {'raw_response': response_text}
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    async def analyze_html(
        self,
        html: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Analyze HTML content
        
        Args:
            html: HTML content
            prompt: Analysis prompt
            
        Returns:
            Analysis results
        """
        try:
            message = await self.async_client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"{prompt}\n\nHTML:\n{html}"
                }]
            )
            
            response_text = message.content[0].text
            
            # Parse response - extract JSON from text
            try:
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end + 1]
                    return json.loads(json_str)
                else:
                    return {'raw_response': response_text}
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from Claude response")
                return {'raw_response': response_text}
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    async def analyze_with_image_and_html(
        self,
        image_data: bytes,
        html: str,
        prompt: str,
        image_format: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Analyze both image and HTML content together
        
        Args:
            image_data: Screenshot bytes
            html: HTML content
            prompt: Analysis prompt
            image_format: MIME type
            
        Returns:
            Analysis results
        """
        try:
            # Detect actual image format from magic bytes
            if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                actual_format = "image/png"
                logger.debug("Detected PNG image format")
            elif image_data[:2] == b'\xff\xd8':
                actual_format = "image/jpeg"
                logger.debug("Detected JPEG image format")
            else:
                actual_format = image_format  # Use provided format as fallback
                logger.debug(f"Using provided format: {image_format}")
            
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Combine prompt with HTML
            full_prompt = f"""{prompt}
            
            HTML Content:
            {html[:10000]}  # Limit HTML to avoid token limits
            """
            
            # Send request
            message = await self.async_client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": actual_format,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": full_prompt
                        }
                    ]
                }]
            )
            
            response_text = message.content[0].text
            
            # DEBUG: Save raw response to file
            import os
            from datetime import datetime
            debug_dir = "ai_debug"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save the prompt and response
            with open(f"{debug_dir}/ai_response_{timestamp}.txt", "w") as f:
                f.write("=" * 60 + "\n")
                f.write("PROMPT:\n")
                f.write("=" * 60 + "\n")
                f.write(full_prompt + "\n")
                f.write("=" * 60 + "\n")
                f.write("RAW RESPONSE:\n")
                f.write("=" * 60 + "\n")
                f.write(response_text + "\n")
            
            logger.info(f"DEBUG: Saved AI response to ai_debug/ai_response_{timestamp}.txt")
            
            # Parse response - extract JSON from text
            # Claude sometimes prefixes JSON with explanatory text
            try:
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end + 1]
                    return json.loads(json_str)
                else:
                    return {'raw_response': response_text}
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from Claude response")
                return {'raw_response': response_text}
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    async def aclose(self):
        """Close the async client properly"""
        try:
            if hasattr(self.async_client, '_client'):
                await self.async_client._client.aclose()
        except Exception as e:
            logger.debug(f"Error closing Claude client: {e}")
    
    def get_token_estimate(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    async def batch_analyze(
        self,
        analyses: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Run multiple analyses in parallel with rate limiting
        
        Args:
            analyses: List of analysis requests
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_with_limit(analysis):
            async with semaphore:
                if 'image' in analysis:
                    return await self.analyze_with_image(
                        analysis['image'],
                        analysis['prompt']
                    )
                else:
                    return await self.analyze_html(
                        analysis['html'],
                        analysis['prompt']
                    )
        
        tasks = [run_with_limit(a) for a in analyses]
        return await asyncio.gather(*tasks, return_exceptions=True)