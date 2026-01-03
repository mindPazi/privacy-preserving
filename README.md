# Privacy-Preserving Techniques for LLM Code Completion

A framework for measuring and analyzing the privacy-utility trade-off in LLM-based code completion systems.

## Overview

This project investigates how code obfuscation techniques can preserve privacy in code completion scenarios while maintaining utility. The framework provides tools to:

- Load and process code examples from the OpenAI HumanEval dataset
- Apply different levels of code obfuscation (low and high)
- Generate code completions using transformer models
- Evaluate utility (ROUGE scores) and privacy (Levenshtein distance)
- Visualize the privacy-utility trade-off

## Project Structure

```plaintext
privacy-preserving/
├── privacy_utility_experiment.ipynb  # Jupyter notebook with full experiment
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── results.json                # Experimental results
├── privacy_utility_scatter.png # Results visualization
├── docs/
│   └── structure.tex           # LaTeX documentation of project structure
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py           # HumanEval dataset loader
│   ├── obfuscation/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base obfuscator
│   │   ├── low_obfuscation.py  # Low-level obfuscation (variable renaming)
│   │   └── high_obfuscation.py # High-level obfuscation (placeholders, strip comments)
│   ├── models/
│   │   ├── __init__.py
│   │   └── code_completion.py  # Code completion model wrapper
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── utility.py          # Utility metrics (ROUGE, BLEU)
│   │   └── privacy.py          # Privacy metrics (Levenshtein distance)
│   └── visualization/
│       ├── __init__.py
│       └── plotting.py         # Privacy-utility trade-off plots
└── tests/
    ├── __init__.py
    ├── test_data.py            # Data loader tests
    ├── test_obfuscation.py     # Obfuscation tests
    └── test_evaluation.py      # Evaluation metric tests
```

## Modules

### Data (`src/data/`)

**HumanEvalDataLoader**: Loads the first N examples from the `openai/openai_humaneval` test split for experimentation.

### Obfuscation (`src/obfuscation/`)

**BaseObfuscator**: Abstract base class defining the obfuscation interface.

**LowObfuscator**: Applies minimal obfuscation:

- Renames local variables and parameters to generic names (var1, var2, etc.)
- Preserves function names and type annotations
- Removes docstrings to avoid inconsistencies

**HighObfuscator**: Applies aggressive obfuscation:

- Replaces all identifiers with placeholders (PLACEHOLDER_0, etc.)
- Strips all comments
- Removes docstrings
- Normalizes whitespace

### Models (`src/models/`)

**CodeCompletionModel**: Wrapper for HuggingFace code completion models (e.g., `Salesforce/codet5-small`).

### Evaluation (`src/evaluation/`)

**UtilityEvaluator**: Computes utility scores comparing generated completions to canonical solutions using:

- ROUGE-1, ROUGE-2, ROUGE-L scores
- BLEU score
- Exact match

**PrivacyEvaluator**: Computes privacy scores comparing obfuscated prompts to original prompts using:

- Normalized Levenshtein distance
- Jaccard distance
- Cosine distance

### Visualization (`src/visualization/`)

**PrivacyUtilityPlotter**: Creates visualizations including:

- Scatter plots of privacy vs. utility scores
- Grouped plots by obfuscation level
- Trend lines and Pareto frontiers

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd privacy-preserving

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the full experiment using the Jupyter notebook:

```bash
jupyter notebook privacy_utility_experiment.ipynb
```

Or use the modules programmatically:

```python
from src.data import HumanEvalDataLoader
from src.obfuscation import LowObfuscator, HighObfuscator
from src.models import CodeCompletionModel
from src.evaluation import UtilityEvaluator, PrivacyEvaluator

# Load data
data_loader = HumanEvalDataLoader(num_examples=20)
data_loader.load_dataset()
prompts = data_loader.get_prompts()

# Apply obfuscation
low_obf = LowObfuscator()
high_obf = HighObfuscator()
low_prompts = [low_obf.obfuscate(p) for p in prompts]
high_prompts = [high_obf.obfuscate(p) for p in prompts]

# Generate completions
model = CodeCompletionModel(model_name="Salesforce/codet5-small")
model.load_model()
completions = model.generate_completions_batch(prompts)

# Evaluate
utility_eval = UtilityEvaluator()
privacy_eval = PrivacyEvaluator()
```

## Experiment Design

The experiment follows this pipeline:

1. **Data Loading**: Load 20 examples from HumanEval test split
2. **Prompt Preparation**: For each example, prepare three versions:
   - Original prompt (no obfuscation)
   - Low-obfuscated prompt (variables renamed)
   - High-obfuscated prompt (placeholders, no comments)
3. **Completion Generation**: Generate completions using CodeT5-small (60 total)
4. **Evaluation**:
   - **Utility Score**: ROUGE-L F1 score comparing completion to canonical solution
   - **Privacy Score**: Normalized Levenshtein distance between obfuscated and original prompt
5. **Visualization**: Scatter plot showing privacy vs. utility trade-off

## Dependencies

See `requirements.txt` for the complete list of dependencies.

## License

[License information to be added]

## References

- OpenAI HumanEval Dataset: <https://github.com/openai/human-eval>
- CodeT5: <https://huggingface.co/Salesforce/codet5-small>
- ROUGE Score: <https://github.com/google-research/google-research/tree/master/rouge>
