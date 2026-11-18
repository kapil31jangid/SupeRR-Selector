# Validation and Limitations
## SupeRR Selector Season 2 — Task 07M Final Audit

---

## 1. Player Identity and Dataset Traceability

All 20 finalists (10 batters + 10 bowlers) and named reserves were matched to the original supplied dataset. Key canonical player IDs verified in Task 07M:

| Player | Corrected ID | Notes |
|--------|-------------|-------|
| Simarjeet Singh | **7533** | Earlier scripts incorrectly used 1998 |
| Murugan Ashwin | **5034** | Earlier scripts incorrectly used 3807 |
| Jaydev Unadkat | **1071** | Earlier scripts incorrectly used 1991 |
| Jake Fraser-McGurk | **7341** | Alias `Jake McGurk` in raw data |

Historical scores for all finalists originate from Task 07F/07H/07J/07K outputs. No scores were modified in 07L or 07M.

---

## 2. Final Verified Rankings

### Top 10 Batters (Combined — All Tiers)

| Rank | Player | PRESSURE-X | Nationality | Tier |
|------|--------|-----------|-------------|------|
| 1 | Jake Fraser-McGurk | 91.88 | Australian | T2 |
| 2 | Jacob Bethell | 90.27 | English | T2 |
| 3 | Harry Brook | 89.42 | English | T2 |
| 4 | Pathum Nissanka | 81.13 | Sri Lankan | T3 |
| 5 | Shai Hope | 76.28 | West Indian | T3 |
| 6 | Shahrukh Khan | 73.76 | Indian | T1 |
| 7 | Rilee Rossouw | 71.41 | South African | T2 |
| 8 | Glenn Maxwell | 70.92 | Australian | T1 |
| 9 | Karun Nair | 68.41 | Indian | T2 |
| 10 | Vijay Shankar | 66.85 | Indian | T1 |

### Top 10 Bowlers (Combined — All Tiers)

| Rank | Player | PRESSURE-X | Nationality | Tier |
|------|--------|-----------|-------------|------|
| 1 | Mohammad Ghazanfar | 84.52 | Afghan | T3 |
| 2 | Tanvir Islam Mondol (a.k.a. Ripon Mondol) | 81.95 | Bangladeshi | T3 |
| 3 | Mujeeb Ur Rahman | 79.94 | Afghan | T2 |
| 4 | Harry Tector | 76.18 | Irish | T4 |
| 5 | Jason Forde (a.k.a. Matthew Forde) | 75.80 | Trinidadian | T3 |
| 6 | Ashton Agar | 74.04 | Australian | T2 |
| 7 | Ben Sears | 73.26 | New Zealander | T2 |
| 8 | Michael Bracewell | 69.48 | New Zealander | T2 |
| 9 | Sikandar Raza | 65.95 | Zimbabwean (eligible) | T3 |
| 10 | Simarjeet Singh | 65.68 | Indian | T1 |

> **Note**: Sikandar Raza's eligibility was specifically verified — he holds Zimbabwean nationality and is eligible for the IPL auction.

---

## 3. Bowling Evidence Limitations (Task 07K Audit)

The following bowlers have zero observed opportunities in one or more pressure phases. Their PRESSURE-X scores in those phases reflect shrinkage to the population mean, **not actual observed performance**:

| Bowler | Unobserved Phases | Evidence Note |
|--------|-------------------|---------------|
| Michael Bracewell | High-Extreme | 0 HE opportunities in dataset window |
| Harry Tector | High-Extreme, Death | 0 HE / 0 Death opportunities |
| Ehsan Khan | Death | 0 Death-over opportunities |
| Mohammad Ghazanfar | High-Extreme | 0 HE opportunities |

**These players are not penalised in the original rankings.** The unobserved phases are noted for transparency. An evidence-qualified re-ranking is provided in `outputs/supporting_evidence/evidence_qualified_bowler_comparison.csv`.

---

## 4. IPL Eligibility

- **184 retained players** excluded (all 10 IPL franchises). See `outputs/supporting_evidence/retained_players.csv`.
- **Pakistan-nationality players** excluded from auction pool. See `outputs/supporting_evidence/ipl_eligibility_audit.csv`.
- **Sikandar Raza**: Zimbabwe national; IPL-eligible. Verified.
- **Mujeeb Ur Rahman**: Afghanistan national; IPL-eligible. Verified.
- **Mohammad Ghazanfar**: Afghanistan national; IPL-eligible. Verified.
- **Tanvir Islam Mondol**: Bangladesh national; IPL-eligible. Verified.

---

## 5. Current-Form Limitations

Current-form assessments (Task 07J addendum, Task 07K) are based on publicly available statistics up to the research cutoff. The following caveats apply:

- Form assessments cover a 12-month preferred window (2025–26 season cycle).
- Some T3/T4 tier competitions have incomplete ball-by-ball coverage in the dataset.
- Injury status and player availability for IPL 2027 were assessed at research cutoff and may change before the auction.

---

## 6. Scoring Methodology Caveats

| Caveat | Detail |
|--------|--------|
| Shrinkage artefacts | Players with <50 qualifying deliveries in a phase show artificially stable scores |
| Competition weighting | T5 players benefit from adjusted scores but face larger uncertainty |
| Season aggregation | Multi-season eligible players use their best-qualifying season |
| Ties | Broken by total balls faced/bowled; secondary by competition tier (higher tier preferred) |

---

## 7. What Was NOT Changed in 07M

- No historical PRESSURE-X scores were modified.
- No player IDs were silently altered without documentation.
- No statistics were fabricated.
- No player was added to or removed from the final shortlist based on name recognition or fame.
- The RR scouting formula (40/30/20/10) was applied independently without altering base scores.

---

## 8. Corrections Made in 07M

| Item | Original | Corrected |
|------|----------|-----------|
| Simarjeet Singh player_id | 1998 | 7533 |
| Murugan Ashwin player_id | 3807 | 5034 |
| Jaydev Unadkat player_id | 1991 | 1071 |
| Bracewell HE phase | Marked as observed | Marked UNOBSERVED |
| Tector HE+Death phase | Marked as observed | Marked UNOBSERVED |

See `outputs/supporting_evidence/final_shortlist_corrections.csv` for the full audit trail.

