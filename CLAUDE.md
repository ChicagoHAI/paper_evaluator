# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a paper evaluator project that implements an LLM-as-a-judge system for academic paper reviews. The project is written in Python and uses OpenRouter to access various LLM APIs for multi-judge evaluation.

## New Feature

We are going to add a new feature for improving a paper. The input is only a latex file, and it will run judges to get reviews, then it will read the reviews and the paper to determine a plan for changes, and then make changes according to the plan. This feature will have two modes. In the automatic mode, it will run this for num_rounds, default to 3. In the interactive mode, it will pause after making a plan and allow the users to review the plan.

Update the configuration file to enable this feature and update README.md after implementing this feature.

## Project Structure

* `src/` - Main source code
  * `main.py` - CLI entry point and orchestration
  * `evaluator.py` - LLM evaluation logic
  * `file_processor.py` - PDF/LaTeX file processing
  * `prompts.py` - Review prompts and templates
* `resource/` - Review guidelines and forms
* `config.yaml` - Example configuration (template)
* `config.local.yaml` - Local configuration (gitignored)
* `reviews/` - Output directory for reviews (gitignored)
* `logs/` - Prompt logs for debugging (gitignored)
* `tests/` - Sample papers for testing

## Usage

The main command-line interface accepts:
```bash
python -m src.main <paper_file> <config_file> [options]
```

Options:
* `--output/-o` - Output directory (default: reviews/)
* `--single-judge` - Use only one judge by name
* `--verbose/-v` - Enable verbose output
* `--log-prompts` - Save prompts to logs/ directory

## Configuration

The configuration file (`config.yaml`) specifies:
* `openrouter_key` - OpenRouter API key
* `judges` - List of LLM judges with model, name, and persona
* `settings` - Global settings (temperature, max_tokens, api_delay, etc.)

Example judges:
* `moonshotai/kimi-k2:free` - Kimi model
* `z-ai/glm-4.5-air:free` - GLM model

## Development Commands

* `uv run python -m src.main` - Run the evaluator
* `uv run pytest` - Run tests
* `uv run black src/` - Format code
* `uv run flake8 src/` - Lint code
