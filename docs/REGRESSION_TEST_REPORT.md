# PRESSURE-X 2.0 — Regression Test Report

**Date:** 2026-11-18
**Test Suite:** `tests/regression_test_suite.py`
**Status:** ALL TESTS PASSING (50/50)

## Test Coverage

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestDataLoading | 11 | All data loader functions |
| TestFiltering | 12 | All filter combinations, view filters, edge cases |
| TestScoring | 4 | Formula validation, official reproduction, sensitivity, ranking order |
| TestComparisonAndExport | 5 | Comparison data, report building, CSV export |
| TestEQBowling | 3 | Prohibited deployments, zero opportunity, EQ comparison |
| TestAIIntegration | 5 | Assistant import, system prompt, configuration, filtering, model selection |
| TestDataIntegrity | 6 | Duplicates, deduplication, cross-references, anomalies |
| TestDomesticIntelligence | 3 | Domestic metrics, competition performance, pressure metrics |

## Key Validations

### Data Loading
- All 26 data_loader functions import and execute successfully
- Pool size: 303 eligible players
- Official shortlist: 28 players
- RR Squad: 19 players

### Filtering
- All 3 view filters work (View A: 274, View B: 28, View C: 1)
- Role, nationality, score thresholds, evidence gates, search all functional
- Filter consistency verified (deterministic results)

### Scoring
- 40/30/20/10 formula validated (max diff: 0.0048)
- All 28 official scores reproduce within 0.01
- Sensitivity analysis: max rank delta = 3
- Rankings correctly sorted descending

### EQ Bowling
- 14 prohibited deployments documented
- 10 zero-opportunity players with artifact diagnoses
- Evidence-qualified comparison with ranking rationale

### AI Integration
- BackboardScoutingAssistant imports and initializes
- System prompt present (>100 chars)
- Model selection works (gemini-2.5-pro)
- Candidate filtering functional

### Data Integrity
- No duplicate player_ids in official rankings
- Player master deduplication verified (1217 unique)
- Shortlist and RR squad players in pool
- No statistical anomalies (SR <= 500, econ <= 20, wickets <= balls)

## Execution
```bash
pytest tests/regression_test_suite.py -v --tb=short
```

**Result:** 50 passed, 4 warnings (Pydantic deprecation)
