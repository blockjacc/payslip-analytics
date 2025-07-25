// Shared utility for dynamic log y-axis ticks for Chart.js

/**
 * Returns 11 ticks: 0, then 10 log steps from min to max (inclusive).
 * @param {number[]} values
 * @returns {{ min: number, max: number, ticks: number[] }}
 */
export function getLogYAxisConfig(values) {
  const nonZero = values.filter(v => v > 0);
  if (nonZero.length === 0) {
    return { min: 0, max: 1, ticks: [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] };
  }
  const min = Math.min(...nonZero);
  const max = Math.max(...nonZero);
  if (min === max) {
    // All values are the same, just show 0 and max
    return { min: 0, max, ticks: [0, ...Array(10).fill(max)] };
  }
  const ticks = [0];
  for (let i = 0; i < 10; i++) {
    // 10 steps from min to max, inclusive
    const t = min * Math.pow(max / min, i / 9);
    ticks.push(Math.round(t));
  }
  // Ensure last tick is exactly max
  ticks[10] = max;
  // Remove duplicates and sort
  const uniqueTicks = Array.from(new Set(ticks)).sort((a, b) => a - b);
  // If less than 11 ticks, pad with max
  while (uniqueTicks.length < 11) uniqueTicks.push(max);
  // If more than 11, trim
  return { min: 0, max, ticks: uniqueTicks.slice(0, 11) };
}

/**
 * Returns just two ticks: 0 and the smallest nonzero value.
 * @param {number[]} values
 * @returns {{ min: number, max: number, ticks: number[] }}
 */
export function getYAxisStartAndFirstTick(values) {
  const nonZero = values.filter(v => v > 0);
  if (nonZero.length === 0) {
    return { min: 0, max: 1, ticks: [0, 1] };
  }
  const min = Math.min(...nonZero);
  return { min: 0, max: min, ticks: [0, min] };
}

/**
 * Maps a data value to its logarithmic position on a linear scale
 * @param {number} value - The actual data value
 * @param {number} min - The minimum non-zero value
 * @param {number} max - The maximum value (total sum)
 * @returns {number} - The position on the linear scale
 */
function mapValueToLogPosition(value, min, max) {
  if (value <= 0) return 0;
  if (value >= max) return max;
  
  // Find which logarithmic segment this value belongs to
  const logMin = Math.log(min);
  const logMax = Math.log(max);
  const logValue = Math.log(value);
  
  // Map to position 1-10 (position 0 is reserved for zero)
  const logPosition = ((logValue - logMin) / (logMax - logMin)) * 9 + 1;
  
  // Convert to linear scale position
  return (logPosition / 10) * max;
}

// Simple y-axis configuration that forces chart to start at 0
export function getSimpleYAxis(values) {
  const nonZero = values.filter(v => v > 0);
  console.log('getSimpleYAxis called with:', values, 'nonZero:', nonZero);
  
  if (nonZero.length === 0) {
    console.log('No nonzero values, returning default');
    return { min: 0, max: 1, ticks: [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], mapValue: (v) => v };
  }
  
  const min = Math.min(...nonZero);
  const totalSum = nonZero.reduce((sum, v) => sum + v, 0);
  
  console.log('min:', min, 'totalSum:', totalSum);
  
  // 11 ticks: 0, min, then 9 more logarithmic steps to totalSum
  const ticks = [0, min]; // Keep exact min value, don't round
  
  // Generate 9 logarithmic steps from min to totalSum
  for (let i = 1; i <= 9; i++) {
    const t = min * Math.pow(totalSum / min, i / 9);
    ticks.push(t); // Keep exact values for positioning
  }
  
  // Ensure last tick is exactly the total sum
  ticks[10] = totalSum;
  
  console.log('Generated ticks:', ticks);
  console.log('First value should reach tick[1]:', ticks[1], 'min value is:', min);
  
  return {
    min: 0,
    max: totalSum,
    ticks: ticks,
    mapValue: (value) => mapValueToLogPosition(value, min, totalSum)
  };
}

/**
 * Unified chart configuration utility for consistent stacked bar charts
 * Handles both tick generation and data sorting for proper stacking (lowest to highest)
 * 
 * @param {Array} items - Array of data items to be charted
 * @param {string} valueKey - Key to access the numeric value in each item (e.g., 'count', 'value')
 * @param {string} labelKey - Key to access the label in each item (e.g., 'work_type_name', 'field_name')
 * @param {Array} colorPalette - Array of colors to use for the chart
 * @param {Object} options - Additional options
 * @returns {Object} Complete chart configuration with data and options
 */
export function getUnifiedStackedBarChart(items, valueKey, labelKey, colorPalette, options = {}) {
  // If per-period stacking is requested, compute stacking order for each period
  let stackingOrders = null;
  let periods = options.periods || [{ data: items }];
  if (options.perPeriodStacking && periods.length > 1) {
    stackingOrders = getStackingOrderForPeriods(
      periods,
      items.map(item => item[labelKey]),
      (period, field) => {
        // Find the item in this period with the given label
        const found = (period.data || []).find(i => i[labelKey] === field);
        return found ? found[valueKey] : 0;
      }
    );
  }

  // Extract values for tick generation
  let values = [];
  if (stackingOrders) {
    periods.forEach(period => {
      (period.data || []).forEach(item => {
        values.push(item[valueKey]);
      });
    });
  } else {
    values = items.map(item => item[valueKey]);
  }

  // Generate ticks using our standard utility
  const { min, max, ticks, mapValue } = getSimpleYAxis(values);

  let chartData;
  if (stackingOrders) {
    // Per-period stacking: each bar (period) has its own stacking order
    const maxFields = items.length;
    chartData = {
      labels: periods.map((period, idx) => period.label || `Period ${idx + 1}`),
      datasets: Array.from({ length: maxFields }).map((_, stackIdx) => {
        return {
          label: null, // will be set per period in tooltip
          data: periods.map((period, periodIdx) => {
            const field = stackingOrders[periodIdx][stackIdx];
            const found = (period.data || []).find(i => i[labelKey] === field);
            const value = found ? found[valueKey] : 0;
            return mapValue(value);
          }),
          backgroundColor: periods.map((period, periodIdx) => {
            const field = stackingOrders[periodIdx][stackIdx];
            const found = items.find(i => i[labelKey] === field);
            return found ? colorPalette[items.indexOf(found) % colorPalette.length] : '#24c2ab';
          }),
          borderColor: options.borderColor || '#222c44',
          borderWidth: options.borderWidth || 2,
          _fields: periods.map((period, periodIdx) => stackingOrders[periodIdx][stackIdx])
        };
      })
    };
    // Set dataset labels for legend (use first period's stacking order)
    chartData.datasets.forEach((ds, idx) => {
      const field = stackingOrders[0][idx];
      ds.label = field;
    });
  } else {
    // Default: global stacking order (legacy)
    const sortedItems = [...items].sort((a, b) => a[valueKey] - b[valueKey]);
    // Calculate cumulative positions for proper stacking
    let cumulativeValues = [];
    let runningSum = 0;
    for (const item of sortedItems) {
      runningSum += item[valueKey];
      cumulativeValues.push(runningSum);
    }
    // Map cumulative sums to logarithmic positions
    const cumulativeLogPositions = cumulativeValues.map(cumVal => mapValue(cumVal));
    // Calculate incremental heights for each segment
    const incrementalHeights = [];
    for (let i = 0; i < cumulativeLogPositions.length; i++) {
      if (i === 0) {
        incrementalHeights.push(cumulativeLogPositions[0]);
      } else {
        incrementalHeights.push(cumulativeLogPositions[i] - cumulativeLogPositions[i-1]);
      }
    }
    chartData = {
      labels: options.labels || [''],
      datasets: sortedItems.map((item, idx) => ({
        label: item[labelKey],
        data: [incrementalHeights[idx]],
        backgroundColor: colorPalette[items.indexOf(item) % colorPalette.length],
        borderColor: options.borderColor || '#222c44',
        borderWidth: options.borderWidth || 2,
        order: idx
      }))
    };
  }

  // Create chart options with our standard configuration
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { 
        display: options.showLegend !== false,
        position: options.legendPosition || 'right',
        labels: { 
          color: '#fff', 
          font: { 
            family: options.fontFamily || 'Open Sans', 
            size: options.fontSize || 14 
          } 
        } 
      },
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        titleColor: '#fff',
        titleFont: {
          family: options.fontFamily || 'Open Sans',
          size: options.fontSize || 16,
          weight: 'bold'
        },
        bodyColor: '#fff',
        bodyFont: {
          family: options.fontFamily || 'Open Sans',
          size: options.fontSize || 15
        },
        padding: 12,
        callbacks: {
          label: ctx => {
            if (ctx.dataset._fields) {
              const field = ctx.dataset._fields[ctx.dataIndex];
              const found = (periods[ctx.dataIndex].data || []).find(i => i[labelKey] === field);
              const value = found ? found[valueKey] : 0;
              return `${field}: ${value.toLocaleString('en-US')}`;
            } else {
              // Legacy/global stacking
              const originalValue = items[ctx.datasetIndex][valueKey];
              return `${ctx.dataset.label}: ${originalValue.toLocaleString('en-US')}`;
            }
          }
        }
      },
      title: { display: false }
    },
    layout: { padding: { left: 0, right: 0, top: 0, bottom: 0 } },
    scales: {
      x: {
        stacked: true,
        grid: { color: 'rgba(255,255,255,0.08)' },
        ticks: { 
          color: '#fff', 
          font: { 
            family: options.fontFamily || 'Open Sans', 
            size: options.fontSize || 16, 
            weight: 'bold' 
          } 
        }
      },
      y: {
        type: 'linear',
        stacked: true,
        min: 0,
        max: max,
        grid: { color: 'rgba(255,255,255,0.12)' },
        ticks: {
          stepSize: max / 10,
          count: 11,
          color: '#fff',
          font: { 
            family: options.fontFamily || 'Open Sans', 
            size: options.fontSize || 16, 
            weight: 'bold' 
          },
          callback: function(value, index, values) {
            if (index < ticks.length) {
              return Math.round(ticks[index]).toLocaleString('en-US');
            }
            return '';
          }
        }
      }
    }
  };
  
  return {
    chartData,
    chartOptions,
    stackingOrders,
    values,
    ticks
  };
}

/**
 * Computes per-period stacking order for fields/items.
 * For each period, returns an array of field/item keys sorted by value (ascending).
 * @param {Array} periods - Array of period objects (with summary or data)
 * @param {Array} fields - Array of field/item keys
 * @param {Function} getValue - Function (period, field) => value
 * @returns {Array<Array>} stackingOrders[periodIndex] = [field1, field2, ...]
 */
export function getStackingOrderForPeriods(periods, fields, getValue) {
  return periods.map(period => {
    return [...fields].sort((a, b) => (getValue(period, a) || 0) - (getValue(period, b) || 0));
  });
}

/**
 * Unified chart configuration for payslip analytics with multiple periods
 * Handles field sorting by total values across all periods
 * 
 * @param {Array} selectedFields - Array of field names
 * @param {Array} periods - Array of period objects with summary data
 * @param {Function} formatLabel - Function to format field labels
 * @param {Object} fieldColors - Object mapping field names to colors
 * @param {Object} options - Additional options
 * @returns {Object} Complete chart configuration with data and options
 */
export function getUnifiedPayslipChart(selectedFields, periods, formatLabel, fieldColors, options = {}) {
  // If per-period stacking is requested, compute stacking order for each period
  let stackingOrders = null;
  if (options.perPeriodStacking) {
    stackingOrders = getStackingOrderForPeriods(
      periods,
      selectedFields,
      (period, field) => period.summary ? period.summary[field] || 0 : 0
    );
  }

  // Extract all values for tick generation
  const values = [];
  periods.forEach(period => {
    selectedFields.forEach(field => {
      values.push(period.summary ? period.summary[field] || 0 : 0);
    });
  });

  // Generate ticks using our standard utility
  const { min, max, ticks, mapValue } = getSimpleYAxis(values);

  // Create chart data with logarithmically positioned values
  let chartData;
  if (stackingOrders) {
    // Per-period stacking: each bar (period) has its own stacking order
    // For Chart.js, we need to build datasets so that for each field, the data array aligns with the stacking order for each period
    // We'll transpose the data: for each period, for each field in that period's stacking order, assign the mapped value
    // To do this, we need to build datasets for all unique fields across all periods, but order the data in each period by that period's stacking order
    // For each period, stackingOrders[periodIdx] gives the order for that period
    // We'll build one dataset per field, but in each period, the value will be 0 unless that field is at the correct stacking position
    // Instead, we will build one dataset per stacking position (max fields), and in each period, the dataset at that position is the field at that stacking order for that period
    // This way, the stacking order is correct per period
    const maxFields = selectedFields.length;
    chartData = {
      labels: periods.map(period => period.label),
      datasets: Array.from({ length: maxFields }).map((_, stackIdx) => {
        return {
          label: null, // will be set per period in tooltip
          data: periods.map((period, periodIdx) => {
            const field = stackingOrders[periodIdx][stackIdx];
            const value = period.summary ? period.summary[field] || 0 : 0;
            return mapValue(value);
          }),
          backgroundColor: periods.map((period, periodIdx) => {
            const field = stackingOrders[periodIdx][stackIdx];
            return fieldColors[field] || '#24c2ab';
          }),
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          // Custom property to help with tooltips
          _fields: periods.map((period, periodIdx) => stackingOrders[periodIdx][stackIdx])
        };
      })
    };
    // Set dataset labels for legend (use first period's stacking order)
    chartData.datasets.forEach((ds, idx) => {
      const field = stackingOrders[0][idx];
      ds.label = formatLabel(field);
    });
  } else {
    // Default: global stacking order (legacy)
    // Calculate total values for each field across all periods
    const fieldTotals = {};
    selectedFields.forEach(field => {
      fieldTotals[field] = periods.reduce((sum, period) => 
        sum + (period.summary ? period.summary[field] || 0 : 0), 0);
    });
    // Sort fields by their total values (lowest to highest) for proper stacking
    const sortedFields = [...selectedFields].sort((a, b) => fieldTotals[a] - fieldTotals[b]);
    chartData = {
      labels: periods.map(period => period.label),
      datasets: sortedFields.map(field => ({
        label: formatLabel(field),
        data: periods.map(period => {
          const originalValue = period.summary ? period.summary[field] || 0 : 0;
          return mapValue(originalValue); // Map to logarithmic position
        }),
        backgroundColor: fieldColors[field] || '#24c2ab',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1
      }))
    };
  }
  
  // Create chart options with our standard configuration
  const aggregationType = options.aggregationType || 'single';
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        type: 'linear',
        display: true,
        min: 0,
        max: max,
        stacked: true,
        ticks: {
          stepSize: max / 10,
          count: 11,
          color: '#fff',
          font: {
            family: "'Open Sans', sans-serif",
            size: 12
          },
          callback: function(value, index, values) {
            if (index < ticks.length) {
              return Math.round(ticks[index]).toLocaleString('en-US');
            }
            return '';
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        stacked: true,
        ticks: {
          color: '#fff',
          font: {
            family: "'Open Sans', sans-serif",
            size: 12
          },
          maxRotation: 45,
          minRotation: 45
        },
        grid: {
          display: false
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'right',
        labels: {
          color: '#fff',
          font: {
            family: "'Open Sans', sans-serif",
            size: 12
          }
        }
      },
      tooltip: {
        enabled: true,
        mode: aggregationType === 'separate' ? 'nearest' : 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        titleFont: {
          family: "'Open Sans', sans-serif",
          size: 12
        },
        bodyColor: '#fff',
        bodyFont: {
          family: "'Open Sans', sans-serif",
          size: 12
        },
        padding: 10,
        callbacks: {
          label: function(context) {
            // For per-period stacking, use _fields to get the field for this period/stack
            if (context.dataset._fields) {
              const field = context.dataset._fields[context.dataIndex];
              const label = formatLabel(field);
              const period = periods[context.dataIndex];
              const value = period.summary ? period.summary[field] || 0 : 0;
              return `${label}: ${value.toLocaleString('en-US')}`;
            } else {
              // Legacy/global stacking
              const label = context.dataset.label || '';
              const fieldIndex = selectedFields.findIndex(f => formatLabel(f) === label);
              const field = selectedFields[fieldIndex];
              const originalValue = periods[context.dataIndex].summary ? periods[context.dataIndex].summary[field] || 0 : 0;
              return `${label}: ${originalValue.toLocaleString('en-US')}`;
            }
          }
        }
      }
    }
  };
  
  return {
    chartData,
    chartOptions,
    stackingOrders,
    values,
    ticks
  };
} 