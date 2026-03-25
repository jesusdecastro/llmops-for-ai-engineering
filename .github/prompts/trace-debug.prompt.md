---
name: trace-debug
description: 'Analyze agent behavior using Langfuse traces to identify failures'
agent: 'observer'
tools:
  - search
  - read
---

# Trace Debugging Guide

Analyze the agent's behavior using Langfuse trace patterns to identify and diagnose failures.

## What to analyze

Given a description of unexpected agent behavior, systematically check:

### 1. Tool call spans
- Was `search_catalog` called when it should have been? (F4 detection)
- Did the tool return results? Check `results_count` in metadata. (F1 detection)
- Was `get_faq_answer` called for FAQ-related queries?

### 2. Response vs source data
- Does the agent's answer contain product details not in the tool's response? (F1 hallucination)
- Does the answer include information beyond the FAQ data? (F2 extrapolation)

### 3. Scope boundaries
- Did the agent answer a question outside TechShop electronics? (F3 scope creep)
- Was the response correctly classified as `out_of_scope`?

### 4. Guardrail traces
- Were `scan_input` and `scan_output` spans present?
- What did `is_safe` / `is_valid` return?

### 5. Token and latency patterns
- Are `input_tokens` and `output_tokens` within expected ranges?
- Is `latency_ms` reasonable for the query complexity?

## Output

Provide a structured diagnosis:
1. **Observed behavior**: what happened
2. **Root cause**: which failure mode (F1/F2/F3/F4) and why
3. **Evidence**: trace spans and metadata that confirm the diagnosis
4. **Fix recommendation**: specific code or prompt change to address it
