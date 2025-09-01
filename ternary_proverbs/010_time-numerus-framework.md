# The Numerus Calendar — 13×28 Compass + Day of the Void (0)

**Filename:** NUMERUS_CALENDAR.md  
**Timestamp:** 2025-09-01

---

## Context
This calendar replaces vague, lumpy time with a clean, intentional structure aligned to the Numerus ladder. It encodes **13 months × 28 days = 364** counted days, plus **one intercalary reset day** in the middle of the solar year:
**the Day of the Void (0)**.

Purpose: convert time into practice. The reset day is a ritual pause. The 13th month (tredecad) is renewal, not curse.

---

## Lesson (Spec in one breath)
- **Year length (counted):** 13 × 28 = **364** days  
- **Reset day:** **1 intercalary day** (“Day of the Void”, state **0**) → total 365
- **Month length:** fixed **28** (4×7)  
- **Month names:** Monad, Dyad, Triad, Tetrad, Pentad, Hexad, Heptad, Octad, Ennead, Decad, Undecad, Duodecad, Tredecad
- **Placement:** **Day of the Void = Gregorian September 14** each civil year (out of month, out of week)
- **Numerus reading:** each 28 → 2+8 = 10 → **1** (monadic renewal cycle), tredecad (13) = **transformative restart**

---

## Expansion (Operational Rules)

### 1) Year Anchor
- **Numerus Year begins:** **March 15** (Gregorian)  
- Rationale: placing the **Day of the Void (Sep 14)** at mid-year yields two clean 182-day arcs around an intercalary 0-day.

### 2) Months (fixed 28)
- 13 months, each 28 days (no exceptions). Weeks are perfectly 4 per month.

### 3) Intercalation
- **Day of the Void (0):** **September 14 (Gregorian)** every year.
  - Not part of any month or week.
  - Ritual function: surrender, reset, reconcile logs, recommit to the Source.
  - Practical function: preserves 365-day civil alignment without warping months.

### 4) Leap Years (Gregorian)
- Optional policy for Feb 29 (when present):
  - **Echo Day (0e):** treat Feb 29 as a second out-of-time day (also not counted in months/weeks).
  - If you’d rather avoid dual intercalaries: you may map Feb 29 into **Duodecad** silently and still keep the **Sep 14 Void Day** as the only ritual 0. Choose one policy, document it, stay consistent.

---

## Application (How to live it)
- **Daily:** move in 4×7 rhythm; every month is symmetrical.  
- **Monthly:** each 28-day block is a monadic decision cycle; close with a written merge (mini-retrospective).  
- **Mid-Year:** **Sep 14** = **0 Nihil**. No work. No goals. Breath + return + offering.  
- **Yearly:** **Tredecad** is your renewal month — archive, prune, refactor, then re-enter at Monad.

---

## Notes
- This calendar is **practice-first**: it privileges coherence over legacy quirks.
- The Void Day is not a holiday; it’s a **reset sacrament**.  
- If you adopt **Echo Day** in leap years, mark it explicitly as 0e to keep logs unambiguous.

---

## 2025 Mapping (Concrete, ready to use)
**Numerus Year 2025 start:** **2025-03-15 (Gregorian)**

| # | Month (28d) | Gregorian span |
|---|-------------|----------------|
| 01 | **Monad** | 2025-03-15 → 2025-04-11 |
| 02 | **Dyad** | 2025-04-12 → 2025-05-09 |
| 03 | **Triad** | 2025-05-10 → 2025-06-06 |
| 04 | **Tetrad** | 2025-06-07 → 2025-07-04 |
| 05 | **Pentad** | 2025-07-05 → 2025-08-01 |
| 06 | **Hexad** | 2025-08-02 → 2025-08-29 |
| 07 | **Heptad** | 2025-08-30 → 2025-09-26 |
| — | **Day of the Void (0)** | **2025-09-14** (intercalary; not counted) |
| 08 | **Octad** | 2025-09-27 → 2025-10-24 |
| 09 | **Ennead** | 2025-10-25 → 2025-11-21 |
| 10 | **Decad** | 2025-11-22 → 2025-12-19 |
| 11 | **Undecad** | 2025-12-20 → 2026-01-16 |
| 12 | **Duodecad** | 2026-01-17 → 2026-02-13 |
| 13 | **Tredecad** | 2026-02-14 → 2026-03-13 |
| → | **Next Year begins** | 2026-03-15 |

> Note: **Sep 14** sits inside Heptad by civil date but is **not counted** toward Heptad’s 28. Treat it as a pause between Heptad-Day 16 and Heptad-Day 17.

---

## Conversion (Human-readable rules)
- To find your Numerus month/day from a Gregorian date:
  1. If **Sep 14** → “**Day of the Void (0)**”.
  2. Else compute days since **Mar 15**; fold into 13×28 grid (ignore the Void day in the count).
  3. Month index = floor(day_index / 28) + 1; Day = (day_index % 28) + 1.
- To go the other way, add (month−1)×28 + (day−1) to **Mar 15** and adjust if you cross **Sep 14** (skip it; it’s out of count).

*(You can later ship this as a small protocol class if you want automated conversion.)*

---

## Reference Verse
**“To everything there is a season, and a time to every purpose under heaven.”** — Ecclesiastes 3:1
