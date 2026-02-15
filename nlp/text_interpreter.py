"""
NLP Text Interpreter for the AI NutriCare System.

This module provides AI/NLP-based interpretation of doctor notes and prescriptions
using GPT-4 (primary) with fallback to BERT-based NER models. It converts qualitative
medical guidance into actionable diet rules.

Requirements: 7.1, 7.2
"""

import json
import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from ai_diet_planner.models import (
    TextualNote,
    DietRule,
    DietaryRestriction,
    RulePriority,
)

# Ambiguous instruction flag
AMBIGUOUS_FLAG = "[MANUAL_REVIEW_REQUIRED]"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NLPBackend(Enum):
    """Available NLP backend models."""
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    GROQ = "groq"
    BERT = "bert"


class NLPTextInterpreter:
    """
    Interprets doctor notes and prescriptions using AI/NLP to extract actionable diet rules.
    
    Uses GPT-4 as the primary model with prompt engineering for medical context,
    and falls back to BERT-based NER model if GPT-4 is unavailable.
    
    Attributes:
        model: The NLP model to use (gpt-4, gpt-3.5-turbo, bert)
        temperature: Temperature setting for GPT models (0.3 for consistency)
        cache: Cache for common note patterns (24-hour TTL)
    """
    
    def __init__(
        self,
        model: str = "groq",
        api_key: Optional[str] = None,
        temperature: float = 0.3,
        enable_cache: bool = True
    ):
        """
        Initialize NLP Text Interpreter.
        
        Args:
            model: NLP model to use ("gpt-4", "gpt-3.5-turbo", "groq", "bert")
            api_key: API key (OpenAI or Groq, reads from env var if not provided)
            temperature: Temperature for LLM models (default 0.3 for consistent outputs)
            enable_cache: Whether to enable caching for common patterns
        """
        self.model = model
        self.temperature = temperature
        self.enable_cache = enable_cache
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Initialize Groq client if using Groq
        self.groq_client = None
        if model == "groq":
            try:
                from groq import Groq
                self.api_key = api_key or os.getenv("GROQ_API_KEY")
                if not self.api_key:
                    logger.warning(
                        "Groq API key not provided. Will fall back to BERT model."
                    )
                    self.model = "bert"
                else:
                    self.groq_client = Groq(api_key=self.api_key)
                    logger.info(f"Initialized NLP Text Interpreter with Groq (llama-3.3-70b)")
            except ImportError:
                logger.warning(
                    "Groq library not installed. Install with: pip install groq"
                )
                logger.warning("Falling back to BERT model.")
                self.model = "bert"
        
        # Initialize OpenAI client if using GPT models
        self.openai_client = None
        if model in ["gpt-4", "gpt-3.5-turbo"]:
            try:
                import openai
                self.api_key = api_key or os.getenv("OPENAI_API_KEY")
                if not self.api_key:
                    logger.warning(
                        "OpenAI API key not provided. Will fall back to BERT model."
                    )
                    self.model = "bert"
                else:
                    self.openai_client = openai.OpenAI(api_key=self.api_key)
                    logger.info(f"Initialized NLP Text Interpreter with {model}")
            except ImportError:
                logger.warning(
                    "OpenAI library not installed. Falling back to BERT model."
                )
                self.model = "bert"
        
        # Initialize BERT model only if explicitly requested
        self.bert_model = None
        if self.model == "bert":
            logger.info("BERT model will be initialized on first use (lazy loading)")
            # Don't initialize BERT here - do it lazily when needed
    
    def _initialize_bert_model(self):
        """Initialize BERT-based NER model for fallback (lazy loading)."""
        if self.bert_model is not None:
            return  # Already initialized
            
        try:
            from transformers import pipeline
            logger.info("Initializing BERT-based NER model (this may take a moment)...")
            # Use a medical NER model fine-tuned on medical text
            self.bert_model = pipeline(
                "ner",
                model="d4data/biomedical-ner-all",
                aggregation_strategy="simple"
            )
            logger.info("BERT model initialized successfully")
        except ImportError:
            logger.error(
                "Transformers library not installed. BERT fallback unavailable."
            )
            self.bert_model = None
        except Exception as e:
            logger.error(f"Failed to initialize BERT model: {e}")
            self.bert_model = None
    
    def interpret_notes(self, notes: List[TextualNote]) -> List[DietRule]:
        """
        Convert textual notes to actionable diet rules.
        
        Args:
            notes: List of doctor notes and prescriptions
            
        Returns:
            List of diet rules with priority levels
            
        Raises:
            ValueError: If notes list is empty
            RuntimeError: If both GPT and BERT models fail
        """
        if not notes:
            raise ValueError("Notes list cannot be empty")
        
        logger.info(f"Interpreting {len(notes)} textual notes")
        
        # Combine notes into single text for processing
        combined_text = self._combine_notes(notes)
        
        # Check cache first
        if self.enable_cache:
            cached_result = self._get_from_cache(combined_text)
            if cached_result:
                logger.info("Retrieved result from cache")
                return cached_result
        
        # Process with primary model
        try:
            if self.model == "groq" and self.groq_client:
                diet_rules = self._interpret_with_groq(combined_text, notes)
            elif self.model in ["gpt-4", "gpt-3.5-turbo"] and self.openai_client:
                diet_rules = self._interpret_with_gpt(combined_text, notes)
            else:
                diet_rules = self._interpret_with_bert(combined_text, notes)
            
            # Cache the result
            if self.enable_cache:
                self._add_to_cache(combined_text, diet_rules)
            
            logger.info(f"Successfully extracted {len(diet_rules)} diet rules")
            return diet_rules
            
        except Exception as e:
            logger.error(f"Primary model failed: {e}")
            # Try fallback to BERT if LLM failed
            if self.model != "bert":
                logger.info("Attempting fallback to BERT model")
                try:
                    if not self.bert_model:
                        self._initialize_bert_model()
                    if self.bert_model:
                        return self._interpret_with_bert(combined_text, notes)
                except Exception as bert_error:
                    logger.error(f"BERT fallback also failed: {bert_error}")
            
            raise RuntimeError(
                f"Failed to interpret notes with both primary and fallback models: {e}"
            )
    
    def _combine_notes(self, notes: List[TextualNote]) -> str:
        """Combine multiple notes into a single text for processing."""
        combined = []
        for note in notes:
            section_header = f"[{note.section.upper()}]"
            combined.append(f"{section_header}\n{note.content}")
        return "\n\n".join(combined)
    
    def _interpret_with_gpt(
        self,
        combined_text: str,
        notes: List[TextualNote]
    ) -> List[DietRule]:
        """
        Interpret notes using GPT-4 with medical prompt engineering.
        
        Uses few-shot learning with example medical notes for better accuracy.
        """
        prompt = self._build_gpt_prompt(combined_text)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=2000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            diet_rules = self._parse_gpt_response(content)
            
            return diet_rules
            
        except Exception as e:
            logger.error(f"GPT API call failed: {e}")
            raise
    
    def _interpret_with_groq(
        self,
        combined_text: str,
        notes: List[TextualNote]
    ) -> List[DietRule]:
        """
        Interpret notes using Groq (llama-3.3-70b) with medical prompt engineering.
        
        Uses few-shot learning with example medical notes for better accuracy.
        """
        prompt = self._build_gpt_prompt(combined_text)  # Same prompt format works for Groq
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Groq's fastest model
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=2000
            )
            
            # Parse the response (same format as GPT)
            content = response.choices[0].message.content
            diet_rules = self._parse_gpt_response(content)
            
            return diet_rules
            
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for GPT with medical context."""
        return """You are a medical AI assistant specialized in dietary guidance. 
Your task is to extract dietary guidelines from doctor's notes and prescriptions.

You must identify:
1. Strict restrictions (allergies, medical contraindications) - REQUIRED priority
2. Recommended foods and nutrients - RECOMMENDED priority
3. Foods to avoid or limit - REQUIRED or RECOMMENDED based on severity
4. Portion size guidance - RECOMMENDED priority

Format your response as a JSON array of diet rules with this structure:
{
  "rule_text": "Clear description of the dietary guideline",
  "priority": "REQUIRED|RECOMMENDED|OPTIONAL",
  "food_categories": ["proteins", "carbs", "fats", "dairy", "vegetables", "fruits"],
  "action": "include|exclude|limit",
  "source": "nlp_extraction"
}

IMPORTANT: If instructions are ambiguous or contradictory, flag them by:
1. Setting the rule_text to start with "[MANUAL_REVIEW_REQUIRED]"
2. Including a description of the ambiguity or contradiction
3. Setting priority to "OPTIONAL" to prevent automatic application

Be precise and medically accurate."""
    
    def _build_gpt_prompt(self, combined_text: str) -> str:
        """Build the user prompt with few-shot examples."""
        examples = self._get_few_shot_examples()
        
        prompt = f"""Extract dietary guidelines from the following medical notes.

{examples}

Now extract dietary guidelines from these notes:

{combined_text}

Provide the output as a JSON array of diet rules."""
        
        return prompt
    
    def _get_few_shot_examples(self) -> str:
        """Get few-shot learning examples for better accuracy."""
        return """Example 1:
Input: "Patient has diabetes. Avoid sugar and refined carbohydrates. Include high-fiber foods."
Output: [
  {
    "rule_text": "Avoid sugar and refined carbohydrates",
    "priority": "REQUIRED",
    "food_categories": ["carbs", "sweets"],
    "action": "exclude",
    "source": "nlp_extraction"
  },
  {
    "rule_text": "Include high-fiber foods",
    "priority": "RECOMMENDED",
    "food_categories": ["vegetables", "fruits", "whole_grains"],
    "action": "include",
    "source": "nlp_extraction"
  }
]

Example 2:
Input: "Patient allergic to peanuts. Reduce sodium intake for hypertension."
Output: [
  {
    "rule_text": "Strict peanut allergy - exclude all peanut products",
    "priority": "REQUIRED",
    "food_categories": ["nuts", "proteins"],
    "action": "exclude",
    "source": "nlp_extraction"
  },
  {
    "rule_text": "Reduce sodium intake for blood pressure control",
    "priority": "REQUIRED",
    "food_categories": ["all"],
    "action": "limit",
    "source": "nlp_extraction"
  }
]"""
    
    def _parse_gpt_response(self, content: str) -> List[DietRule]:
        """Parse GPT response into DietRule objects."""
        try:
            # Extract JSON from response (handle markdown code blocks)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            rules_data = json.loads(content)
            
            # Convert to DietRule objects
            diet_rules = []
            for rule_data in rules_data:
                try:
                    priority_str = rule_data.get("priority", "RECOMMENDED").upper()
                    priority = RulePriority[priority_str]
                    
                    diet_rule = DietRule(
                        rule_text=rule_data["rule_text"],
                        priority=priority,
                        food_categories=rule_data.get("food_categories", []),
                        action=rule_data.get("action", "limit"),
                        source=rule_data.get("source", "nlp_extraction")
                    )
                    diet_rules.append(diet_rule)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid rule: {e}")
                    continue
            
            return diet_rules
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            logger.debug(f"Response content: {content}")
            # Return empty list rather than failing completely
            return []
    
    def _interpret_with_bert(
        self,
        combined_text: str,
        notes: List[TextualNote]
    ) -> List[DietRule]:
        """
        Interpret notes using BERT-based NER model as fallback.
        
        This is a simpler rule-based approach using entity recognition.
        """
        if not self.bert_model:
            logger.warning("BERT model not available, using basic rule extraction")
            return self._basic_rule_extraction(combined_text)
        
        try:
            # Use BERT NER to extract entities
            entities = self.bert_model(combined_text)
            
            # Convert entities to diet rules using heuristics
            diet_rules = self._entities_to_diet_rules(entities, combined_text)
            
            return diet_rules
            
        except Exception as e:
            logger.error(f"BERT processing failed: {e}")
            return self._basic_rule_extraction(combined_text)
    
    def _entities_to_diet_rules(
        self,
        entities: List[Dict],
        text: str
    ) -> List[DietRule]:
        """Convert BERT entities to diet rules using heuristics."""
        diet_rules = []
        text_lower = text.lower()
        
        # Extract conditions and medications
        conditions = []
        for entity in entities:
            if entity.get("entity_group") in ["Disease", "Condition"]:
                conditions.append(entity["word"].lower())
        
        # Check for ambiguous or contradictory instructions
        ambiguous_rules = self._detect_ambiguous_instructions(text_lower)
        diet_rules.extend(ambiguous_rules)
        
        # Apply condition-based rules
        if any(cond in ["diabetes", "diabetic", "glucose"] for cond in conditions):
            diet_rules.append(DietRule(
                rule_text="Limit sugar and refined carbohydrates for diabetes management",
                priority=RulePriority.REQUIRED,
                food_categories=["carbs", "sweets"],
                action="limit",
                source="nlp_extraction"
            ))
        
        if any(cond in ["hypertension", "blood pressure", "bp"] for cond in conditions):
            diet_rules.append(DietRule(
                rule_text="Reduce sodium intake for blood pressure control",
                priority=RulePriority.REQUIRED,
                food_categories=["all"],
                action="limit",
                source="nlp_extraction"
            ))
        
        if any(cond in ["cholesterol", "hyperlipidemia", "lipid"] for cond in conditions):
            diet_rules.append(DietRule(
                rule_text="Limit saturated fats and cholesterol",
                priority=RulePriority.REQUIRED,
                food_categories=["fats", "proteins"],
                action="limit",
                source="nlp_extraction"
            ))
        
        # Check for allergy keywords
        if "allerg" in text_lower:
            # Try to extract allergen
            import re
            allergy_pattern = r"allerg(?:y|ic) to ([a-z\s]+)"
            matches = re.findall(allergy_pattern, text_lower)
            for allergen in matches:
                allergen = allergen.strip()
                diet_rules.append(DietRule(
                    rule_text=f"Strict allergy: exclude {allergen}",
                    priority=RulePriority.REQUIRED,
                    food_categories=["all"],
                    action="exclude",
                    source="nlp_extraction"
                ))
        
        # If no rules extracted, add a general healthy diet rule
        if not diet_rules:
            diet_rules.append(DietRule(
                rule_text="Follow general healthy diet guidelines",
                priority=RulePriority.RECOMMENDED,
                food_categories=["all"],
                action="include",
                source="nlp_extraction"
            ))
        
        return diet_rules
    
    def _basic_rule_extraction(self, text: str) -> List[DietRule]:
        """
        Basic rule extraction using keyword matching.
        
        This is the most basic fallback when no AI models are available.
        """
        diet_rules = []
        text_lower = text.lower()
        
        # Check for ambiguous or contradictory instructions first
        ambiguous_rules = self._detect_ambiguous_instructions(text_lower)
        diet_rules.extend(ambiguous_rules)
        
        # Keyword-based extraction
        keywords_to_rules = {
            ("diabetes", "glucose", "sugar"): DietRule(
                rule_text="Limit sugar intake for diabetes management",
                priority=RulePriority.REQUIRED,
                food_categories=["carbs", "sweets"],
                action="limit",
                source="nlp_extraction"
            ),
            ("hypertension", "blood pressure", "bp"): DietRule(
                rule_text="Reduce sodium for blood pressure control",
                priority=RulePriority.REQUIRED,
                food_categories=["all"],
                action="limit",
                source="nlp_extraction"
            ),
            ("cholesterol", "lipid"): DietRule(
                rule_text="Limit saturated fats and cholesterol",
                priority=RulePriority.REQUIRED,
                food_categories=["fats"],
                action="limit",
                source="nlp_extraction"
            ),
            ("obese", "obesity", "overweight"): DietRule(
                rule_text="Control portion sizes and reduce caloric intake",
                priority=RulePriority.RECOMMENDED,
                food_categories=["all"],
                action="limit",
                source="nlp_extraction"
            ),
        }
        
        for keywords, rule in keywords_to_rules.items():
            if any(keyword in text_lower for keyword in keywords):
                diet_rules.append(rule)
        
        # Default rule if nothing found
        if not diet_rules:
            diet_rules.append(DietRule(
                rule_text="Follow balanced diet with variety of nutrients",
                priority=RulePriority.RECOMMENDED,
                food_categories=["all"],
                action="include",
                source="nlp_extraction"
            ))
        
        return diet_rules
    
    def _detect_ambiguous_instructions(self, text: str) -> List[DietRule]:
        """
        Detect ambiguous or contradictory dietary instructions.
        
        Args:
            text: Lowercased text to analyze
            
        Returns:
            List of DietRule objects flagged for manual review
        """
        ambiguous_rules = []
        
        # Pattern 1: Contradictory include/exclude for same food
        # e.g., "include dairy" and "avoid dairy" in same text
        contradictory_patterns = [
            (r"(include|eat|consume).*dairy", r"(avoid|exclude|no).*dairy"),
            (r"(include|eat|consume).*sugar", r"(avoid|exclude|no).*sugar"),
            (r"(include|eat|consume).*carb", r"(avoid|exclude|no|limit).*carb"),
            (r"(include|eat|consume).*fat", r"(avoid|exclude|no|limit).*fat"),
            (r"(include|eat|consume).*meat", r"(avoid|exclude|no).*meat"),
        ]
        
        import re
        for include_pattern, exclude_pattern in contradictory_patterns:
            if re.search(include_pattern, text) and re.search(exclude_pattern, text):
                # Extract the food item
                food_match = re.search(r"(dairy|sugar|carb|fat|meat)", text)
                food_item = food_match.group(1) if food_match else "food item"
                
                ambiguous_rules.append(DietRule(
                    rule_text=f"{AMBIGUOUS_FLAG} Contradictory instructions about {food_item}: both include and exclude mentioned",
                    priority=RulePriority.OPTIONAL,
                    food_categories=["all"],
                    action="limit",
                    source="nlp_extraction"
                ))
        
        # Pattern 2: Vague or unclear quantities
        # e.g., "some sugar", "moderate amounts", "occasionally"
        vague_patterns = [
            r"some\s+\w+",
            r"moderate\s+amount",
            r"occasionally",
            r"maybe",
            r"possibly",
            r"consider",
            r"might want to",
        ]
        
        for pattern in vague_patterns:
            if re.search(pattern, text):
                ambiguous_rules.append(DietRule(
                    rule_text=f"{AMBIGUOUS_FLAG} Vague or unclear dietary instruction detected - requires clarification",
                    priority=RulePriority.OPTIONAL,
                    food_categories=["all"],
                    action="limit",
                    source="nlp_extraction"
                ))
                break  # Only flag once for vague instructions
        
        # Pattern 3: Conflicting medical conditions
        # e.g., instructions for both low-carb (diabetes) and high-carb (athletic) diets
        if ("low carb" in text or "reduce carb" in text) and ("high carb" in text or "increase carb" in text):
            ambiguous_rules.append(DietRule(
                rule_text=f"{AMBIGUOUS_FLAG} Conflicting carbohydrate recommendations detected",
                priority=RulePriority.OPTIONAL,
                food_categories=["carbs"],
                action="limit",
                source="nlp_extraction"
            ))
        
        # Pattern 4: Unclear allergy information
        # e.g., "possible allergy", "suspected intolerance"
        if re.search(r"(possible|suspected|maybe|might be).*?(allerg|intoleran)", text):
            ambiguous_rules.append(DietRule(
                rule_text=f"{AMBIGUOUS_FLAG} Unclear allergy/intolerance information - requires confirmation",
                priority=RulePriority.OPTIONAL,
                food_categories=["all"],
                action="exclude",
                source="nlp_extraction"
            ))
        
        return ambiguous_rules
    
    def extract_restrictions(self, notes: List[TextualNote]) -> List[DietaryRestriction]:
        """
        Extract strict dietary restrictions (allergies, intolerances).
        
        Args:
            notes: List of textual notes
            
        Returns:
            List of dietary restrictions
        """
        # First get all diet rules
        diet_rules = self.interpret_notes(notes)
        
        # Filter for REQUIRED priority rules that exclude foods
        restrictions = []
        for rule in diet_rules:
            if rule.priority == RulePriority.REQUIRED and rule.action == "exclude":
                # Determine restriction type
                restriction_type = "medical"
                if "allerg" in rule.rule_text.lower():
                    restriction_type = "allergy"
                elif "intoleran" in rule.rule_text.lower():
                    restriction_type = "intolerance"
                
                restriction = DietaryRestriction(
                    restriction_type=restriction_type,
                    restricted_items=rule.food_categories,
                    severity="strict"
                )
                restrictions.append(restriction)
        
        return restrictions
    
    def extract_recommendations(self, notes: List[TextualNote]) -> List[str]:
        """
        Extract dietary recommendations and preferences.
        
        Args:
            notes: List of textual notes
            
        Returns:
            List of recommendation strings
        """
        # Get all diet rules
        diet_rules = self.interpret_notes(notes)
        
        # Filter for RECOMMENDED priority rules
        recommendations = []
        for rule in diet_rules:
            if rule.priority == RulePriority.RECOMMENDED:
                recommendations.append(rule.rule_text)
        
        return recommendations
    
    def resolve_conflicts(self, rules: List[DietRule]) -> List[DietRule]:
        """
        Resolve conflicting diet rules using medical priority.
        
        Priority hierarchy: REQUIRED > RECOMMENDED > OPTIONAL
        More specific rules override general rules.
        
        Args:
            rules: List of potentially conflicting diet rules
            
        Returns:
            List of resolved diet rules
        """
        if not rules:
            return []
        
        # Sort by priority (REQUIRED first)
        priority_order = {
            RulePriority.REQUIRED: 0,
            RulePriority.RECOMMENDED: 1,
            RulePriority.OPTIONAL: 2
        }
        sorted_rules = sorted(rules, key=lambda r: priority_order[r.priority])
        
        # Track conflicts by food category and action
        resolved = []
        seen_conflicts = {}
        
        for rule in sorted_rules:
            # Create a conflict key
            for category in rule.food_categories:
                conflict_key = (category, rule.action)
                
                if conflict_key not in seen_conflicts:
                    # First rule for this category/action combination
                    seen_conflicts[conflict_key] = rule
                else:
                    # Conflict detected - keep higher priority rule
                    existing_rule = seen_conflicts[conflict_key]
                    if priority_order[rule.priority] < priority_order[existing_rule.priority]:
                        # New rule has higher priority
                        seen_conflicts[conflict_key] = rule
                        logger.info(
                            f"Conflict resolved: '{rule.rule_text}' overrides "
                            f"'{existing_rule.rule_text}' due to higher priority"
                        )
        
        # Collect unique resolved rules
        resolved = list(seen_conflicts.values())
        
        # Remove duplicates
        unique_rules = []
        seen_texts = set()
        for rule in resolved:
            if rule.rule_text not in seen_texts:
                seen_texts.add(rule.rule_text)
                unique_rules.append(rule)
        
        return unique_rules
    
    def _get_from_cache(self, key: str) -> Optional[List[DietRule]]:
        """Get result from cache if not expired (24-hour TTL)."""
        if key not in self.cache:
            return None
        
        # Check if cache entry is expired (24 hours)
        timestamp = self.cache_timestamps.get(key)
        if timestamp:
            age = datetime.now() - timestamp
            if age.total_seconds() > 86400:  # 24 hours
                # Expired, remove from cache
                del self.cache[key]
                del self.cache_timestamps[key]
                return None
        
        return self.cache[key]
    
    def _add_to_cache(self, key: str, value: List[DietRule]):
        """Add result to cache with timestamp."""
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.now()
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("Cache cleared")
    
    def is_flagged_for_review(self, rule: DietRule) -> bool:
        """
        Check if a diet rule is flagged for manual review.
        
        Args:
            rule: DietRule to check
            
        Returns:
            True if the rule requires manual review, False otherwise
        """
        return rule.rule_text.startswith(AMBIGUOUS_FLAG)
