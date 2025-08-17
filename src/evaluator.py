"""
Core evaluation module for LLM-based paper review.
Handles OpenRouter API calls and review generation.
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .prompts import create_evaluation_prompt, create_multi_judge_prompt


class LLMEvaluator:
    """Handles LLM-based paper evaluation using OpenRouter API."""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3-haiku", 
                 temperature: float = 0.1, max_tokens: int = 4000, log_prompts: bool = False):
        """
        Initialize the evaluator.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier for OpenRouter
            temperature: Temperature for response generation
            max_tokens: Maximum tokens for response
            log_prompts: Whether to save prompts to logs/ directory
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.log_prompts = log_prompts
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    def evaluate_paper(self, paper_content: str, paper_title: str = "Unknown Paper", 
                      judge_persona: str = "", guidelines_file: str = "resource/neurips_guidelines.txt") -> str:
        """
        Evaluate a paper using the configured LLM.
        
        Args:
            paper_content: Full text content of the paper
            paper_title: Title of the paper
            judge_persona: Optional persona/expertise for specialized evaluation
        
        Returns:
            Generated review text
        """
        if judge_persona:
            prompt = create_multi_judge_prompt(paper_content, paper_title, judge_persona, guidelines_file)
        else:
            prompt = create_evaluation_prompt(paper_content, paper_title, guidelines_file)
        
        # Log prompt if enabled
        if self.log_prompts:
            self._save_prompt(prompt, paper_title, judge_persona)
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            # Check for HTTP errors and provide detailed error messages
            if response.status_code == 400:
                error_details = "Bad Request - "
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        if 'message' in error_data['error']:
                            error_details += error_data['error']['message']
                        else:
                            error_details += str(error_data['error'])
                    else:
                        error_details += "Invalid request parameters"
                except:
                    error_details += "Invalid request format or parameters"
                return f"API Error (400): {error_details}\nModel: {self.model}\nCheck if model name is correct and available."
            
            elif response.status_code == 401:
                return f"API Error (401): Unauthorized - Invalid API key\nCheck your OpenRouter API key in config file."
            
            elif response.status_code == 402:
                return f"API Error (402): Payment Required - Insufficient credits or quota exceeded\nCheck your OpenRouter account balance."
            
            elif response.status_code == 429:
                return f"API Error (429): Rate Limited - Too many requests\nTry increasing api_delay in config or wait before retrying."
            
            elif response.status_code >= 500:
                return f"API Error ({response.status_code}): Server Error - OpenRouter service issue\nTry again later or contact OpenRouter support."
            
            response.raise_for_status()
            
            result = response.json()
            
            # Check if response has expected structure
            if 'choices' not in result or not result['choices']:
                return f"API Error: Empty or invalid response structure\nResponse: {result}"
            
            if 'message' not in result['choices'][0] or 'content' not in result['choices'][0]['message']:
                return f"API Error: Missing content in response\nResponse structure: {result['choices'][0] if result['choices'] else 'No choices'}"
            
            content = result['choices'][0]['message']['content']
            if not content or content.strip() == "":
                return f"API Error: Empty content returned from model {self.model}\nThis may indicate a model issue or prompt problem."
            
            return content
            
        except requests.exceptions.RequestException as e:
            return f"Network Error: {str(e)}\nCheck your internet connection and OpenRouter service status."
        except KeyError as e:
            return f"Response Format Error: Missing key {str(e)} in API response\nThis may indicate an API change or model issue."
        except Exception as e:
            return f"Unexpected Error: {str(e)}\nModel: {self.model}"
    
    def _save_prompt(self, prompt: str, paper_title: str, judge_persona: str = ""):
        """Save prompt to logs directory for inspection."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp and model info
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in paper_title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        safe_title = safe_title.replace(' ', '_')
        
        model_name = self.model.replace('/', '_').replace(':', '_')
        persona_suffix = f"_{judge_persona.replace(' ', '_')}" if judge_persona else ""
        
        filename = f"{timestamp}_{safe_title}_{model_name}{persona_suffix}.prompt.txt"
        filepath = logs_dir / filename
        
        # Save prompt with metadata
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Prompt Log\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Paper Title: {paper_title}\n")
            f.write(f"Model: {self.model}\n")
            f.write(f"Judge Persona: {judge_persona or 'None'}\n")
            f.write(f"Temperature: {self.temperature}\n")
            f.write(f"Max Tokens: {self.max_tokens}\n")
            f.write(f"{'='*80}\n\n")
            f.write(prompt)
    
    def batch_evaluate(self, paper_content: str, paper_title: str, 
                      judges: List[Dict[str, str]], delay: float = 1.0,
                      temperature: float = None, max_tokens: int = None, 
                      guidelines_file: str = "resource/neurips_guidelines.txt") -> Dict[str, str]:
        """
        Evaluate a paper with multiple judges.
        
        Args:
            paper_content: Full text content of the paper
            paper_title: Title of the paper
            judges: List of judge configurations with 'name', 'model', and optional 'persona'
            delay: Delay between API calls in seconds
            temperature: Temperature override for all judges
            max_tokens: Max tokens override for all judges
        
        Returns:
            Dictionary mapping judge names to their reviews
        """
        reviews = {}
        
        for judge in judges:
            judge_name = judge.get('name', 'unnamed_judge')
            judge_model = judge.get('model', self.model)
            judge_persona = judge.get('persona', '')
            
            print(f"Evaluating with {judge_name} ({judge_model})...")
            
            # Create evaluator for this specific judge's model
            judge_temperature = temperature if temperature is not None else self.temperature
            judge_max_tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            evaluator = LLMEvaluator(self.api_key, judge_model, judge_temperature, judge_max_tokens, self.log_prompts)
            review = evaluator.evaluate_paper(paper_content, paper_title, judge_persona, guidelines_file)
            reviews[judge_name] = review
            
            # Add delay between calls to respect rate limits
            if delay > 0:
                time.sleep(delay)
        
        return reviews