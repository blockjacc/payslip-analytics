# Payslip Analytics App

A comprehensive analytics application for payslip and shifts data visualization with unified charting standards.

## Project Structure

```
payslip-analytics/
├── backend/          # Python Flask backend
│   ├── app.py        # Main Flask application
│   ├── payslip_fields.py  # Field definitions
│   └── requirements.txt   # Python dependencies
├── frontend/         # Vue.js frontend
│   ├── src/
│   │   ├── components/
│   │   ├── views/    # Analytics views
│   │   └── utils/    # Chart utilities
│   └── package.json  # Node.js dependencies
└── README.md         # This file
```

## Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
yarn install
yarn serve
```

## Architecture Principles

### In-Memory Compute Principle
- **Single Fetch:** Backend retrieves and decrypts all relevant records in one query
- **No Backend Specialization:** Backend doesn't implement separate endpoints for each visualization
- **In-Memory Processing:** All computation (aggregation, grouping, filtering) performed in memory
- **Rationale:** Minimizes database I/O, maximizes flexibility, maintains simple backend

### Unified Chart System
All charts in the application use a unified system for consistent behavior and visual appearance.

## Charting Standards

### 1. Unified Chart Architecture

#### Core Utilities (`src/utils/chartAxis.js`)
- **`getUnifiedStackedBarChart()`**: For simple single-value charts (shifts analytics)
- **`getUnifiedPayslipChart()`**: For multi-period, multi-field charts (payslip analytics)
- **`mapValueToLogPosition()`**: Transforms data values to logarithmic positions on linear scale

#### Key Technical Innovation: Logarithmic Position Mapping
The system solves the fundamental Chart.js alignment issue between linear scale positions and logarithmic tick values:

```javascript
function mapValueToLogPosition(value, min, max) {
  const logMin = Math.log(min);
  const logMax = Math.log(max);
  const logValue = Math.log(value);
  const logPosition = ((logValue - logMin) / (logMax - logMin)) * 9 + 1;
  return (logPosition / 10) * max;
}
```

This ensures that data segments align perfectly with their corresponding tick marks.

### 2. Chart Configuration Standards

#### Y-Axis Specifications
- **Type:** Linear scale with logarithmically-spaced custom tick values
- **Start:** Always at 0
- **First Tick Above 0:** Smallest non-zero value among all selected fields
- **Top Tick:** Total sum of all values (aggregate) or max period sum (separate)
- **Ticks:** Exactly 11 ticks total: [0, min, then 9 logarithmic steps to total sum]
- **Implementation:** Custom tick generation with callback mapping

#### Tick Generation Logic
```javascript
export function getSimpleYAxis(values) {
  const nonZero = values.filter(v => v > 0);
  const min = Math.min(...nonZero);
  const totalSum = nonZero.reduce((sum, v) => sum + v, 0);
  
  // 11 ticks: 0, min, then 9 more logarithmic steps to totalSum
  const ticks = [0, min];
  for (let i = 1; i <= 9; i++) {
    const t = min * Math.pow(totalSum / min, i / 9);
    ticks.push(Math.round(t));
  }
  ticks[10] = totalSum; // Ensure last tick is exactly the total sum
  
  return { min: 0, max: totalSum, ticks };
}
```

#### Visual Standards
- **Font:** 'Open Sans' for all chart text
- **Legend:** Always displayed on the right
- **Stacking Order:** Always lowest to highest values (bottom to top)
- **Colors:** Consistent across all charts using predefined color schemes

### 3. Chart Types and Usage

#### Payslip Analytics Charts
- **File:** `Analytics.vue`
- **Function:** `getUnifiedPayslipChart()`
- **Features:**
  - Multi-period support (aggregate/separate views)
  - Multi-field stacking
  - Period-based data organization
  - Click handlers for drilldown navigation

#### Shifts Analytics Charts
- **Files:** `ShiftsScheduleTypeAnalytics.vue`, `ShiftsAllocationAnalytics.vue`
- **Function:** `getUnifiedStackedBarChart()`
- **Features:**
  - Single-period data
  - Category-based stacking
  - Simplified data structure

### 4. Data Handling Standards

#### Payslip Data Structure
```javascript
// Aggregate View
{
  periods: [{ period: 'Total', data: {...} }],
  selectedFields: ['field1', 'field2', 'field3']
}

// Separate View
{
  periods: [
    { period: 'Period 1', data: {...} },
    { period: 'Period 2', data: {...} }
  ],
  selectedFields: ['field1', 'field2', 'field3']
}
```

#### Shifts Data Structure
```javascript
{
  data: { 'Category1': count1, 'Category2': count2 },
  colors: { 'Category1': '#color1', 'Category2': '#color2' }
}
```

### 5. Implementation Examples

#### Payslip Chart Implementation
```javascript
// In Analytics.vue
const chartConfig = getUnifiedPayslipChart({
  periods: this.periods,
  selectedFields: this.selectedFields,
  colors: this.colors,
  onBarClick: this.handleBarClick
});

this.chart = new Chart(ctx, chartConfig);
```

#### Shifts Chart Implementation
```javascript
// In ShiftsScheduleTypeAnalytics.vue
const chartConfig = getUnifiedStackedBarChart({
  label: 'Schedule Types',
  data: this.scheduleTypeCounts,
  colors: this.colors
});

this.chart = new Chart(ctx, chartConfig);
```

### 6. Technical Notes

#### Linear vs Logarithmic Scale
- **Problem:** Chart.js logarithmic scale doesn't reliably respect custom tick arrays
- **Solution:** Use linear scale with logarithmically-spaced tick values
- **Implementation:** Custom callback function maps Chart.js positions to exact values

#### Alignment Solution
- **Issue:** Data segments not aligning with tick marks
- **Root Cause:** Chart.js using linear positions vs logarithmic tick values
- **Fix:** `mapValueToLogPosition()` transforms data values to correct linear positions

#### Tooltip Handling
- **Challenge:** Display original values instead of transformed positions
- **Solution:** Custom tooltip callbacks that reference original data values
- **Implementation:** Separate data tracking for tooltips vs chart positioning

### 7. Drilldown Data Handling

#### Principle
- Backend returns period-separated employee records (one record per employee per period)
- Frontend performs all computation and aggregation in memory
- No additional backend endpoints for drilldown views

#### Drilldown Views
- **Separate Drilldown:** One row per employee per period
- **Aggregate Drilldown:** Employee records grouped by `emp_id` with summed totals
- **CSV Export:** Reflects current in-memory view, not new backend query

### 8. Implementation Checklist

#### For New Charts
- [ ] Use unified chart utilities (`getUnifiedStackedBarChart` or `getUnifiedPayslipChart`)
- [ ] Implement 11-tick logarithmic Y-axis with custom tick generation
- [ ] Ensure proper stacking order (lowest to highest values)
- [ ] Include legend on the right
- [ ] Use 'Open Sans' font throughout
- [ ] Implement proper tooltip handling with original values
- [ ] Test alignment between data segments and tick marks

#### For New Analytics Views
- [ ] Follow in-memory compute principle
- [ ] Implement consistent button styling and card layout
- [ ] Use unified routing patterns
- [ ] Include drilldown navigation if applicable
- [ ] Implement CSV export using in-memory data

### 9. Real-World Examples

#### Payslip Analytics
- **Values:** [1157.92, 2077, 39.01] (Overtime, Regular, Absent)
- **Generated Ticks:** [0, 39, 64, 104, 171, 279, 457, 748, 1223, 2001, 3274]
- **Stacking Order:** Absent (39.01), Regular (2077), Overtime (1157.92)
- **Result:** Perfect alignment with logarithmic tick spacing

#### Shifts Analytics
- **Values:** [148, 7, 1, 1, 1] (schedule type counts)
- **Generated Ticks:** [0, 1, 2, 3, 5, 9, 17, 29, 51, 90, 158]
- **Stacking Order:** Open Shift (1), Rest Day (1), Workshift (1), Flexible Hours (7), Uniform Working Days (148)
- **Result:** Consistent behavior with payslip charts

## Development Guidelines

### Code Standards
- Follow Vue.js best practices and composition API patterns
- Use TypeScript-style JSDoc comments for documentation
- Implement proper error handling and loading states
- Maintain consistent naming conventions across components

### Testing
- Test chart alignment by verifying first segment reaches first tick
- Validate stacking order matches value sorting (lowest to highest)
- Ensure tooltip values match original data, not transformed positions
- Verify consistent behavior across all chart types

### Performance
- Leverage in-memory compute for all analytics operations
- Minimize backend requests through single-fetch strategy
- Use efficient data structures for large datasets
- Implement proper component lifecycle management

---

**This documentation serves as the definitive guide for all charting and analytics implementation in the Payslip Analytics App. Any new features must follow these standards for consistency, maintainability, and user experience.** 