# Contributing to Paper Evaluator

Thank you for your interest in contributing to the Paper Evaluator project!

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/paper_evaluator.git
   cd paper_evaluator
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ChicagoHAI/paper_evaluator.git
   ```
4. Install dependencies:
   ```bash
   uv sync
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure they follow the project guidelines

3. Run tests (if available):
   ```bash
   uv run pytest
   ```

4. Format your code:
   ```bash
   uv run black src/
   ```

5. Lint your code:
   ```bash
   uv run flake8 src/
   ```

6. Commit your changes:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Open a pull request against the main repository

## Code Style

- Follow PEP 8 Python style guidelines
- Use Black for code formatting
- Include docstrings for all functions and classes
- Keep functions focused and concise

## Adding New Features

When adding new features:

1. Update the README.md with usage examples
2. Add tests if applicable
3. Update config.yaml if new configuration options are needed
4. Document any new command-line arguments

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Any relevant error messages or logs

## Pull Request Guidelines

- Keep changes focused and atomic
- Write clear commit messages
- Update documentation as needed
- Ensure all tests pass
- Add yourself to the contributors list if this is your first contribution

## Questions?

Feel free to open an issue for any questions or clarifications.
