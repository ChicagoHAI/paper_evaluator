"""
Prompt generation module for paper evaluation.
Uses review guidelines and form to create structured prompts for LLM judges.
"""

import os
from pathlib import Path


def load_review_guidelines(guidelines_file: str = "resource/neurips_guidelines.txt") -> str:
    """Load the review guidelines from specified file path"""
    project_root = Path(__file__).parent.parent
    guidelines_path = project_root / guidelines_file
    
    with open(guidelines_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_evaluation_prompt(paper_content: str, paper_title: str = "Unknown Paper", guidelines_file: str = "resource/neurips_guidelines.txt") -> str:
    """
    Create a structured prompt for LLM-based paper evaluation.
    
    Args:
        paper_content: The full text content of the paper
        paper_title: The title of the paper (optional)
    
    Returns:
        A formatted prompt for LLM evaluation
    """
    guidelines = load_review_guidelines(guidelines_file)
    
    prompt = f"""You are an expert academic peer reviewer evaluating a research paper for a top-tier conference. Your task is to provide a thorough, constructive, and fair review following the NeurIPS review guidelines.

REVIEW GUIDELINES:
{guidelines}

PAPER TO REVIEW:
Title: {paper_title}

Content:
{paper_content}

INSTRUCTIONS:
Please provide a comprehensive review following the structure outlined in the guidelines above. Your review should include:

1. **Summary**: Briefly summarize the paper and its contributions in your own words
2. **Strengths and Weaknesses**: Provide thorough assessment covering Quality, Clarity, Significance, and Originality
3. **Quality Score** (1-4): Rate the technical soundness
4. **Clarity Score** (1-4): Rate the writing and presentation quality  
5. **Significance Score** (1-4): Rate the impact and importance
6. **Originality Score** (1-4): Rate the novelty and insights
7. **Questions**: List 3-5 key actionable questions for the authors
8. **Limitations**: Assess if limitations are adequately addressed
9. **Overall Score** (1-6): Provide final recommendation with justification
10. **Confidence Score** (1-5): Rate your confidence in the assessment

Be constructive, specific, and fair in your evaluation. Focus on helping the authors improve their work while maintaining rigorous academic standards.

REVIEW:
"""
    
    return prompt


def create_multi_judge_prompt(paper_content: str, paper_title: str = "Unknown Paper", judge_persona: str = "", guidelines_file: str = "resource/neurips_guidelines.txt") -> str:
    """
    Create a prompt for a specific judge persona.
    
    Args:
        paper_content: The full text content of the paper
        paper_title: The title of the paper
        judge_persona: Specific expertise or perspective for this judge
    
    Returns:
        A formatted prompt tailored for the specific judge
    """
    base_prompt = create_evaluation_prompt(paper_content, paper_title, guidelines_file)
    
    if judge_persona:
        persona_addition = f"""
JUDGE PERSONA: {judge_persona}
Please evaluate this paper particularly from the perspective of your expertise in {judge_persona}. While providing a complete review, pay special attention to aspects most relevant to your area of expertise.

"""
        # Insert the persona instruction after the guidelines
        parts = base_prompt.split("PAPER TO REVIEW:")
        return parts[0] + persona_addition + "PAPER TO REVIEW:" + parts[1]
    
    return base_prompt