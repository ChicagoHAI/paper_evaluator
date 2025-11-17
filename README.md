# Paper Evaluator

An LLM-powered paper evaluation system that provides structured peer reviews following academic conference guidelines. The system uses multiple LLM judges via OpenRouter API to evaluate research papers in PDF or LaTeX format.

## Features

- **Multi-format support**: Process PDF and LaTeX files
- **Multiple LLM judges**: Use different models with specialized personas
- **Structured evaluation**: Follows NeurIPS review guidelines
- **Comprehensive scoring**: Quality, Clarity, Significance, and Originality ratings
- **Batch processing**: Evaluate with multiple judges simultaneously
- **Paper improvement**: Iterative self-improvement based on LLM reviews
- **Interactive mode**: Review improvement plans before applying changes
- **Automatic mode**: Multi-round improvement without user intervention

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd paper_evaluator
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```
   
   This will install the project dependencies and make the `paper_evaluator` command available via `uv run`.

3. Set up your configuration:
   ```bash
   cp config.yaml config.local.yaml
   # Edit config.local.yaml and add your OpenRouter API key
   ```

## Configuration

1. Get an API key from [OpenRouter](https://openrouter.ai/)
2. Edit `config.local.yaml` and replace `"sk-or-v1-your-actual-api-key-here"` with your actual API key
3. Customize judges and their personas as needed

The configuration includes two free models by default:
- `deepseek/kimi-k2:free` - Specialized in ML and AI systems
- `zhipuai/glm-4.5-air:free` - Specialized in NLP and computational linguistics

## Usage

### Basic Usage

Evaluate a paper with all configured judges:
```bash
uv run paper_evaluator paper.pdf config.local.yaml
```

Or equivalently:
```bash
source .venv/bin/activate
paper_evaluator paper.pdf config.local.yaml
```

### Advanced Options

```bash
# Specify output directory
uv run paper_evaluator paper.tex config.local.yaml --output my_reviews/

# Use only a single judge
uv run paper_evaluator paper.pdf config.local.yaml --single-judge "Kimi"

# Enable verbose output
uv run paper_evaluator paper.pdf config.local.yaml --verbose

# Save prompts to logs/ directory for inspection
uv run paper_evaluator paper.pdf config.local.yaml --log-prompts

# Combine options
uv run paper_evaluator paper.pdf config.local.yaml --output reviews/ --verbose --log-prompts
```

### Paper Improvement

Automatically improve a LaTeX paper based on LLM reviews:

```bash
# Automatic improvement (3 rounds by default)
uv run paper_evaluator paper.tex config.local.yaml --improve

# Automatic improvement with custom rounds
uv run paper_evaluator paper.tex config.local.yaml --improve --rounds 5

# Interactive improvement (pause for plan review)
uv run paper_evaluator paper.tex config.local.yaml --improve --interactive

# Combine with other options
uv run paper_evaluator paper.tex config.local.yaml --improve --interactive --verbose
```

### Output

The system generates:
- **Reviews**: Individual review files: `paper_name.judge_name.review.txt`
- **Summary**: Summary file (multi-judge): `paper_name.summary.txt`
- **Improvements**: Improved papers in `improvements/session_timestamp/`
- **Plans**: Improvement plans: `round_N_plan.txt`
- **Logs**: Prompt logs (if enabled): `logs/{timestamp}_{paper}_{model}_{persona}.prompt.txt`

Each review includes:
- Paper summary and key contributions
- Strengths and weaknesses analysis
- Numerical ratings (1-4) for Quality, Clarity, Significance, Originality  
- Overall recommendation (1-6) with confidence score
- Actionable questions for authors
- Assessment of limitations

### Testing

Test with the sample paper:
```bash
uv run paper_evaluator tests/sample_paper.tex config.local.yaml --verbose --log-prompts
```

## Project Structure

```
paper_evaluator/
├── src/
│   ├── main.py              # Command-line interface
│   ├── evaluator.py         # LLM evaluation logic
│   ├── file_processor.py    # PDF/LaTeX processing
│   ├── prompts.py           # Prompt generation
│   └── improver.py          # Paper improvement logic
├── resource/
│   └── neurips_guidelines.txt # NeurIPS review guidelines
├── config.yaml              # Example configuration
├── config.local.yaml        # Local configuration (with API key)
└── pyproject.toml           # Project dependencies
```

## Development

Run tests (when available):
```bash
uv run pytest
```

Format code:
```bash
uv run black src/
```

Lint code:
```bash
uv run flake8 src/
```

## Requirements

- Python 3.8+
- OpenRouter API key
- For PDF processing: PyPDF2
- For LaTeX processing: Basic text processing (included)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{paper_evaluator,
  title = {Paper Evaluator},
  author = {Chenhao Tan},
  year = {2025},
  url = {https://github.com/yourusername/paper_evaluator}
}
```