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

## Operational Information

### Python Version
- **Python 3.13** is required for this project
- Virtual environment is already configured - **do not recreate it**

### Environment and Configuration
- **Encryption**: AES decryption is used for sensitive data
  - Encryption key is stored in `backend/.env`
  - Database fields marked with 'e' are encrypted, 'n' are non-encrypted
  - Follow existing encryption patterns - do not deviate from current implementation
- **Database Credentials**: Located in `backend/.env` (not main repo)
- **Field Mappings**: `payslip_fields.py` contains Python dictionary with nested dataclasses reflecting `payslip_fields_mapping.txt`

### Port Management
- **Backend**: Port 5000
- **Frontend**: Port 3000
- **Important**: Always kill existing processes before starting:
  ```bash
  kill -9 $(lsof -t -i:3000,5000) 2>/dev/null || true && pkill -f "node.*" && pkill -f "python.*app.py"
  ```

### Development Standards
- Backend includes linting and type-checking with undefined variable scanning
- Virtual environment **must be activated** before running backend operations

## Setup Instructions

### Backend Setup
```bash
cd backend
# Virtual environment is already configured - do not recreate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py  # Note: Use python3, not python
```

**Important Notes:**
- **Always activate virtual environment** before running backend operations: `source venv/bin/activate`
- **Use python3** command (not `python`) to avoid "command not found" errors
- Backend runs on **port 5002** by default
- Virtual environment is pre-configured - do not recreate it

### Frontend Setup
```bash
cd frontend
yarn install  # Use yarn, not npm
yarn dev       # Start development server
```

**Important Notes:**
- **Use yarn package manager** (not npm) for all frontend operations
- Available commands:
  - `yarn dev` - Start development server
  - `yarn build` - Build for production
  - `yarn serve` - Serve built files
- Frontend runs on **port 3000** by default

## Architecture Principles

### In-Memory Compute Principle
- **Single Fetch:** Backend retrieves and decrypts all relevant records in one query
- **No Backend Specialization:** Backend doesn't implement separate endpoints for each visualization
- **In-Memory Processing:** All computation (aggregation, grouping, filtering) performed in memory
- **Rationale:** Minimizes database I/O, maximizes flexibility, maintains simple backend

### Unified Chart System
All charts in the application use a unified system for consistent behavior and visual appearance.

**New in 2024:**
- Stacking order for stacked bar charts is now determined per period (not globally). For each period, fields/items are stacked in ascending order of value for that period. This ensures correct visual representation even when the order of values changes between periods.
- This per-period stacking is supported for all analytics modules (payslip, shifts, deep dive, etc.) via a shared utility.
- Legacy global stacking order is still available for backward compatibility.

## UX/UI Design System

### Universal Background System
The application implements a unified background system to ensure visual consistency across all pages and components.

#### Architecture
- **BaseLayout Component**: Single source of truth for page background styling
- **Location**: `frontend/src/components/layouts/BaseLayout.vue`
- **Usage**: Wraps all page content through `App.vue`

#### Background Gradient
- **Colors**: Green to purple gradient
- **CSS**: `background: linear-gradient(to right, rgba(0, 128, 0, 0.1) 0%, rgba(128, 0, 128, 0.1) 100%);`
- **Opacity**: Very subtle (0.1) for optimal text readability

#### Implementation Pattern
```vue
<!-- App.vue -->
<template>
  <div id="app">
    <BaseLayout>
      <router-view></router-view>
    </BaseLayout>
  </div>
</template>
```

```vue
<!-- BaseLayout.vue -->
<template>
  <div class="min-h-screen" style="background: linear-gradient(to right, rgba(0, 128, 0, 0.1) 0%, rgba(128, 0, 128, 0.1) 100%);">
    <slot />
  </div>
</template>
```

#### Component Standards
- **No Individual Backgrounds**: Vue components should NOT define their own background styles
- **Gradient Inheritance**: All pages inherit the universal gradient from BaseLayout
- **Button Styling**: UI element gradients (like blue-to-cyan buttons) are preserved
- **Consistency**: Eliminates background inconsistencies and copy-paste drift

#### Migration Benefits
- **Single Source**: Background changes made in one place apply universally
- **Maintainability**: No more scattered background styles across components
- **Consistency**: Uniform visual experience across all pages
- **Design System Foundation**: Establishes pattern for other global styles

## Code Reusability & DRY Principles

The application implements extensive code reuse patterns to eliminate duplication and ensure consistency across modules.

### 1. Backend Employee Search Abstraction

#### Unified Search Function
```python
# Location: backend/app.py (lines 46-133)
def search_employees_by_name(cursor, company_id, name_search, context='all', limit=10):
```

**Features:**
- **AES Decryption:** Handles encrypted employee names consistently
- **Database Joins:** Includes department, rank, and location data
- **Context Filtering:** Supports different search contexts
- **Reusable Parameters:** Configurable search terms and limits

**Context Options:**
- `context='shifts'` - employees with shift assignments
- `context='payslip'` - employees with payroll data  
- `context='all'` - no additional filtering

#### Unified API Endpoint
```python
# Replaces multiple endpoint patterns
/api/search-employees-by-name/<company_id>/<name_search>?context=<context>&limit=<limit>
```

**Usage:**
- Payslip module: `context=payslip`
- Shifts module: `context=shifts`
- General search: `context=all`

### 2. Frontend Component Reusability

#### Employee Search Component
```vue
<!-- Location: frontend/src/components/EmployeeSearch.vue -->
<EmployeeSearch 
  :company-id="companyId"
  context="shifts"
  placeholder="search by name..."
  @employee-selected="handleSelection"
/>
```

**Features:**
- **Debounced Search:** 300ms delay for optimal UX
- **Consistent Display:** "FirstName LastName (emp_id)" format
- **Dropdown Interface:** Clean selection experience
- **Error Handling:** Unified error states and messaging

**Reused In:**
- `EmployeeShifts.vue` (shifts context)
- `Employees.vue` (payslip context)

#### Paginated Table Component
```vue
<!-- Location: frontend/src/components/PaginatedTable.vue -->
<PaginatedTable 
  :data="tableData"
  :items-per-page="20"
  record-type="shift changes"
  :subtitle-text="descriptiveText"
>
  <template #table="{ paginatedData }">
    <!-- Custom table content -->
  </template>
  <template #actions>
    <!-- Custom action buttons -->
  </template>
</PaginatedTable>
```

**Features:**
- **Flexible Slots:** Custom table content and action buttons
- **Pagination Logic:** Previous/next controls with page information
- **Responsive Design:** Consistent styling across screen sizes
- **Data Management:** Auto-resets pagination when data changes

**Reused In:**
- `EmployeeShiftHistory.vue` (individual employee shifts)
- `ShiftsChangesResults.vue` (period-based change analysis)

### 3. Period-Based Change Detection

#### Backend Algorithm
```python
# Location: backend/app.py (lines 540-683)
@app.route('/api/shifts-changes-by-period/<int:company_id>/<string:date_from>/<string:date_to>')
```

**Features:**
- **Efficient O(n) Processing:** Single query with in-memory analysis
- **Date Range Validation:** Enforces 2-7 day periods
- **Change Detection:** Compares consecutive shift assignments
- **Deduplication:** Removes duplicate change records

**Algorithm Steps:**
1. Single query for all shifts in period with AES decryption
2. Sort by employee ID and date for optimal processing
3. Track last shift per employee in HashMap
4. Detect changes when shift type or name differs
5. Deduplicate and sort results by employee name

### 4. Standardized Data Formatting

#### Consistent Patterns
- **Employee Display:** `"${firstName} ${lastName} (${empId})"`
- **Date Formatting:** Short month format with consistent locale
- **Error Handling:** Unified try-catch patterns with user-friendly messages
- **Loading States:** Consistent spinner and messaging across components

#### Eliminated Duplication
- **Old Search Endpoint:** Removed `/api/search-employees` (emp_id only)
- **Duplicate UI Logic:** Consolidated search interfaces
- **Custom Pagination:** Extracted into reusable component
- **Inconsistent Formatting:** Unified date, name, and error displays

### 5. Component Communication Standards

#### Props Interface
```javascript
// Consistent prop patterns across reusable components
props: {
  companyId: { type: String, required: true },
  context: { type: String, default: 'all' },
  itemsPerPage: { type: Number, default: 20 },
  placeholder: { type: String, default: 'search...' }
}
```

#### Event Patterns
```javascript
// Standardized event naming and payload structure
this.$emit('employee-selected', { emp_id, first_name, last_name, ... });
this.$emit('data-updated', { total: count, filtered: filteredCount });
```

## Charting Standards

### 1. Unified Chart Architecture

#### Core Utilities (`src/utils/chartAxis.js`)
- **`getUnifiedStackedBarChart()`**: For simple single-value charts (shifts analytics), now supports per-period stacking order.
- **`getUnifiedPayslipChart()`**: For multi-period, multi-field charts (payslip analytics), now supports per-period stacking order.
- **`getStackingOrderForPeriods()`**: Utility to compute correct stacking order for each period, used by all chart utilities.
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
- **Stacking Order:** By default, each period’s bar stacks fields/items in ascending order of value for that period (per-period stacking). Legacy global stacking is available for backward compatibility.
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

#### Stacking Algorithm Fix (Critical)
- **Problem:** Individual value mapping for stacked charts was mathematically incorrect
- **Issue:** Mapping each value individually (91→X, 100→Y, 114→Z) then stacking X+Y+Z ≠ correct total
- **Solution:** Cumulative position mapping with incremental heights
- **2024 Update:** Stacking order is now determined per period, not globally. The new utility `getStackingOrderForPeriods` ensures each bar is stacked in the correct order for its period. All chart utilities support this for maximum flexibility and accuracy. Legacy global stacking is still supported for backward compatibility.
- **Implementation:**
  1. Calculate cumulative values: [91, 191, 305]
  2. Map cumulative values to log positions: [logPos(91), logPos(191), logPos(305)]
  3. Calculate incremental heights: [logPos(91), logPos(191)-logPos(91), logPos(305)-logPos(191)]
  4. Chart.js stacks incremental heights to reach correct total
- **Result:** Stacked bars now perfectly reach top tick marks

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
- [ ] Ensure proper stacking order (per-period stacking, unless global stacking is required)
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

#### Shifts Allocation Fix Example
- **Values:** [91, 100, 114] (employee counts by shift)
- **Problem (Before Fix):** Individual mappings summed to ~164, chart stopped mid-way
- **Solution (After Fix):** Cumulative mapping [91, 191, 305] with incremental heights
- **Result:** Chart perfectly reaches top tick at 305

## Development Guidelines

### Code Standards
- Follow Vue.js best practices and composition API patterns
- Use TypeScript-style JSDoc comments for documentation
- Implement proper error handling and loading states
- Maintain consistent naming conventions across components

### User Interface Standards
- **Text Case Convention:** All system-generated text must be lowercase
  - Button labels: "schedule type", "allocation", "by employee" (not "Schedule Type", "Allocation")
  - Page titles: "payslip analytics", "shifts selection" (not "Payslip Analytics", "Shifts Selection")
  - Menu items: "home", "analytics", "shifts" (not "Home", "Analytics", "Shifts")
  - Chart labels and legends: use lowercase throughout
  - **Exception:** User-entered data (names, company names) should preserve original case
  - **Exception:** Proper nouns and acronyms (API, URL, etc.) maintain standard capitalization

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

#### AES Decryption Optimization (Critical Performance Fix)
- **Problem:** Original `/api/analytics/` endpoint used O(n×m×db) nested loops for AES decryption
- **Impact:** For 100 payslip rows × 5 fields = 500 separate database calls per request
- **Solution:** Migrated to SQL-based AES decryption pattern from `/api/analytics-prefetch/`
- **Implementation:**
  ```sql
  -- Before (nested loops with separate DB calls)
  for row in rows:
      for field in fields:
          cursor.execute("SELECT CAST(AES_DECRYPT(%s, %s) AS DECIMAL(10,2))", (row[field], key))
  
  -- After (single SQL query with built-in decryption)
  SELECT CAST(AES_DECRYPT(field1, %s) AS DECIMAL(10,2)) AS field1,
         CAST(AES_DECRYPT(field2, %s) AS DECIMAL(10,2)) AS field2
  FROM payroll_payslip WHERE conditions...
  ```
- **Result:** 500x performance improvement (500 DB calls → 1 DB call)
- **Affected Endpoints:** Both "separate" and "single/aggregate" analytics paths
- **Verification:** Functionality remains identical, only performance improved

## Database Considerations

#### Indexes for Analytics Performance
- The following indexes are created for efficient analytics queries:
  - `payroll_payslip(company_id, period_from, period_to)`
  - `payroll_payslip(company_id, emp_id)`
  - `payroll_payslip(company_id, emp_id, period_from, period_to)`
  - `payroll_payslip(company_id, payroll_group_id)`
  - `employee_payroll_information(company_id, department_id)`
  - `employee_payroll_information(company_id, rank_id)`
  - `employee_payroll_information(company_id, employment_type)`
  - `employee_payroll_information(company_id, position)`
  - `employee_payroll_information(company_id, cost_center)`
  - `employee_payroll_information(company_id, project_id)`
  - `employee_payroll_information(company_id, location_and_offices_id)`
- These indexes ensure that all main WHERE clauses and JOINs in payslip analytics endpoints are covered for optimal performance.

### MySQL Reserved Keywords
When working with database queries, be aware of MySQL reserved keywords that require special handling:

#### `rank`