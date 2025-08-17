"""
Paper improvement module for iterative self-improvement based on LLM reviews.
Handles automatic and interactive improvement workflows.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .evaluator import LLMEvaluator
from .file_processor import FileProcessor
from .prompts import create_improvement_plan_prompt, create_paper_revision_prompt


class PaperImprover:
    """Handles iterative paper improvement based on LLM reviews."""
    
    def __init__(self, evaluator: LLMEvaluator, guidelines_file: str = "resource/neurips_guidelines.txt"):
        """
        Initialize the paper improver.
        
        Args:
            evaluator: LLMEvaluator instance for generating reviews and plans
            guidelines_file: Path to review guidelines file
        """
        self.evaluator = evaluator
        self.guidelines_file = guidelines_file
    
    def improve_paper_automatic(self, paper_file: str, judges: List[Dict[str, str]], 
                               num_rounds: int = 3, output_dir: str = "improvements",
                               verbose: bool = False) -> str:
        """
        Automatically improve a paper for specified number of rounds.
        
        Args:
            paper_file: Path to LaTeX paper file
            judges: List of judge configurations
            num_rounds: Number of improvement rounds
            output_dir: Directory to save improved versions
            verbose: Enable verbose output
        
        Returns:
            Path to final improved paper
        """
        if verbose:
            print(f"Starting automatic improvement for {num_rounds} rounds...")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create timestamped subdirectory for this improvement session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = output_path / f"session_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        current_paper = paper_file
        paper_name = Path(paper_file).stem
        
        for round_num in range(1, num_rounds + 1):
            if verbose:
                print(f"\n--- Round {round_num}/{num_rounds} ---")
            
            # Generate reviews for current version
            if verbose:
                print("Generating reviews...")
            reviews = self._generate_reviews(current_paper, judges, verbose)
            
            # Create improvement plan
            if verbose:
                print("Creating improvement plan...")
            plan = self._create_improvement_plan(current_paper, reviews, verbose)
            
            # Save plan
            plan_file = session_dir / f"round_{round_num}_plan.txt"
            with open(plan_file, 'w', encoding='utf-8') as f:
                f.write(f"# Improvement Plan - Round {round_num}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(plan)
            
            # Apply improvements
            if verbose:
                print("Applying improvements...")
            improved_paper = self._apply_improvements(current_paper, plan, verbose)
            
            # Save improved version
            improved_file = session_dir / f"round_{round_num}_{paper_name}_improved.tex"
            with open(improved_file, 'w', encoding='utf-8') as f:
                f.write(improved_paper)
            
            current_paper = str(improved_file)
            
            if verbose:
                print(f"Round {round_num} completed. Improved paper saved to: {improved_file}")
        
        # Create final version
        final_file = session_dir / f"{paper_name}_final_improved.tex"
        shutil.copy2(current_paper, final_file)
        
        if verbose:
            print(f"\nAutomatic improvement completed! Final paper: {final_file}")
        
        return str(final_file)
    
    def improve_paper_interactive(self, paper_file: str, judges: List[Dict[str, str]], 
                                 output_dir: str = "improvements", verbose: bool = False) -> str:
        """
        Interactively improve a paper with user approval at each step.
        
        Args:
            paper_file: Path to LaTeX paper file
            judges: List of judge configurations
            output_dir: Directory to save improved versions
            verbose: Enable verbose output
        
        Returns:
            Path to final improved paper
        """
        if verbose:
            print("Starting interactive improvement...")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create timestamped subdirectory for this improvement session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = output_path / f"interactive_session_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        current_paper = paper_file
        paper_name = Path(paper_file).stem
        round_num = 1
        
        while True:
            print(f"\n--- Round {round_num} ---")
            
            # Generate reviews for current version
            print("Generating reviews...")
            reviews = self._generate_reviews(current_paper, judges, verbose)
            
            # Create improvement plan
            print("Creating improvement plan...")
            plan = self._create_improvement_plan(current_paper, reviews, verbose)
            
            # Save and display plan
            plan_file = session_dir / f"round_{round_num}_plan.txt"
            with open(plan_file, 'w', encoding='utf-8') as f:
                f.write(f"# Improvement Plan - Round {round_num}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(plan)
            
            print(f"\nImprovement plan saved to: {plan_file}")
            print("\n" + "="*80)
            print("IMPROVEMENT PLAN:")
            print("="*80)
            print(plan[:2000] + ("..." if len(plan) > 2000 else ""))
            print("="*80)
            
            # Ask for user approval
            while True:
                response = input("\nProceed with this improvement plan? (y/n/q): ").lower().strip()
                if response in ['y', 'yes']:
                    break
                elif response in ['n', 'no']:
                    print("Skipping this round. Generating new plan...")
                    continue
                elif response in ['q', 'quit']:
                    print("Improvement process terminated by user.")
                    return current_paper
                else:
                    print("Please enter 'y' (yes), 'n' (no), or 'q' (quit)")
            
            # Apply improvements
            print("Applying improvements...")
            improved_paper = self._apply_improvements(current_paper, plan, verbose)
            
            # Save improved version
            improved_file = session_dir / f"round_{round_num}_{paper_name}_improved.tex"
            with open(improved_file, 'w', encoding='utf-8') as f:
                f.write(improved_paper)
            
            current_paper = str(improved_file)
            print(f"Round {round_num} completed. Improved paper saved to: {improved_file}")
            
            # Ask if user wants to continue
            while True:
                response = input("\nContinue with another improvement round? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    round_num += 1
                    break
                elif response in ['n', 'no']:
                    # Create final version
                    final_file = session_dir / f"{paper_name}_final_improved.tex"
                    shutil.copy2(current_paper, final_file)
                    print(f"\nInteractive improvement completed! Final paper: {final_file}")
                    return str(final_file)
                else:
                    print("Please enter 'y' (yes) or 'n' (no)")
    
    def _generate_reviews(self, paper_file: str, judges: List[Dict[str, str]], verbose: bool = False) -> Dict[str, str]:
        """Generate reviews for the current paper version."""
        # Process paper file
        paper_content, paper_title = FileProcessor.process_file(paper_file)
        clean_content = FileProcessor.clean_text_for_evaluation(paper_content)
        
        if verbose:
            print(f"Paper title: {paper_title}")
            print(f"Content length: {len(clean_content)} characters")
        
        # Generate reviews using batch evaluation
        reviews = self.evaluator.batch_evaluate(
            clean_content,
            paper_title,
            judges,
            delay=1.0,
            guidelines_file=self.guidelines_file
        )
        
        return reviews
    
    def _create_improvement_plan(self, paper_file: str, reviews: Dict[str, str], verbose: bool = False) -> str:
        """Create improvement plan based on reviews."""
        # Read paper content
        paper_content, paper_title = FileProcessor.process_file(paper_file)
        
        # Create plan generation prompt
        prompt = create_improvement_plan_prompt(paper_content, reviews, paper_title)
        
        if verbose:
            print("Generating improvement plan with LLM...")
        
        # Make direct API call for plan generation
        plan = self._call_llm_for_task(prompt, verbose)
        
        return plan
    
    def _apply_improvements(self, paper_file: str, improvement_plan: str, verbose: bool = False) -> str:
        """Apply improvements to the paper based on the plan."""
        # Read paper content
        paper_content, paper_title = FileProcessor.process_file(paper_file)
        
        # Create revision prompt
        prompt = create_paper_revision_prompt(paper_content, improvement_plan, paper_title)
        
        if verbose:
            print("Generating improved paper with LLM...")
        
        # Make direct API call for paper revision
        improved_paper = self._call_llm_for_task(prompt, verbose)
        
        return improved_paper
    
    def _call_llm_for_task(self, prompt: str, verbose: bool = False) -> str:
        """Make a direct LLM API call for improvement tasks."""
        import requests
        import json
        
        payload = {
            "model": self.evaluator.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.evaluator.temperature,
            "max_tokens": self.evaluator.max_tokens
        }
        
        try:
            response = requests.post(
                self.evaluator.base_url,
                headers=self.evaluator.headers,
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                return f"API Error: Empty or invalid response structure"
            
            content = result['choices'][0]['message']['content']
            if not content:
                return f"API Error: Empty content returned"
            
            return content
            
        except Exception as e:
            return f"Error generating content: {str(e)}"