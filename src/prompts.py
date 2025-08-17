"""
Prompt generation module for paper evaluation.
Uses review guidelines and form to create structured prompts for LLM judges.
"""

import os
from pathlib import Path
from typing import Dict


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


def create_improvement_plan_prompt(paper_content: str, reviews: Dict[str, str], paper_title: str = "Unknown Paper") -> str:
    """
    Create a prompt for generating an improvement plan based on reviews.
    
    Args:
        paper_content: The full text content of the paper
        reviews: Dictionary mapping judge names to their reviews
        paper_title: Title of the paper
    
    Returns:
        A formatted prompt for generating improvement plan
    """
    reviews_text = ""
    for judge_name, review in reviews.items():
        reviews_text += f"## Review by {judge_name}\n{review}\n\n"
    
    prompt = f"""You are an expert academic writer and researcher. Your task is to analyze peer reviews of a research paper and create a detailed improvement plan.

PAPER TITLE: {paper_title}

PEER REVIEWS:
{reviews_text}

ORIGINAL PAPER:
{paper_content}

TASK:
Based on the peer reviews, create a comprehensive improvement plan for this paper. Your plan should address the major concerns and suggestions from the reviewers while maintaining the paper's core contributions.

Your improvement plan should include:

1. **Critical Issues**: List the most important problems that must be addressed
2. **Content Changes**: Specific sections that need rewriting, clarification, or expansion using existing content
3. **Structural Changes**: Any reorganization needed for better flow and clarity
4. **Technical Improvements**: Mathematical notation, algorithm descriptions, better explanation of existing methods
5. **Writing Quality**: Grammar, style, and presentation improvements
6. **Discussion Enhancements**: Better analysis of existing results and limitations

IMPORTANT CONSTRAINTS:
- DO NOT suggest adding new experimental results or data that don't exist in the paper
- Focus on improving clarity, presentation, and analysis of existing content
- Suggest reorganization and better explanation rather than new research
- Any new content should be analytical/discussion-based, not experimental

For each improvement, provide:
- Specific location in the paper (section/paragraph)
- Clear description of what needs to be changed using existing content
- Justification based on reviewer feedback
- Priority level (High/Medium/Low)

IMPROVEMENT PLAN:
"""
    
    return prompt


def create_paper_revision_prompt(paper_content: str, improvement_plan: str, paper_title: str = "Unknown Paper") -> str:
    """
    Create a prompt for revising the paper based on an improvement plan.
    
    Args:
        paper_content: The full text content of the paper
        improvement_plan: The improvement plan from previous step
        paper_title: Title of the paper
    
    Returns:
        A formatted prompt for revising the paper
    """
    prompt = f"""You are an expert academic writer and researcher. Your task is to revise a research paper based on a detailed improvement plan.

PAPER TITLE: {paper_title}

IMPROVEMENT PLAN:
{improvement_plan}

ORIGINAL PAPER:
{paper_content}

TASK:
Revise the paper according to the improvement plan. Make the changes systematically while preserving the original contributions and maintaining academic writing standards.

IMPORTANT GUIDELINES:
1. Keep the original LaTeX structure and formatting
2. Preserve all mathematical notation and references
3. Maintain the paper's core contributions and findings
4. Focus only on changes specified in the improvement plan
5. Ensure all changes improve clarity, correctness, and presentation
6. DO NOT add new experimental results, data, or claims not supported by existing content
7. DO NOT make up new numbers, statistics, or experimental findings
8. Only reorganize, clarify, and better explain existing content

REVISION CONSTRAINTS:
- Only make changes that are supported by existing text in the paper
- Improve explanations of existing methods and results
- Enhance clarity through better organization and writing
- Add analytical discussion based on existing findings
- Do not invent new experiments, datasets, or numerical results

Please provide the complete revised paper in LaTeX format. Make sure to:
- Address all high-priority items from the improvement plan using existing content
- Improve writing quality and clarity without adding unsupported claims
- Reorganize and better explain existing technical content
- Maintain proper academic tone and structure

REVISED PAPER:
"""
    
    return prompt