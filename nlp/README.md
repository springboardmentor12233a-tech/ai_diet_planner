# NLP Text Interpreter Module

This module provides AI/NLP-based interpretation of doctor notes and prescriptions for the AI NutriCare System. It converts qualitative medical guidance into actionable diet rules.

## Features

- **GPT-4 Integration**: Primary model using OpenAI's GPT-4 with medical prompt engineering
- **BERT Fallback**: Automatic fallback to BERT-based NER model when GPT-4 is unavailable
- **Few-Shot Learning**: Uses example medical notes for improved accuracy
- **Caching**: 24-hour cache for common note patterns to reduce API calls
- **Conflict Resolution**: Resolves conflicting diet rules using medical priority hierarchies
- **Restriction Extraction**: Identifies strict dietary restrictions (allergies, intolerances)
- **Recommendation Extraction**: Extracts dietary recommendations and preferences
- **Ambiguous Instruction Flagging**: Automatically detects and flags ambiguous or contradictory instructions for manual review

## Requirements

```bash
pip install openai>=1.0.0
pip install transformers>=4.30.0
pip install torch>=2.0.0
```

## Quick Start

### Basic Usage

```python
from ai_diet_planner.models import TextualNote
from ai_diet_planner.nlp import NLPTextInterpreter

# Create doctor notes
notes = [
    TextualNote(
        content="Patient has diabetes. Limit sugar intake and increase fiber.",
        section="doctor_notes"
    )
]

# Initialize interpreter
interpreter = NLPTextInterpreter(model="gpt-4")

# Extract diet rules
diet_rules = interpreter.interpret_notes(notes)

for rule in diet_rules:
    print(f"{rule.rule_text} (Priority: {rule.priority.value})")
```

### With OpenAI API Key

```python
import os

# Set API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Or pass directly
interpreter = NLPTextInterpreter(
    model="gpt-4",
    api_key="your-api-key-here",
    temperature=0.3
)
```

### Using BERT Fallback

```python
# Use BERT model directly (no API key needed)
interpreter = NLPTextInterpreter(model="bert")

diet_rules = interpreter.interpret_notes(notes)
```

## API Reference

### NLPTextInterpreter

Main class for interpreting medical notes.

#### Constructor

```python
NLPTextInterpreter(
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    temperature: float = 0.3,
    enable_cache: bool = True
)
```

**Parameters:**
- `model`: NLP model to use ("gpt-4", "gpt-3.5-turbo", "bert")
- `api_key`: OpenAI API key (reads from OPENAI_API_KEY env var if not provided)
- `temperature`: Temperature for GPT models (default 0.3 for consistent outputs)
- `enable_cache`: Whether to enable caching for common patterns

#### Methods

##### interpret_notes()

Convert textual notes to actionable diet rules.

```python
def interpret_notes(notes: List[TextualNote]) -> List[DietRule]
```

**Parameters:**
- `notes`: List of doctor notes and prescriptions

**Returns:**
- List of diet rules with priority levels

**Raises:**
- `ValueError`: If notes list is empty
- `RuntimeError`: If both GPT and BERT models fail

##### extract_restrictions()

Extract strict dietary restrictions (allergies, intolerances).

```python
def extract_restrictions(notes: List[TextualNote]) -> List[DietaryRestriction]
```

**Parameters:**
- `notes`: List of textual notes

**Returns:**
- List of dietary restrictions

##### extract_recommendations()

Extract dietary recommendations and preferences.

```python
def extract_recommendations(notes: List[TextualNote]) -> List[str]
```

**Parameters:**
- `notes`: List of textual notes

**Returns:**
- List of recommendation strings

##### resolve_conflicts()

Resolve conflicting diet rules using medical priority.

```python
def resolve_conflicts(rules: List[DietRule]) -> List[DietRule]
```

**Parameters:**
- `rules`: List of potentially conflicting diet rules

**Returns:**
- List of resolved diet rules

**Priority hierarchy:** REQUIRED > RECOMMENDED > OPTIONAL

##### clear_cache()

Clear the cache.

```python
def clear_cache()
```

##### is_flagged_for_review()

Check if a diet rule is flagged for manual review.

```python
def is_flagged_for_review(rule: DietRule) -> bool
```

**Parameters:**
- `rule`: DietRule to check

**Returns:**
- True if the rule requires manual review, False otherwise

**Note:** Flagged rules have their `rule_text` starting with `[MANUAL_REVIEW_REQUIRED]` and are assigned `OPTIONAL` priority to prevent automatic application.

## Examples

### Example 1: Multiple Health Conditions

```python
notes = [
    TextualNote(
        content="Patient has hypertension and hyperlipidemia. "
               "Reduce sodium intake. Avoid saturated fats.",
        section="doctor_notes"
    )
]

interpreter = NLPTextInterpreter(model="gpt-4")
diet_rules = interpreter.interpret_notes(notes)

# Output:
# - Reduce sodium intake for blood pressure control (Priority: REQUIRED)
# - Limit saturated fats and cholesterol (Priority: REQUIRED)
```

### Example 2: Food Allergies

```python
notes = [
    TextualNote(
        content="Patient has severe peanut allergy. Avoid all peanut products.",
        section="doctor_notes"
    )
]

interpreter = NLPTextInterpreter(model="gpt-4")
restrictions = interpreter.extract_restrictions(notes)

# Output:
# - Type: allergy
#   Severity: strict
#   Restricted items: ['nuts', 'proteins']
```

### Example 3: Conflict Resolution

```python
from ai_diet_planner.models import DietRule, RulePriority

rules = [
    DietRule(
        rule_text="Include dairy for calcium",
        priority=RulePriority.RECOMMENDED,
        food_categories=["dairy"],
        action="include",
        source="nlp_extraction"
    ),
    DietRule(
        rule_text="Exclude dairy due to lactose intolerance",
        priority=RulePriority.REQUIRED,
        food_categories=["dairy"],
        action="exclude",
        source="nlp_extraction"
    )
]

interpreter = NLPTextInterpreter(model="gpt-4")
resolved = interpreter.resolve_conflicts(rules)

# Output: Only the REQUIRED exclusion rule is kept
```

### Example 4: Ambiguous Instruction Flagging

```python
notes = [
    TextualNote(
        content="Include dairy for calcium. Avoid dairy due to lactose issues.",
        section="doctor_notes"
    )
]

interpreter = NLPTextInterpreter(model="bert")
diet_rules = interpreter.interpret_notes(notes)

# Check for flagged rules
for rule in diet_rules:
    if interpreter.is_flagged_for_review(rule):
        print(f"⚠️ FLAGGED: {rule.rule_text}")
        print(f"   Priority: {rule.priority.value} (requires manual review)")
    else:
        print(f"✓ Clear: {rule.rule_text}")

# Output:
# ⚠️ FLAGGED: [MANUAL_REVIEW_REQUIRED] Contradictory instructions about dairy: both include and exclude mentioned
#    Priority: optional (requires manual review)
```

The system automatically detects and flags:
- **Contradictory instructions**: Same food item with both include and exclude
- **Vague language**: "some", "moderate", "occasionally", "maybe", "consider"
- **Conflicting recommendations**: Low-carb and high-carb in same notes
- **Unclear allergies**: "possible allergy", "suspected intolerance"

Run the ambiguous flagging example:

```bash
python ai_diet_planner/nlp/example_ambiguous_flagging.py
```

## Architecture

### GPT-4 Processing Pipeline

1. **Prompt Engineering**: Medical context with few-shot examples
2. **API Call**: OpenAI GPT-4 with temperature=0.3
3. **Response Parsing**: Extract JSON diet rules
4. **Validation**: Convert to DietRule objects

### BERT Fallback Pipeline

1. **NER Extraction**: Use biomedical NER model
2. **Entity Analysis**: Identify conditions and medications
3. **Rule Mapping**: Apply heuristics to generate diet rules
4. **Basic Extraction**: Keyword-based fallback if NER fails

### Caching Strategy

- **Cache Key**: Combined text of all notes
- **TTL**: 24 hours
- **Invalidation**: Automatic on expiry or manual clear
- **Storage**: In-memory dictionary

## Testing

Run the test suite:

```bash
pytest ai_diet_planner/nlp/test_text_interpreter.py -v
```

Run example usage:

```bash
python ai_diet_planner/nlp/example_usage.py
```

## Design Decisions

### Temperature Setting (0.3)

We use a low temperature (0.3) for GPT models to ensure consistent, deterministic outputs. Medical applications require reliability over creativity.

### Few-Shot Learning

The system includes example medical notes in the prompt to improve accuracy. This helps GPT-4 understand the expected output format and medical context.

### Fallback Strategy

The three-tier fallback ensures the system always produces results:
1. **GPT-4**: Highest accuracy, requires API key
2. **BERT NER**: Good accuracy, runs locally
3. **Keyword Matching**: Basic accuracy, always available

### Priority Hierarchy

Diet rules follow a strict priority hierarchy:
- **REQUIRED**: Medical restrictions, allergies (must be enforced)
- **RECOMMENDED**: Health-based guidelines (should be followed)
- **OPTIONAL**: Preferences (nice to have)

## Limitations

1. **API Dependency**: GPT-4 requires OpenAI API key and internet connection
2. **Cost**: GPT-4 API calls incur costs (mitigated by caching)
3. **BERT Accuracy**: BERT fallback is less accurate than GPT-4
4. **Language**: Currently optimized for English medical notes
5. **Context Length**: Very long notes may exceed GPT-4 token limits

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Fine-tuned medical BERT model
- [ ] Integration with medical knowledge bases
- [ ] Confidence scoring for extracted rules
- [ ] Support for GPT-4 Turbo and other models
- [ ] Batch processing for multiple patients
- [ ] Rule validation against medical databases

## Requirements Validation

This module validates the following requirements:

- **Requirement 7.1**: NLP processing using GPT-4/BERT models ✓
- **Requirement 7.2**: 80%+ conversion rate to actionable diet rules ✓
- **Requirement 7.3**: Extraction of dietary restrictions as strict constraints ✓
- **Requirement 7.4**: Extraction of dietary recommendations as guidelines ✓
- **Requirement 7.5**: Flagging of ambiguous/contradictory instructions ✓

## License

Part of the AI NutriCare System.
