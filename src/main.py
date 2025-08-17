#!/usr/bin/env python3
"""
Main module for paper evaluation system.
Handles command-line interface and orchestrates the evaluation process.
"""

import argparse
import yaml
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .file_processor import FileProcessor
from .evaluator import LLMEvaluator


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def save_review(review_content: str, output_path: str, judge_name: str = None):
    """Save review to file."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Add header with metadata
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"""# Paper Review
Generated: {timestamp}
Judge: {judge_name or 'Default'}
{"="*50}

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + review_content)
    
    print(f"Review saved to: {output_path}")


def main():
    """Main entry point for the paper evaluator."""
    parser = argparse.ArgumentParser(
        description="LLM-based paper evaluation system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main paper.pdf config.yaml
  python -m src.main paper.tex config.local.yaml --output reviews/
  python -m src.main paper.pdf config.yaml --single-judge "Claude"
        """
    )
    
    parser.add_argument(
        "paper_file",
        help="Path to the paper file (PDF or LaTeX)"
    )
    
    parser.add_argument(
        "config_file", 
        help="Path to the configuration YAML file"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="reviews",
        help="Output directory for review files (default: reviews/)"
    )
    
    parser.add_argument(
        "--single-judge",
        help="Use only a single judge by name from config"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--log-prompts",
        action="store_true",
        help="Save prompts to logs/ directory for inspection"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.verbose:
            print(f"Loading configuration from: {args.config_file}")
        config = load_config(args.config_file)
        
        # Process paper file
        if args.verbose:
            print(f"Processing paper file: {args.paper_file}")
        paper_content, paper_title = FileProcessor.process_file(args.paper_file)
        
        # Clean content for evaluation
        clean_content = FileProcessor.clean_text_for_evaluation(paper_content)
        
        if args.verbose:
            print(f"Paper title: {paper_title}")
            print(f"Content length: {len(clean_content)} characters")
        
        # Get API key
        api_key = config.get('openrouter_key')
        if not api_key:
            raise ValueError("OpenRouter API key not found in configuration")
        
        # Prepare judges
        judges = config.get('judges', [])
        if not judges:
            raise ValueError("No judges configured")
        
        # Filter to single judge if requested
        if args.single_judge:
            judges = [j for j in judges if j.get('name') == args.single_judge]
            if not judges:
                raise ValueError(f"Judge '{args.single_judge}' not found in configuration")
        
        # Prepare output directory
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        
        # Generate base filename from paper file
        paper_name = Path(args.paper_file).stem
        
        # Get settings from config
        settings = config.get('settings', {})
        temperature = settings.get('temperature', 0.1)
        max_tokens = settings.get('max_tokens', 4000)
        api_delay = settings.get('api_delay', 1.0)
        
        # Check if prompt logging is enabled (from config or command line)
        log_prompts = args.log_prompts or settings.get('log_prompts', False)
        
        # Get guidelines file path from config
        guidelines_file = config.get('guidelines_file', 'resource/neurips_guidelines.txt')
        
        # Create evaluator and run evaluations
        evaluator = LLMEvaluator(api_key, temperature=temperature, max_tokens=max_tokens, log_prompts=log_prompts)
        
        if len(judges) == 1:
            # Single judge evaluation
            judge = judges[0]
            judge_name = judge.get('name', 'default')
            review = evaluator.evaluate_paper(
                clean_content, 
                paper_title, 
                judge.get('persona', ''),
                guidelines_file
            )
            
            output_file = output_dir / f"{paper_name}.{judge_name}.review.txt"
            save_review(review, str(output_file), judge_name)
            
        else:
            # Multi-judge evaluation
            if args.verbose:
                print(f"Running evaluation with {len(judges)} judges...")
            
            reviews = evaluator.batch_evaluate(
                clean_content, 
                paper_title, 
                judges,
                delay=api_delay,
                guidelines_file=guidelines_file
            )
            
            # Save individual reviews
            for judge_name, review in reviews.items():
                output_file = output_dir / f"{paper_name}.{judge_name}.review.txt"
                save_review(review, str(output_file), judge_name)
            
            # Create summary file
            summary_file = output_dir / f"{paper_name}.summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Multi-Judge Review Summary\n")
                f.write(f"Paper: {paper_title}\n")
                f.write(f"Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Judges: {', '.join(reviews.keys())}\n\n")
                
                for judge_name, review in reviews.items():
                    f.write(f"## {judge_name} Review\n")
                    f.write(f"See: {paper_name}.{judge_name}.review.txt\n\n")
            
            print(f"Summary saved to: {summary_file}")
        
        print("Evaluation completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()