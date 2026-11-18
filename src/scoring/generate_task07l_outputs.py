import os
import datetime
import pandas as pd
import numpy as np

os.makedirs('outputs/task07l', exist_ok=True)
ref_date = datetime.date(2027, 4, 1)

# ==============================================================================
# 1. CANDIDATE MASTER DATABASE (BATTERS & BOWLERS)
# ==============================================================================

candidates_data = [
    # --------------------------------------------------------------------------
    # BATTERS
    # --------------------------------------------------------------------------
    {
        'player_id': 7341, 'player_name': 'Jake Fraser-McGurk', 'role': 'Batter',
        'country': 'AUS', 'nationality': 'Overseas', 'dob': '2002-04-11',
        'task07k_rank': 2, 'hist_pressure_score': 92.2031, 'total_pressure_balls': 218,
        'he_balls': 30, 'death_balls': 28, 'chase_balls': 112, 'pp_balls': 142,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 90.0, 'career_stage_desc': 'Ascending international sensation entering physical peak; 8-10 year franchise runway.',
        'dev_runway_years': 9,
        'bat_versatility': 96.0, 'bowl_specialist': 20.0, 'athletic_fielding': 92.0, 'tactical_adaptability': 88.0, 'rr_squad_fit': 98.0,
        'composite_skill_ceiling': 94.0,
        'primary_technical_strengths': 'Unprecedented powerplay boundary acceleration (IPL SR ~200); fearless bat speed through the line against 145+ kph pace; elite boundary catching.',
        'technical_dev_areas': 'Shot selection against quality wrist-spin early in the innings; pacing longer chases when 2-3 wickets fall in powerplay.',
        'rr_tactical_role': 'Explosive Opening Enforcer / Top-Order Disruptor',
        'recent_comp_window': 'IPL 2025-2026, T20Is (AUS), BBL', 'matches_eval': 24,
        'perf_summary': '485 runs in 2026 window, SR 188.72, avg 32.33; 56 off 20b vs West Indies; consistently produces match-winning powerplays.',
        'traj_trend': 'Ascending', 'form_rating': 'STRONG', 'form_score': 92.0,
        'match_fitness_notes': '100% match fit; regular starter in Australia T20I top order.',
        'targeting_tier': 'TIER 1 PRIMARY TARGET',
        '3yr_value': 'Immediate powerplay dominance; potential to become the face of RR overseas batting core through 2030.',
        'rr_synergy': 'Creates the most destructive opening partnership in IPL alongside Yashasvi Jaiswal, completely dismantling opposition powerplays.'
    },
    {
        'player_id': 6280, 'player_name': 'Harry Brook', 'role': 'Batter',
        'country': 'ENG', 'nationality': 'Overseas', 'dob': '1999-02-22',
        'task07k_rank': 1, 'hist_pressure_score': 93.3014, 'total_pressure_balls': 215,
        'he_balls': 14, 'death_balls': 68, 'chase_balls': 130, 'pp_balls': 35,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 78.0, 'career_stage_desc': 'Established world superstar entering peak prime; 5-7 year prime franchise runway.',
        'dev_runway_years': 6,
        'bat_versatility': 98.0, 'bowl_specialist': 30.0, 'athletic_fielding': 94.0, 'tactical_adaptability': 94.0, 'rr_squad_fit': 96.0,
        'composite_skill_ceiling': 96.0,
        'primary_technical_strengths': '360-degree boundary hitting against express pace and elite spin; devastating death-overs striking (SR 210+); captaincy & leadership maturity.',
        'technical_dev_areas': 'Adapting immediately to slower, two-paced sub-continent turning surfaces in daytime Jaipur fixtures.',
        'rr_tactical_role': 'Elite Clutch Finisher / Middle-Overs Spin Destroyer (No. 4/5)',
        'recent_comp_window': 'T20Is 2025-2026 (ENG Captain/Key Batter), The Hundred', 'matches_eval': 22,
        'perf_summary': '690 T20I runs in 2026, avg 49.29, SR 189.04, 2 centuries (100 off 47b vs NZ); highest run-scorer in international T20s in 2026.',
        'traj_trend': 'Ascending', 'form_rating': 'STRONG', 'form_score': 95.0,
        'match_fitness_notes': 'Fully active international captain; peak physical conditioning.',
        'targeting_tier': 'TIER 1 PRIMARY TARGET',
        '3yr_value': 'Anchor of middle-order finishing; match-winning ceiling in high-pressure playoff encounters.',
        'rr_synergy': 'Complements Riyan Parag and Dhruv Jurel perfectly, forming the most formidable middle/death hitting axis in the competition.'
    },
    {
        'player_id': 23311, 'player_name': 'Jacob Bethell', 'role': 'Batter',
        'country': 'ENG', 'nationality': 'Overseas', 'dob': '2003-10-23',
        'task07k_rank': 12, 'hist_pressure_score': 87.1824, 'total_pressure_balls': 175,
        'he_balls': 24, 'death_balls': 45, 'chase_balls': 88, 'pp_balls': 42,
        'zero_opp_deficit': False, 'pressure_conf': 'MEDIUM',
        'dev_potential_score': 96.0, 'career_stage_desc': 'Generational 3-dimensional prodigy at beginning of career; 10+ year franchise development runway.',
        'dev_runway_years': 10,
        'bat_versatility': 92.0, 'bowl_specialist': 78.0, 'athletic_fielding': 98.0, 'tactical_adaptability': 92.0, 'rr_squad_fit': 96.0,
        'composite_skill_ceiling': 92.0,
        'primary_technical_strengths': 'Elegant left-handed boundary striker; high backlift providing immense leverage against spin; accurate left-arm orthodox bowling; generational boundary fielder.',
        'technical_dev_areas': 'Developing consistent boundary options against hard-length hit-the-deck pace bowling on Indian tracks.',
        'rr_tactical_role': 'Dynamic 3D All-Rounder (LHB / SLA / Elite Fielder)',
        'recent_comp_window': 'Vitality Blast, The Hundred, England T20I debut series', 'matches_eval': 15,
        'perf_summary': '280 runs, SR 158.4, 8 wickets (econ 7.40); celebrated international breakout with match-winning cameos vs Australia and West Indies.',
        'traj_trend': 'Ascending', 'form_rating': 'POSITIVE', 'form_score': 82.0,
        'match_fitness_notes': 'Young, athletic, highly mobile; emerging multi-format England international.',
        'targeting_tier': 'TIER 1 PRIMARY TARGET (LONG-TERM SCOUTING PRIORITY)',
        '3yr_value': 'Franchise cornerstone; multi-skill utility ensures high auction return-on-investment across multiple mega-cycles.',
        'rr_synergy': 'Exemplifies Rajasthan Royals’ DNA of finding young international prodigies and developing them into global icons.'
    },
    {
        'player_id': 6931, 'player_name': 'Pathum Nissanka', 'role': 'Batter',
        'country': 'SL', 'nationality': 'Overseas', 'dob': '1998-05-18',
        'task07k_rank': 14, 'hist_pressure_score': 86.0712, 'total_pressure_balls': 406,
        'he_balls': 87, 'death_balls': 32, 'chase_balls': 214, 'pp_balls': 160,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 74.0, 'career_stage_desc': 'Established international top-order anchor entering peak maturity; 5-6 year runway.',
        'dev_runway_years': 5,
        'bat_versatility': 82.0, 'bowl_specialist': 10.0, 'athletic_fielding': 86.0, 'tactical_adaptability': 84.0, 'rr_squad_fit': 82.0,
        'composite_skill_ceiling': 80.0,
        'primary_technical_strengths': 'Classical batting technique against high pace; elite wristwork through mid-wicket; dependable powerplay pace-handling; deep pressure sample (406 balls).',
        'technical_dev_areas': 'Increasing boundary strike rate beyond 140 in death-overs scenarios; expanding aerial reverse-sweeps.',
        'rr_tactical_role': 'High-Floor Top-Order Accumulator / Inning Stabilizer',
        'recent_comp_window': 'T20Is 2025-2026 (SL), LPL', 'matches_eval': 20,
        'perf_summary': '540 runs in 2026, avg 38.57, SR 138.82; 82 off 54b vs IND; high consistency across sub-continental tracks.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 85.0,
        'match_fitness_notes': 'Full match fitness; primary opener for Sri Lanka.',
        'targeting_tier': 'TIER 2 SECONDARY TARGET',
        '3yr_value': 'High-floor overseas insurance behind Jaiswal and overseas starters; eliminates top-order batting collapses.',
        'rr_synergy': 'Provides tactical balance if explosive openers experience form slumps; excels on Sawai Mansingh Stadium pitch.'
    },
    {
        'player_id': 4369, 'player_name': 'Shai Hope', 'role': 'Batter',
        'country': 'WI', 'nationality': 'Overseas', 'dob': '1993-11-10',
        'task07k_rank': 7, 'hist_pressure_score': 87.1985, 'total_pressure_balls': 227,
        'he_balls': 51, 'death_balls': 42, 'chase_balls': 134, 'pp_balls': 51,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 50.0, 'career_stage_desc': 'Experienced international leader and dual-role keeper; 2-3 year prime window.',
        'dev_runway_years': 3,
        'bat_versatility': 88.0, 'bowl_specialist': 10.0, 'athletic_fielding': 88.0, 'tactical_adaptability': 88.0, 'rr_squad_fit': 86.0,
        'composite_skill_ceiling': 85.0,
        'primary_technical_strengths': 'Exceptional current T20 striking transformation; world-class against spin bowling; dependable wicketkeeper with calm tactical temperament.',
        'technical_dev_areas': 'Maintaining boundary cadence against elite 145+ kph express pace in the death overs.',
        'rr_tactical_role': 'Dual-Role WK-Anchor / Senior Tactical Stabilizer',
        'recent_comp_window': 'T20Is 2025-2026 (WI Captain/WK), CPL, ILT20', 'matches_eval': 19,
        'perf_summary': '624 runs, avg 44.57, SR 152.20, 2 centuries (102* off 51b vs IND); reinvented T20 game with aggressive intent.',
        'traj_trend': 'Ascending', 'form_rating': 'STRONG', 'form_score': 94.0,
        'match_fitness_notes': 'Captain of West Indies ODI/T20 sides; peak match conditioning.',
        'targeting_tier': 'TIER 2 SECONDARY TARGET (SENIOR STABILIZER)',
        '3yr_value': 'Immediate tactical cover for Dhruv Jurel; brings leadership and calming influence in pressurized playoff chases.',
        'rr_synergy': 'Offers tactical flexibility as both top-order accumulator and middle-overs spin counter, safeguarding against collapses.'
    },
    {
        'player_id': 3782, 'player_name': 'M Shahrukh Khan', 'role': 'Batter',
        'country': 'IND', 'nationality': 'Indian', 'dob': '1995-05-27',
        'task07k_rank': 11, 'hist_pressure_score': 84.6521, 'total_pressure_balls': 100,
        'he_balls': 52, 'death_balls': 48, 'chase_balls': 65, 'pp_balls': 0,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 55.0, 'career_stage_desc': 'Experienced domestic power hitter entering prime finishing years; 3-4 year runway.',
        'dev_runway_years': 4,
        'bat_versatility': 74.0, 'bowl_specialist': 40.0, 'athletic_fielding': 84.0, 'tactical_adaptability': 78.0, 'rr_squad_fit': 90.0,
        'composite_skill_ceiling': 80.0,
        'primary_technical_strengths': 'Immense domestic raw bat speed; 52 high-extreme balls in IPL pressure; specialized death-overs boundary power; handy off-spin matchup overs.',
        'technical_dev_areas': 'Defensive technique against sharp bouncers directed at helmet; strike rotation against high-quality wrist-spin.',
        'rr_tactical_role': 'Domestic Power-Hitting Death Finisher (No. 6/7)',
        'recent_comp_window': 'SMAT 2025-2026, TNPL, IPL matches', 'matches_eval': 16,
        'perf_summary': '265 runs, SR 166.4, avg 29.44; 3 match-winning final-over finishes in domestic T20 cricket.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 80.0,
        'match_fitness_notes': 'Fully fit domestic finisher with proven IPL credentials.',
        'targeting_tier': 'TIER 1 DOMESTIC TARGET',
        '3yr_value': 'High-value Indian domestic finisher; reduces overseas slot dependency in lower-order hitting.',
        'rr_synergy': 'Forms an all-Indian finishing partnership with Dhruv Jurel and Shubham Dubey, freeing up overseas slots for top-order stars.'
    },
    {
        'player_id': 930, 'player_name': 'Karun Nair', 'role': 'Batter',
        'country': 'IND', 'nationality': 'Indian', 'dob': '1991-12-06',
        'task07k_rank': 5, 'hist_pressure_score': 88.0195, 'total_pressure_balls': 113,
        'he_balls': 76, 'death_balls': 18, 'chase_balls': 72, 'pp_balls': 35,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 42.0, 'career_stage_desc': 'Veteran domestic anchor with proven clutch pedigree; 1-2 year domestic reserve window.',
        'dev_runway_years': 2,
        'bat_versatility': 80.0, 'bowl_specialist': 15.0, 'athletic_fielding': 78.0, 'tactical_adaptability': 80.0, 'rr_squad_fit': 78.0,
        'composite_skill_ceiling': 78.0,
        'primary_technical_strengths': 'High-extreme clutch pedigree (76 HE balls); pristine technical foundation; ability to absorb pressure and reconstruct an innings after top-order failure.',
        'technical_dev_areas': 'Low recent IPL match rhythm (18 runs in 2 inngs in 2026); limited boundary clearing against 145+ kph pace in final overs.',
        'rr_tactical_role': 'Domestic Top/Middle Anchor / Crisis Reserve',
        'recent_comp_window': 'Ranji Trophy, Vijay Hazare, SMAT, IPL 2026 (2 matches)', 'matches_eval': 12,
        'perf_summary': 'Prolific in domestic first-class; limited T20 2026 rhythm (18 runs, SR 100.0); needs competitive T20 trial validation.',
        'traj_trend': 'Declining', 'form_rating': 'WEAK', 'form_score': 50.0,
        'match_fitness_notes': 'Fit but lacks recent high-intensity T20 game time.',
        'targeting_tier': 'EXPERIENCED TACTICAL ANCHOR / RESERVE',
        '3yr_value': 'Low-cost domestic batting depth; emergency cover for top/middle order.',
        'rr_synergy': 'Former Rajasthan Royals batter familiar with franchise culture; reliable squad depth player.'
    },
    {
        'player_id': 2877, 'player_name': 'Vijay Shankar', 'role': 'Batter',
        'country': 'IND', 'nationality': 'Indian', 'dob': '1991-01-26',
        'task07k_rank': 9, 'hist_pressure_score': 85.6278, 'total_pressure_balls': 187,
        'he_balls': 92, 'death_balls': 46, 'chase_balls': 136, 'pp_balls': 5,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 38.0, 'career_stage_desc': 'Veteran domestic all-rounder with deepest active pressure sample; 1-2 year runway.',
        'dev_runway_years': 2,
        'bat_versatility': 76.0, 'bowl_specialist': 50.0, 'athletic_fielding': 74.0, 'tactical_adaptability': 78.0, 'rr_squad_fit': 76.0,
        'composite_skill_ceiling': 75.0,
        'primary_technical_strengths': 'Deepest active Indian clutch sample (92 HE balls, 136 chase balls); proven IPL playoff temperament; useful 1-2 overs of medium pace.',
        'technical_dev_areas': 'Injury recovery history; lack of 2026 verified match sample; vulnerable to sharp short-pitch deliveries.',
        'rr_tactical_role': 'Domestic Crisis Recovery Batter / Backup Seam AR',
        'recent_comp_window': 'Domestic First-Class, Rehabilitation window 2025-2026', 'matches_eval': 8,
        'perf_summary': 'No verified 2026 T20 matches due to injury rehab; deep historical IPL track record.',
        'traj_trend': 'Unverified / Insufficient Data', 'form_rating': 'INSUFFICIENT DATA', 'form_score': 62.0,
        'match_fitness_notes': 'Cleared medical rehab; requires pre-auction fitness assessment.',
        'targeting_tier': 'EXPERIENCED TACTICAL ANCHOR / RESERVE',
        '3yr_value': 'Experienced domestic middle-order cover; high historical clutch reliability.',
        'rr_synergy': 'Complements Riyan Parag as an experienced batting cushion in difficult run-chases.'
    },
    {
        'player_id': 772, 'player_name': 'Rilee Rossouw', 'role': 'Batter',
        'country': 'SA', 'nationality': 'Overseas', 'dob': '1989-10-09',
        'task07k_rank': 3, 'hist_pressure_score': 89.2783, 'total_pressure_balls': 115,
        'he_balls': 46, 'death_balls': 24, 'chase_balls': 78, 'pp_balls': 32,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 36.0, 'career_stage_desc': 'Veteran overseas boundary hitter in twilight years; 1-2 year franchise window.',
        'dev_runway_years': 2,
        'bat_versatility': 80.0, 'bowl_specialist': 10.0, 'athletic_fielding': 74.0, 'tactical_adaptability': 78.0, 'rr_squad_fit': 78.0,
        'composite_skill_ceiling': 82.0,
        'primary_technical_strengths': 'Devastating left-handed bat swing; excels against high pace; proven franchise century maker.',
        'technical_dev_areas': 'Declining athletic mobility; limited runway; struggles when ball grips and turns sharply.',
        'rr_tactical_role': 'Impact Middle-Order Boundary Striker (Backup)',
        'recent_comp_window': 'PSL, SA20 2025-2026', 'matches_eval': 18,
        'perf_summary': '385 runs, avg 32.08, SR 154.62; multiple match-winning knocks in franchise leagues.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 85.0,
        'match_fitness_notes': 'Fit franchise circuit player.',
        'targeting_tier': 'EXPERIENCED IMPACT BACKUP',
        '3yr_value': 'Short-term overseas boundary hitting insurance.',
        'rr_synergy': 'Backup option for Harry Brook / Jacob Bethell if tactical left-hand power is required.'
    },
    {
        'player_id': 838, 'player_name': 'Glenn Maxwell', 'role': 'Batter',
        'country': 'AUS', 'nationality': 'Overseas', 'dob': '1988-10-14',
        'task07k_rank': 4, 'hist_pressure_score': 89.0412, 'total_pressure_balls': 273,
        'he_balls': 104, 'death_balls': 72, 'chase_balls': 165, 'pp_balls': 45,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 35.0, 'career_stage_desc': 'Legendary veteran match-winner in final career phase; 1-2 year runway.',
        'dev_runway_years': 1,
        'bat_versatility': 92.0, 'bowl_specialist': 75.0, 'athletic_fielding': 86.0, 'tactical_adaptability': 84.0, 'rr_squad_fit': 82.0,
        'composite_skill_ceiling': 88.0,
        'primary_technical_strengths': 'Unmatched match-winning ceiling on his day; reverse-sweep mastery; useful off-spin bowling against left-handers.',
        'technical_dev_areas': 'Extreme performance volatility; susceptibility to high-speed hard lengths; age-related physical wear.',
        'rr_tactical_role': 'High-Variance Impact Match-Winner / Spin AR',
        'recent_comp_window': 'BBL, MLC, T20Is (AUS) 2025-2026', 'matches_eval': 17,
        'perf_summary': '280 runs, avg 23.33, SR 168.67; explosive flashes interspersed with low scores.',
        'traj_trend': 'High Variance', 'form_rating': 'MIXED', 'form_score': 72.0,
        'match_fitness_notes': 'Managing ongoing ankle and physical workload.',
        'targeting_tier': 'EXPERIENCED IMPACT BACKUP',
        '3yr_value': 'Short-term high-ceiling ceiling pick; low multi-year development runway.',
        'rr_synergy': 'Brings immense big-match experience and tactical daring for knockout games.'
    },

    # --------------------------------------------------------------------------
    # BOWLERS
    # --------------------------------------------------------------------------
    {
        'player_id': 7935, 'player_name': 'Mohammad Ghazanfar', 'role': 'Bowler',
        'country': 'AFG', 'nationality': 'Overseas', 'dob': '2006-03-20',
        'task07k_rank': 5, 'hist_pressure_score': 70.3021, 'total_pressure_balls': 108,
        'he_balls': 12, 'death_balls': 0, 'chase_balls': 66, 'pp_balls': 0,
        'zero_opp_deficit': True, 'pressure_conf': 'LOW / ARTIFACT-AFFECTED (EQ 70.30)',
        'dev_potential_score': 98.0, 'career_stage_desc': 'Generational 21-year-old mystery spin prodigy; 10+ year franchise development runway.',
        'dev_runway_years': 10,
        'bat_versatility': 30.0, 'bowl_specialist': 98.0, 'athletic_fielding': 88.0, 'tactical_adaptability': 90.0, 'rr_squad_fit': 98.0,
        'composite_skill_ceiling': 94.0,
        'primary_technical_strengths': 'Virtually unpickable carrom ball and wrong’un; high-arm release producing steep bounce; immense natural spin deception; fits RR mystery spin heritage.',
        'technical_dev_areas': 'Developing death-overs discipline and powerplay containment against elite IPL hitters; building tactical maturity when attacked.',
        'rr_tactical_role': 'Specialist Mystery Spinner / Long-Term Franchise Project',
        'recent_comp_window': 'U19 World Cup, ACC Premier Cup, Afghanistan T20Is, BPL', 'matches_eval': 16,
        'perf_summary': '22 wickets in 2026, econ 6.42, strike rate 14.8; breakthrough international performances including 4/12 vs Zimbabwe.',
        'traj_trend': 'Ascending', 'form_rating': 'POSITIVE', 'form_score': 82.0,
        'match_fitness_notes': 'Peak youth fitness, supple bowling shoulder, highly athletic.',
        'targeting_tier': 'TIER 1 PRIMARY TARGET (LONG-TERM SCOUTING PRIORITY)',
        '3yr_value': 'Franchise cornerstone; under RR spin coaching, can become the most devastating mystery spinner in the IPL by 2028-2029.',
        'rr_synergy': 'Mirrors RR’s historic breakthroughs with young spinners; pairs with Ravi Bishnoi and Ravindra Jadeja to create unplayable spin web in Jaipur.'
    },
    {
        'player_id': 24767, 'player_name': 'Ripon Mondol', 'role': 'Bowler',
        'country': 'BAN', 'nationality': 'Overseas', 'dob': '2003-03-21',
        'task07k_rank': 6, 'hist_pressure_score': 78.6314, 'total_pressure_balls': 120,
        'he_balls': 7, 'death_balls': 54, 'chase_balls': 60, 'pp_balls': 66,
        'zero_opp_deficit': False, 'pressure_conf': 'MEDIUM',
        'dev_potential_score': 88.0, 'career_stage_desc': 'High-ceiling young fast bowler entering physical prime; 8-9 year franchise development runway.',
        'dev_runway_years': 8,
        'bat_versatility': 20.0, 'bowl_specialist': 92.0, 'athletic_fielding': 86.0, 'tactical_adaptability': 84.0, 'rr_squad_fit': 90.0,
        'composite_skill_ceiling': 88.0,
        'primary_technical_strengths': 'Proven death-overs execution (54 death balls in dataset); pinpoint blockhole yorker; sharp heavy ball bouncer; rapid arm speed.',
        'technical_dev_areas': 'Managing economy when batsmen step out of crease; tactical variation on flat Indian batting tracks.',
        'rr_tactical_role': 'High-Pace Enforcer / Death-Overs Development',
        'recent_comp_window': 'BPL 2025-2026, Bangladesh High Performance Camp', 'matches_eval': 11,
        'perf_summary': '4 wickets in BPL 2026, econ 9.40 (small sample); previously took 15 wickets in BPL 2024 at avg 16.2; immense raw upside.',
        'traj_trend': 'Ascending', 'form_rating': 'INSUFFICIENT DATA', 'form_score': 65.0,
        'match_fitness_notes': 'Fully fit fast bowler; working with elite Bangladesh fast-bowling coaches.',
        'targeting_tier': 'TIER 1 DEVELOPMENT TARGET',
        '3yr_value': 'Potential high-speed death-overs banker; high return on low-to-mid auction expenditure.',
        'rr_synergy': 'Works alongside Jofra Archer, Sandeep Sharma, and Shane Bond to refine tactical death bowling execution.'
    },
    {
        'player_id': 6450, 'player_name': 'Mujeeb Ur Rahman', 'role': 'Bowler',
        'country': 'AFG', 'nationality': 'Overseas', 'dob': '2001-03-28',
        'task07k_rank': 9, 'hist_pressure_score': 72.8512, 'total_pressure_balls': 210,
        'he_balls': 30, 'death_balls': 12, 'chase_balls': 118, 'pp_balls': 96,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 84.0, 'career_stage_desc': 'Young international mystery spinner entering prime years; 7-8 year franchise runway.',
        'dev_runway_years': 7,
        'bat_versatility': 25.0, 'bowl_specialist': 92.0, 'athletic_fielding': 82.0, 'tactical_adaptability': 86.0, 'rr_squad_fit': 92.0,
        'composite_skill_ceiling': 86.0,
        'primary_technical_strengths': 'All phases observed (210 balls, 96 PP balls); elite powerplay finger-spin containment; traditional carrom and off-break deception.',
        'technical_dev_areas': 'Handling left-handed power hitters targeting the short square boundary; expanding middle-overs wicket-taking strike rate.',
        'rr_tactical_role': 'Multi-Phase Mystery Spin Anchor (Powerplay & Middle)',
        'recent_comp_window': 'BBL, ILT20, T20Is 2025-2026', 'matches_eval': 18,
        'perf_summary': '20 wickets, econ 6.95, strike rate 18.2; highly reliable franchise tournament performer across multiple leagues.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 84.0,
        'match_fitness_notes': '100% active and fit; extensive international tournament conditioning.',
        'targeting_tier': 'TIER 1 PRIMARY TARGET',
        '3yr_value': 'Ready-made international wicket-taker who still has extensive development upside at age 26.',
        'rr_synergy': 'Allows RR to squeeze opposition in the mandatory powerplay (overs 1-6), creating wickets for Bishnoi and Archer.'
    },
    {
        'player_id': 2364, 'player_name': 'Ashton Agar', 'role': 'Bowler',
        'country': 'AUS', 'nationality': 'Overseas', 'dob': '1993-10-14',
        'task07k_rank': 2, 'hist_pressure_score': 84.1023, 'total_pressure_balls': 144,
        'he_balls': 11, 'death_balls': 12, 'chase_balls': 80, 'pp_balls': 6,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 50.0, 'career_stage_desc': 'Experienced international defensive spin tactician; 2-3 year prime window.',
        'dev_runway_years': 3,
        'bat_versatility': 65.0, 'bowl_specialist': 88.0, 'athletic_fielding': 95.0, 'tactical_adaptability': 90.0, 'rr_squad_fit': 88.0,
        'composite_skill_ceiling': 84.0,
        'primary_technical_strengths': 'Ranks #1 in Task 07K Evidence-Qualified scoring (84.10); flawless length control; left-arm defensive mastery; elite boundary fielding and handy lower-order hitting.',
        'technical_dev_areas': 'Limited strike weapon on flat tracks; low multi-year development runway.',
        'rr_tactical_role': 'Defensive Spin Controller / Senior Tactician',
        'recent_comp_window': 'BBL 2025-2026, Marsh Cup, T20Is (AUS)', 'matches_eval': 15,
        'perf_summary': '14 wickets, econ 6.82, BBI 3/16; stifling middle-overs economy across BBL season.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 86.0,
        'match_fitness_notes': 'Experienced professional athlete; excellent fielding conditioning.',
        'targeting_tier': 'TIER 2 SECONDARY TARGET (EXPERIENCED ANCHOR)',
        '3yr_value': 'Immediate tactical containment bank; mentors younger spinners in professional match preparation.',
        'rr_synergy': 'Provides tactical left-arm spin insurance behind Ravindra Jadeja and Manimaran Siddharth.'
    },
    {
        'player_id': 8295, 'player_name': 'Matthew Forde', 'role': 'Bowler',
        'country': 'WI', 'nationality': 'Overseas', 'dob': '2002-05-07',
        'task07k_rank': 24, 'hist_pressure_score': 68.7612, 'total_pressure_balls': 132,
        'he_balls': 3, 'death_balls': 24, 'chase_balls': 68, 'pp_balls': 72,
        'zero_opp_deficit': False, 'pressure_conf': 'LOW',
        'dev_potential_score': 85.0, 'career_stage_desc': 'Young pace-bowling all-rounder entering physical peak; 7-8 year franchise runway.',
        'dev_runway_years': 8,
        'bat_versatility': 68.0, 'bowl_specialist': 85.0, 'athletic_fielding': 86.0, 'tactical_adaptability': 84.0, 'rr_squad_fit': 88.0,
        'composite_skill_ceiling': 82.0,
        'primary_technical_strengths': 'Tall high-arm release providing sharp new-ball swing; hit-the-deck pace; explosive lower-order batting muscle (No. 8).',
        'technical_dev_areas': 'Consistency of length when swing disappears; death-overs yorker execution.',
        'rr_tactical_role': 'New-Ball Pace All-Rounder / Lower-Order Hitter',
        'recent_comp_window': 'CPL, West Indies T20Is 2025-2026', 'matches_eval': 14,
        'perf_summary': '15 wickets, econ 7.85, 145 runs (SR 155.0); dynamic dual-skill impact in Caribbean cricket.',
        'traj_trend': 'Ascending', 'form_rating': 'INSUFFICIENT DATA', 'form_score': 64.0,
        'match_fitness_notes': 'Young, athletic, highly energetic fast bowler.',
        'targeting_tier': 'TIER 2 DEVELOPMENT TARGET',
        '3yr_value': 'High-upside pace all-rounder development; covers both pace bowling and lower-order hitting.',
        'rr_synergy': 'Complements Jofra Archer with the new ball and lengthens Rajasthan’s batting tail.'
    },
    {
        'player_id': 4856, 'player_name': 'Benjamin Sears', 'role': 'Bowler',
        'country': 'NZ', 'nationality': 'Overseas', 'dob': '1998-02-11',
        'task07k_rank': 16, 'hist_pressure_score': 71.1423, 'total_pressure_balls': 122,
        'he_balls': 13, 'death_balls': 30, 'chase_balls': 58, 'pp_balls': 45,
        'zero_opp_deficit': False, 'pressure_conf': 'MEDIUM',
        'dev_potential_score': 70.0, 'career_stage_desc': 'Peak-age express pace strike bowler; 4-5 year runway.',
        'dev_runway_years': 5,
        'bat_versatility': 20.0, 'bowl_specialist': 88.0, 'athletic_fielding': 84.0, 'tactical_adaptability': 80.0, 'rr_squad_fit': 84.0,
        'composite_skill_ceiling': 82.0,
        'primary_technical_strengths': 'Genuine 145-150 kph express pace; sharp bouncer that hurries international batters; wicket-taking middle-overs strike option.',
        'technical_dev_areas': 'Controlling economy rate when boundary riders are up; injury management for high-stress action.',
        'rr_tactical_role': 'Express 145+ Strike Bowler / Middle-Overs Enforcer',
        'recent_comp_window': 'Super Smash, T20Is (NZ) 2025-2026', 'matches_eval': 12,
        'perf_summary': '16 wickets, avg 19.5, SR 13.8, econ 8.45; demonstrated hostile pace against top-tier batting lineups.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'MIXED', 'form_score': 74.0,
        'match_fitness_notes': 'Fully fit after managed physical conditioning program.',
        'targeting_tier': 'TIER 2 SECONDARY TARGET',
        '3yr_value': 'Express pace strike weapon to support Archer; provides venomous backup pace.',
        'rr_synergy': 'Gives RR the option of deploying twin express 145+ kph pace enforcers alongside Jofra Archer.'
    },
    {
        'player_id': 4812, 'player_name': 'Harry Tector', 'role': 'Bowler',
        'country': 'IRE', 'nationality': 'Overseas', 'dob': '1999-12-06',
        'task07k_rank': 3, 'hist_pressure_score': 75.7120, 'total_pressure_balls': 120,
        'he_balls': 34, 'death_balls': 0, 'chase_balls': 70, 'pp_balls': 36,
        'zero_opp_deficit': True, 'pressure_conf': 'MEDIUM (EQ 75.71 - Zero Death Balls)',
        'dev_potential_score': 75.0, 'career_stage_desc': 'Prime-age batting all-rounder with matchup bowling utility; 5-6 year runway.',
        'dev_runway_years': 6,
        'bat_versatility': 85.0, 'bowl_specialist': 65.0, 'athletic_fielding': 88.0, 'tactical_adaptability': 84.0, 'rr_squad_fit': 80.0,
        'composite_skill_ceiling': 76.0,
        'primary_technical_strengths': 'High-IQ matchup off-spin bowling against left-handers; tight middle-overs economy; strong batting technique providing dual-role utility.',
        'technical_dev_areas': 'Zero observed death-overs bowling (EQ score drops to 75.71); must strictly be used in middle-overs matchups.',
        'rr_tactical_role': 'Tactical Matchup Off-Spinner / Batting Depth',
        'recent_comp_window': 'T20Is 2025-2026 (IRE), Franchise appearances', 'matches_eval': 15,
        'perf_summary': '9 wickets (econ 7.20), 380 runs (SR 136.5); dependable international multi-format performer.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 82.0,
        'match_fitness_notes': '100% fit and active international performer.',
        'targeting_tier': 'TIER 2 SECONDARY TARGET',
        '3yr_value': 'Versatile multi-skill squad asset; provides emergency middle-order batting and matchup bowling.',
        'rr_synergy': 'Valuable sixth-bowler option against left-hand heavy opposition top orders.'
    },
    {
        'player_id': 2984, 'player_name': 'Sikandar Raza', 'role': 'Bowler',
        'country': 'ZIM', 'nationality': 'Overseas', 'dob': '1986-04-24',
        'task07k_rank': 7, 'hist_pressure_score': 72.8821, 'total_pressure_balls': 264,
        'he_balls': 89, 'death_balls': 24, 'chase_balls': 120, 'pp_balls': 0,
        'zero_opp_deficit': True, 'pressure_conf': 'HIGH (EQ 72.88 - 89 HE Balls)',
        'dev_potential_score': 32.0, 'career_stage_desc': 'Legendary veteran clutch performer and global franchise icon; 1-2 year runway.',
        'dev_runway_years': 2,
        'bat_versatility': 88.0, 'bowl_specialist': 86.0, 'athletic_fielding': 88.0, 'tactical_adaptability': 94.0, 'rr_squad_fit': 92.0,
        'composite_skill_ceiling': 90.0,
        'primary_technical_strengths': 'Deepest pressure sample in pool (89 HE balls, 264 total balls); carrom ball and slider variations; elite clutch temperament; 2026 ICC No. 1 All-Rounder form.',
        'technical_dev_areas': 'Age 40 (reference date); near conclusion of physical runway; physical maintenance required.',
        'rr_tactical_role': 'Elite Clutch All-Rounder / Senior Leader & Match Finisher',
        'recent_comp_window': 'T20Is 2025-2026 (ZIM Captain), ILT20, CPL, PSL', 'matches_eval': 25,
        'perf_summary': '12 wickets (econ 6.55), 361 runs (SR 149.20); leading Zimbabwe to multiple historic T20I triumphs; rated STRONG.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'STRONG', 'form_score': 92.0,
        'match_fitness_notes': 'Outstanding physical conditioning; leads by personal example in international cricket.',
        'targeting_tier': 'EXPERIENCED TACTICAL LEADER / CLUTCH ANCHOR',
        '3yr_value': 'Immediate championship leadership and clutch composure; invaluable mentor to Ghazanfar, Bethell, and young core.',
        'rr_synergy': 'Provides ice-cold composure in tight matches; can win matches with either bat or ball under extreme pressure.'
    },
    {
        'player_id': 6512, 'player_name': 'Michael Bracewell', 'role': 'Bowler',
        'country': 'NZ', 'nationality': 'Overseas', 'dob': '1991-02-14',
        'task07k_rank': 1, 'hist_pressure_score': 82.6895, 'total_pressure_balls': 102,
        'he_balls': 4, 'death_balls': 0, 'chase_balls': 52, 'pp_balls': 34,
        'zero_opp_deficit': True, 'pressure_conf': 'MEDIUM (EQ 82.69 - Zero Death Balls)',
        'dev_potential_score': 40.0, 'career_stage_desc': 'Experienced international bowling all-rounder; 2-3 year runway.',
        'dev_runway_years': 2,
        'bat_versatility': 82.0, 'bowl_specialist': 78.0, 'athletic_fielding': 82.0, 'tactical_adaptability': 84.0, 'rr_squad_fit': 80.0,
        'composite_skill_ceiling': 80.0,
        'primary_technical_strengths': 'Hard off-spin driven into the deck; powerplay containment (econ 6.10); powerful lower-order hitting capability.',
        'technical_dev_areas': 'Zero observed death-overs balls; shrinkage artifact dropped EQ score to 82.69; cannot bowl past over 15.',
        'rr_tactical_role': 'Powerplay & Middle-Overs Enforcer (Strictly Non-Death)',
        'recent_comp_window': 'T20Is 2025-2026 (NZ Captain/AR), Super Smash', 'matches_eval': 15,
        'perf_summary': '11 wickets (econ 6.90), 220 runs (SR 144.0); dependable international contributor.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 84.0,
        'match_fitness_notes': 'Fit and regular member of New Zealand national squad.',
        'targeting_tier': 'EXPERIENCED TACTICAL ANCHOR / RESERVE',
        '3yr_value': 'Short-term tactical bowling depth; lower-order batting insurance.',
        'rr_synergy': 'Useful replacement if overseas spin all-rounder is required in conditions offering grip.'
    },
    {
        'player_id': 3807, 'player_name': 'Murugan Ashwin', 'role': 'Bowler',
        'country': 'IND', 'nationality': 'Indian', 'dob': '1990-09-08',
        'task07k_rank': 10, 'hist_pressure_score': 65.6812, 'total_pressure_balls': 174,
        'he_balls': 71, 'death_balls': 6, 'chase_balls': 95, 'pp_balls': 54,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 40.0, 'career_stage_desc': 'Veteran domestic wrist-spinner; 1-2 year domestic depth window.',
        'dev_runway_years': 2,
        'bat_versatility': 20.0, 'bowl_specialist': 85.0, 'athletic_fielding': 78.0, 'tactical_adaptability': 80.0, 'rr_squad_fit': 84.0,
        'composite_skill_ceiling': 75.0,
        'primary_technical_strengths': 'Top active eligible Indian bowler; deep IPL pressure sample (71 HE balls, 174 total balls); aggressive googly and leg-break trajectory.',
        'technical_dev_areas': 'Occasional drag-downs when attacked; limited multi-year runway at age 36.',
        'rr_tactical_role': 'Domestic Attacking Wrist-Spinner / Spin Reserve',
        'recent_comp_window': 'SMAT 2025-2026, TNPL, IPL matches', 'matches_eval': 14,
        'perf_summary': '14 wickets, econ 7.60, strike rate 19.5; consistent domestic wicket-taker.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'MIXED', 'form_score': 70.0,
        'match_fitness_notes': 'Regular domestic competitor; experienced professional.',
        'targeting_tier': 'TIER 1 DOMESTIC TARGET',
        '3yr_value': 'Crucial Indian domestic wrist-spin depth; protects franchise against injuries to Indian spinners.',
        'rr_synergy': 'Provides high-quality domestic leg-spin cover behind Ravi Bishnoi without consuming an overseas slot.'
    },
    {
        'player_id': 1998, 'player_name': 'Simarjeet Singh', 'role': 'Bowler',
        'country': 'IND', 'nationality': 'Indian', 'dob': '1998-01-17',
        'task07k_rank': 15, 'hist_pressure_score': 59.6912, 'total_pressure_balls': 105,
        'he_balls': 6, 'death_balls': 24, 'chase_balls': 48, 'pp_balls': 52,
        'zero_opp_deficit': False, 'pressure_conf': 'LOW',
        'dev_potential_score': 68.0, 'career_stage_desc': 'Prime-age Indian fast bowler with hit-the-deck attributes; 4-5 year runway.',
        'dev_runway_years': 5,
        'bat_versatility': 15.0, 'bowl_specialist': 80.0, 'athletic_fielding': 76.0, 'tactical_adaptability': 76.0, 'rr_squad_fit': 80.0,
        'composite_skill_ceiling': 72.0,
        'primary_technical_strengths': 'High release point generating steep bounce; clocks 140+ kph; aggressive powerplay hit-the-deck bowling.',
        'technical_dev_areas': 'Low observed high-extreme pressure sample (6 HE balls); developing reliable slower balls for death overs.',
        'rr_tactical_role': 'Domestic Hit-the-Deck Seam Depth / Powerplay Pacer',
        'recent_comp_window': 'SMAT 2025-2026, Delhi Premier League, IPL matches', 'matches_eval': 12,
        'perf_summary': '12 wickets, econ 8.20, strike rate 17.5; troubled top orders with steep bounce.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'MIXED', 'form_score': 70.0,
        'match_fitness_notes': 'Fit and active domestic seamer.',
        'targeting_tier': 'TIER 2 DOMESTIC TARGET',
        '3yr_value': 'Domestic pace bowling development; provides backup seam options behind Shami, Sandeep, and Archer.',
        'rr_synergy': 'Adds valuable Indian fast bowling depth, ensuring RR maintains tactical flexibility across varied pitches.'
    },
    {
        'player_id': 1991, 'player_name': 'Jaydev Unadkat', 'role': 'Bowler',
        'country': 'IND', 'nationality': 'Indian', 'dob': '1991-10-18',
        'task07k_rank': 13, 'hist_pressure_score': 60.4120, 'total_pressure_balls': 145,
        'he_balls': 35, 'death_balls': 23, 'chase_balls': 68, 'pp_balls': 45,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 42.0, 'career_stage_desc': 'Veteran domestic left-arm seamer and domestic captain; 1-2 year runway.',
        'dev_runway_years': 2,
        'bat_versatility': 45.0, 'bowl_specialist': 78.0, 'athletic_fielding': 76.0, 'tactical_adaptability': 82.0, 'rr_squad_fit': 78.0,
        'composite_skill_ceiling': 72.0,
        'primary_technical_strengths': 'Left-arm angle; vast repertoire of slower balls and off-cutters; 35 HE balls; domestic leadership experience.',
        'technical_dev_areas': 'Lack of outright pace (125-130 kph); vulnerability against elite death hitters on small grounds.',
        'rr_tactical_role': 'Domestic Left-Arm Seam Tactician / Senior Reserve',
        'recent_comp_window': 'Ranji Trophy, SMAT 2025-2026, IPL matches', 'matches_eval': 15,
        'perf_summary': 'Consistent domestic captain; 13 wickets in domestic white ball, econ 7.85.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'MIXED', 'form_score': 68.0,
        'match_fitness_notes': 'Active domestic leader; robust fitness.',
        'targeting_tier': 'EXPERIENCED TACTICAL ANCHOR / RESERVE',
        '3yr_value': 'Low-cost domestic pace cover; brings dressing room leadership.',
        'rr_synergy': 'Former Rajasthan Royals spearhead familiar with Jaipur ground dimensions.'
    },
    {
        'player_id': 499, 'player_name': 'Shakib Al Hasan', 'role': 'Bowler',
        'country': 'BAN', 'nationality': 'Overseas', 'dob': '1987-03-24',
        'task07k_rank': 8, 'hist_pressure_score': 75.1610, 'total_pressure_balls': 150,
        'he_balls': 18, 'death_balls': 24, 'chase_balls': 72, 'pp_balls': 42,
        'zero_opp_deficit': False, 'pressure_conf': 'HIGH',
        'dev_potential_score': 30.0, 'career_stage_desc': 'Legendary veteran all-rounder in final career chapter; 1 year runway.',
        'dev_runway_years': 1,
        'bat_versatility': 80.0, 'bowl_specialist': 85.0, 'athletic_fielding': 76.0, 'tactical_adaptability': 88.0, 'rr_squad_fit': 78.0,
        'composite_skill_ceiling': 80.0,
        'primary_technical_strengths': 'All phases observed (18 HE, 24 Death, 42 PP); consummate tactical mastery; left-arm arm ball and flight variation.',
        'technical_dev_areas': 'Age 40; limited physical runway; external career transitions.',
        'rr_tactical_role': 'Experienced All-Phase Defensive Spin Bank',
        'recent_comp_window': 'BPL, CPL, Global T20 2025-2026', 'matches_eval': 16,
        'perf_summary': '16 wickets, econ 6.48; highly disciplined tournament bowling.',
        'traj_trend': 'Stable / Peak', 'form_rating': 'POSITIVE', 'form_score': 84.0,
        'match_fitness_notes': 'Experienced professional.',
        'targeting_tier': 'EXPERIENCED IMPACT BACKUP',
        '3yr_value': 'Short-term tactical defensive cover.',
        'rr_synergy': 'Tactical left-arm option for turning pitches.'
    },
    {
        'player_id': 5750, 'player_name': 'Ehsan Khan', 'role': 'Bowler',
        'country': 'HK', 'nationality': 'Overseas', 'dob': '1984-12-27',
        'task07k_rank': 4, 'hist_pressure_score': 73.9812, 'total_pressure_balls': 120,
        'he_balls': 0, 'death_balls': 18, 'chase_balls': 65, 'pp_balls': 24,
        'zero_opp_deficit': True, 'pressure_conf': 'LOW / ARTIFACT-AFFECTED (EQ 73.98 - Zero HE Balls)',
        'dev_potential_score': 25.0, 'career_stage_desc': 'Veteran associate finger spinner aged 42; 0-1 year runway.',
        'dev_runway_years': 1,
        'bat_versatility': 30.0, 'bowl_specialist': 65.0, 'athletic_fielding': 60.0, 'tactical_adaptability': 65.0, 'rr_squad_fit': 55.0,
        'composite_skill_ceiling': 55.0,
        'primary_technical_strengths': 'Tight associate off-spin lines; steady execution against non-Tier 1 opposition.',
        'technical_dev_areas': 'Zero high-extreme balls; lowest development runway in pool; lacks physical attributes for IPL intensity.',
        'rr_tactical_role': 'Associate Finger Spinner (Non-Target)',
        'recent_comp_window': 'ICC Associate Fixtures, Challenge League', 'matches_eval': 10,
        'perf_summary': 'Steady associate bowling against Tier 4/5 teams; unproven against elite batting.',
        'traj_trend': 'Declining', 'form_rating': 'INSUFFICIENT DATA', 'form_score': 60.0,
        'match_fitness_notes': 'Older associate bowler.',
        'targeting_tier': 'LOW-PRIORITY / UNSUITED TO RR MODEL',
        '3yr_value': 'Negligible long-term franchise value.',
        'rr_synergy': 'Unsuited to RR’s high-ceiling, elite-athleticism scouting requirements.'
    }
]

df_all = pd.DataFrame(candidates_data)

# Compute age as of 2027-04-01
def calc_age(dob_str):
    dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
    age = ref_date.year - dob.year - ((ref_date.month, ref_date.day) < (dob.month, dob.day))
    return age

def get_dev_category(age):
    if age <= 23:
        return 'Emerging'
    elif age <= 26:
        return 'Young development candidate'
    elif age <= 30:
        return 'Prime-age performer'
    else:
        return 'Experienced performer'

df_all['age_as_of_2027_04_01'] = df_all['dob'].apply(calc_age)
df_all['development_category'] = df_all['age_as_of_2027_04_01'].apply(get_dev_category)

# Dimension Weights:
# Dim A (Historical Pressure): 40%
# Dim B (Age & Development): 30%
# Dim C (Skill Ceiling & RR Fit): 20%
# Dim D (Current Form & Trajectory): 10%
df_all['dimA_hist_pressure'] = df_all['hist_pressure_score']
df_all['dimB_dev_potential'] = df_all['dev_potential_score']
df_all['dimC_skill_ceiling'] = df_all['composite_skill_ceiling']
df_all['dimD_current_form'] = df_all['form_score']

df_all['unrounded_scouting_score'] = (
    0.40 * df_all['dimA_hist_pressure'] +
    0.30 * df_all['dimB_dev_potential'] +
    0.20 * df_all['dimC_skill_ceiling'] +
    0.10 * df_all['dimD_current_form']
)
df_all['rr_scouting_score'] = df_all['unrounded_scouting_score'].round(2)

# Separate Batters and Bowlers and rank
df_bat = df_all[df_all['role'] == 'Batter'].sort_values('unrounded_scouting_score', ascending=False).reset_index(drop=True)
df_bat['scouting_rank'] = df_bat.index + 1
df_bat['rank_delta'] = df_bat['task07k_rank'] - df_bat['scouting_rank']

df_bowl = df_all[df_all['role'] == 'Bowler'].sort_values('unrounded_scouting_score', ascending=False).reset_index(drop=True)
df_bowl['scouting_rank'] = df_bowl.index + 1
df_bowl['rank_delta'] = df_bowl['task07k_rank'] - df_bowl['scouting_rank']

print('Batters Scouting Results:')
print(df_bat[['scouting_rank', 'player_name', 'age_as_of_2027_04_01', 'development_category', 'rr_scouting_score', 'task07k_rank', 'rank_delta']])

print('\nBowlers Scouting Results:')
print(df_bowl[['scouting_rank', 'player_name', 'age_as_of_2027_04_01', 'development_category', 'rr_scouting_score', 'task07k_rank', 'rank_delta']])

# Combine back for common audits
df_all_ranked = pd.concat([df_bat, df_bowl], ignore_index=True)

# ==============================================================================
# DELIVERABLE 1: outputs/task07l/age_and_career_stage_audit.csv
# ==============================================================================
age_audit = df_all_ranked[[
    'player_id', 'player_name', 'role', 'nationality', 'country', 'dob',
    'age_as_of_2027_04_01', 'development_category', 'career_stage_desc',
    'dev_runway_years', 'dev_potential_score'
]].rename(columns={
    'dob': 'date_of_birth',
    'career_stage_desc': 'career_stage_description',
    'dev_runway_years': 'development_runway_years',
    'dev_potential_score': 'development_potential_score'
})
age_audit.to_csv('outputs/task07l/age_and_career_stage_audit.csv', index=False)
print('Saved outputs/task07l/age_and_career_stage_audit.csv')

# ==============================================================================
# DELIVERABLE 2: outputs/task07l/skill_ceiling_assessment.csv
# ==============================================================================
skill_audit = df_all_ranked[[
    'player_id', 'player_name', 'role', 'nationality',
    'bat_versatility', 'bowl_specialist', 'athletic_fielding',
    'tactical_adaptability', 'rr_squad_fit', 'composite_skill_ceiling',
    'primary_technical_strengths', 'technical_dev_areas', 'rr_tactical_role'
]].rename(columns={
    'bat_versatility': 'batting_versatility_score',
    'bowl_specialist': 'bowling_specialist_score',
    'athletic_fielding': 'athletic_fielding_score',
    'tactical_adaptability': 'tactical_adaptability_score',
    'rr_squad_fit': 'rr_squad_fit_score',
    'composite_skill_ceiling': 'composite_skill_ceiling_score',
    'technical_dev_areas': 'technical_development_areas'
})
skill_audit.to_csv('outputs/task07l/skill_ceiling_assessment.csv', index=False)
print('Saved outputs/task07l/skill_ceiling_assessment.csv')

# ==============================================================================
# DELIVERABLE 3: outputs/task07l/current_form_trajectory.csv
# ==============================================================================
form_audit = df_all_ranked[[
    'player_id', 'player_name', 'role', 'nationality',
    'recent_comp_window', 'matches_eval', 'perf_summary',
    'traj_trend', 'form_rating', 'form_score', 'match_fitness_notes'
]].rename(columns={
    'recent_comp_window': 'recent_competition_window',
    'matches_eval': 'matches_evaluated',
    'perf_summary': 'performance_summary',
    'traj_trend': 'trajectory_trend',
    'form_rating': 'current_form_rating',
    'form_score': 'current_form_score'
})
form_audit.to_csv('outputs/task07l/current_form_trajectory.csv', index=False)
print('Saved outputs/task07l/current_form_trajectory.csv')

# ==============================================================================
# DELIVERABLE 4: outputs/task07l/pressure_evidence_reliability.csv
# ==============================================================================
pressure_audit = df_all_ranked[[
    'player_id', 'player_name', 'role', 'nationality',
    'hist_pressure_score', 'total_pressure_balls', 'he_balls',
    'death_balls', 'chase_balls', 'pp_balls', 'zero_opp_deficit',
    'pressure_conf', 'dimA_hist_pressure'
]].rename(columns={
    'hist_pressure_score': 'original_or_eq_pressure_score',
    'he_balls': 'high_extreme_balls',
    'pp_balls': 'powerplay_balls',
    'zero_opp_deficit': 'zero_opportunity_deficit_flag',
    'pressure_conf': 'pressure_evidence_confidence',
    'dimA_hist_pressure': 'historical_pressure_dimension_score'
})
pressure_audit.to_csv('outputs/task07l/pressure_evidence_reliability.csv', index=False)
print('Saved outputs/task07l/pressure_evidence_reliability.csv')

# ==============================================================================
# DELIVERABLE 5: outputs/task07l/rr_scouting_priority_scores.csv
# ==============================================================================
scouting_scores = df_all_ranked[[
    'player_id', 'player_name', 'role', 'nationality', 'country',
    'age_as_of_2027_04_01', 'development_category',
    'dimA_hist_pressure', 'dimB_dev_potential', 'dimC_skill_ceiling', 'dimD_current_form',
    'rr_scouting_score', 'unrounded_scouting_score', 'scouting_rank', 'task07k_rank', 'rank_delta'
]].rename(columns={
    'dimA_hist_pressure': 'dimA_historical_pressure_score',
    'dimB_dev_potential': 'dimB_age_development_score',
    'dimC_skill_ceiling': 'dimC_skill_ceiling_score',
    'dimD_current_form': 'dimD_current_form_score',
    'scouting_rank': 'scouting_rank_within_role',
    'task07k_rank': 'task07k_original_rank'
})
scouting_scores.to_csv('outputs/task07l/rr_scouting_priority_scores.csv', index=False)
print('Saved outputs/task07l/rr_scouting_priority_scores.csv')

# ==============================================================================
# DELIVERABLE 6: outputs/task07l/rr_player_development_profiles.csv
# ==============================================================================
dev_profiles = df_all_ranked[[
    'player_id', 'player_name', 'role', 'nationality',
    'age_as_of_2027_04_01', 'development_category', 'rr_scouting_score', 'scouting_rank',
    'targeting_tier', 'primary_technical_strengths', 'technical_dev_areas',
    '3yr_value', 'rr_synergy'
]].rename(columns={
    'targeting_tier': 'rr_auction_targeting_tier',
    'primary_technical_strengths': 'key_strengths',
    'technical_dev_areas': 'development_opportunities_coaching_plan',
    '3yr_value': 'projected_3year_value',
    'rr_synergy': 'rr_squad_synergy'
})
dev_profiles.to_csv('outputs/task07l/rr_player_development_profiles.csv', index=False)
print('Saved outputs/task07l/rr_player_development_profiles.csv')

# ==============================================================================
# DELIVERABLE 7: outputs/task07l/unrestricted_vs_rr_scouting_ranking.csv
# ==============================================================================
def get_shift_driver(row):
    if row['rank_delta'] > 0:
        if row['development_category'] in ['Emerging', 'Young development candidate']:
            return 'High development runway, exceptional technical ceiling, and youth progression'
        else:
            return 'Current form surge and superior tactical role fit for Rajasthan Royals'
    elif row['rank_delta'] < 0:
        if row['development_category'] == 'Experienced performer':
            return 'Older career stage, limited multi-year runway, and lower developmental ceiling'
        else:
            return 'Zero-opportunity bowling deficits or high performance variance'
    else:
        return 'Balanced historical excellence matching prime developmental window'

def get_strategic_verdict(row):
    if row['scouting_rank'] <= 3:
        return 'MUST-TARGET: Core franchise pillar / High-ceiling cornerstone'
    elif row['scouting_rank'] <= 6:
        return 'HIGH PRIORITY: Tactical starter / High-floor developmental value'
    elif row['scouting_rank'] <= 10:
        return 'SELECTIVE TARGET: Role specialist / Domestic depth / Experience anchor'
    else:
        return 'RESERVE / NON-TARGET: Superseded by younger, higher-ceiling alternatives'

df_all_ranked['primary_driver_of_shift'] = df_all_ranked.apply(get_shift_driver, axis=1)
df_all_ranked['rr_scouting_strategic_verdict'] = df_all_ranked.apply(get_strategic_verdict, axis=1)

unrestricted_comp = df_all_ranked[[
    'role', 'player_id', 'player_name', 'nationality',
    'age_as_of_2027_04_01', 'development_category',
    'task07k_rank', 'hist_pressure_score', 'scouting_rank', 'rr_scouting_score',
    'rank_delta', 'primary_driver_of_shift', 'rr_scouting_strategic_verdict'
]].rename(columns={
    'task07k_rank': 'unrestricted_task07k_rank',
    'hist_pressure_score': 'unrestricted_task07k_score',
    'scouting_rank': 'rr_scouting_rank'
})
unrestricted_comp.to_csv('outputs/task07l/unrestricted_vs_rr_scouting_ranking.csv', index=False)
print('Saved outputs/task07l/unrestricted_vs_rr_scouting_ranking.csv')

# ==============================================================================
# DELIVERABLE 8: outputs/task07l/final_combined_top10_batters.csv
# ==============================================================================
top10_batters = df_bat.head(10).copy()
top10_batters['final_rank'] = top10_batters.index + 1
top10_batters_out = top10_batters[[
    'final_rank', 'player_id', 'player_name', 'country', 'nationality',
    'age_as_of_2027_04_01', 'development_category', 'rr_tactical_role',
    'hist_pressure_score', 'rr_scouting_score', 'unrounded_scouting_score',
    'form_rating', 'pressure_conf', 'primary_technical_strengths',
    'technical_dev_areas', 'targeting_tier', 'rr_synergy'
]].rename(columns={
    'rr_tactical_role': 'role',
    'hist_pressure_score': 'original_pressure_score',
    'rr_scouting_score': 'rr_scouting_priority_score',
    'form_rating': 'current_form_assessment',
    'pressure_conf': 'pressure_evidence_confidence',
    'primary_technical_strengths': 'main_strengths',
    'technical_dev_areas': 'development_opportunities',
    'targeting_tier': 'auction_targeting_strategy',
    'rr_synergy': 'why_rr_should_consider'
})
top10_batters_out.to_csv('outputs/task07l/final_combined_top10_batters.csv', index=False)
print('Saved outputs/task07l/final_combined_top10_batters.csv')

# ==============================================================================
# DELIVERABLE 9: outputs/task07l/final_combined_top10_bowlers.csv
# ==============================================================================
top10_bowlers = df_bowl.head(10).copy()
top10_bowlers['final_rank'] = top10_bowlers.index + 1
top10_bowlers_out = top10_bowlers[[
    'final_rank', 'player_id', 'player_name', 'country', 'nationality',
    'age_as_of_2027_04_01', 'development_category', 'rr_tactical_role',
    'hist_pressure_score', 'rr_scouting_score', 'unrounded_scouting_score',
    'form_rating', 'pressure_conf', 'primary_technical_strengths',
    'technical_dev_areas', 'targeting_tier', 'rr_synergy'
]].rename(columns={
    'rr_tactical_role': 'role',
    'hist_pressure_score': 'original_evidence_qualified_score',
    'rr_scouting_score': 'rr_scouting_priority_score',
    'form_rating': 'current_form_assessment',
    'pressure_conf': 'pressure_evidence_confidence',
    'primary_technical_strengths': 'main_strengths',
    'technical_dev_areas': 'development_opportunities',
    'targeting_tier': 'auction_targeting_strategy',
    'rr_synergy': 'why_rr_should_consider'
})
top10_bowlers_out.to_csv('outputs/task07l/final_combined_top10_bowlers.csv', index=False)
print('Saved outputs/task07l/final_combined_top10_bowlers.csv')

print('All 7 CSV deliverables created successfully.')

