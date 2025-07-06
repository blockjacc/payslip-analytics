# frontend

## Project setup
```
yarn install
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

# Charting Standards for Payslip Analytics App

## Stacked Bar Chart Logic (Payslip Analytics)

### 1. Chart Structure
- **Type:** Vertical stacked bar chart (Chart.js Bar with `stacked: true`)
- **X-Axis:**
  - For aggregate/single-period: one label, e.g., 'Total'
  - For separate/multi-period: one label per period (e.g., 'March 3, 2025 - March 17, 2025')
- **Y-Axis:**
  - **Type:** Logarithmic
  - **Start:** Always at 0
  - **First Tick Above 0:** Smallest non-zero value among all selected fields
  - **Top Tick:** Total sum (for aggregate) or max period sum (for separate)
  - **Ticks:** Exactly 11 ticks (including 0 and the top), spaced logarithmically
  - **Tick Values:** [0, min, ..., max] (10 log steps between min and max)
  - **No extra ticks**—only these 11 are shown (enforced with `afterBuildTicks`)
- **Bar Segments:**
  - Each selected field is a segment in the stack
  - All selected fields are always included, even if value is zero
  - Smallest value is at the bottom, largest at the top
- **Legend:** Always displayed on the right
- **Font:** 'Open Sans' for all chart text

### 2. Data Handling
- **Aggregate View:**
  - Treat as a single-period 'separate' case for charting logic
  - All selected fields are stacked in one bar
- **Separate View:**
  - Each period is a bar, fields are stacked segments
- **Field Names:**
  - Must match between backend and frontend
  - All selected fields must be present in the chart, even if value is zero

### 3. UI/UX Consistency
- **Button Styling:** Consistent with payslip pattern
- **Card Layout:** Consistent with payslip pattern
- **Routing:** Unified pattern for all analytics

### 4. Implementation Checklist
- [ ] Chart is a single vertical stacked bar for aggregate, multiple for separate
- [ ] Y-axis starts at 0, first tick is smallest value, top is total, 11 ticks only
- [ ] All selected fields are always shown as segments
- [ ] Legend is on the right
- [ ] Font is 'Open Sans' everywhere
- [ ] Chart logic is unified for aggregate and separate

### 5. Example (Aggregate)
- **Y-Axis Ticks:** 0, 34,829, 61,904, 110,025, 195,554, 347,569, 617,754, 1,097,968, 1,951,480, 3,468,474, 6,164,712
- **Bar Segments:** Night Shift, Overtime, Regular (stacked)

---

**This documentation is the predicate for all charting in this app. Any new chart or analytics view must follow these standards for consistency, clarity, and maintainability.**

## Drilldown Data Handling (Payslip Analytics)

### Principle
- The backend always returns period-separated employee records (one record per employee per period).
- The frontend is responsible for all further computation and aggregation, in memory.

### Drilldown Views
- **Separate Drilldown:**
  - The frontend displays the data as structured in memory: one row per employee per period.
  - The user can select a period to view the breakdown for that period only.
- **Aggregate Drilldown:**
  - The frontend groups all employee records by `emp_id` and sums all numeric fields across all periods.
  - Only one row per employee is displayed, with totals for each field for the full period.
  - The CSV export for aggregate drilldown also uses these in-memory totals.

### Rationale
- This approach keeps the backend simple and stateless.
- All analytics, aggregation, and drilldown logic is centralized in the frontend, making it easy to adapt and extend.
- This is fully consistent with the in-memory compute principle described in `inmemorycompute.txt`.

---

## In-Memory Compute Principle (All Analytics & Drilldowns)

### Principle
- **Single Fetch:** The backend retrieves and decrypts all relevant records for a user's analytics/drilldown request in one query.
- **No Backend Specialization:** The backend does not implement separate endpoints or logic for each visualization, aggregation, or drilldown type.
- **In-Memory Processing:** All further computation—aggregation, grouping, filtering, drilldown, and transformation—is performed in memory (in the frontend or backend session), not in the database or via additional backend endpoints.

### Application
- **Analytics Views:** The frontend receives all necessary raw records and computes totals, groupings, and visualizations as needed.
- **Drilldowns:** The frontend (or in-memory backend logic) can group, sum, or filter records for any drilldown or export, without requiring new backend code.
- **CSV/Export:** Any export reflects the current in-memory view, not a new backend query.

### Rationale
- **Performance:** Minimizes database I/O and backend load by fetching once per request.
- **Flexibility:** Enables new visualizations, aggregations, and drilldowns without backend changes.
- **Maintainability:** Keeps backend simple, stateless, and focused on secure data retrieval and decryption.

### Example
- For payslip analytics, the backend returns all payslip records for the selected period(s). The frontend computes both aggregate and per-period views, as well as employee-level drilldowns, entirely in memory.

---

**This principle applies to all analytics and drilldown features in this app. Any new visualization or export should be implemented using in-memory compute, not new backend endpoints.**
