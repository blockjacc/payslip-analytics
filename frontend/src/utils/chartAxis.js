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

// Simple y-axis configuration that forces chart to start at 0
export function getSimpleYAxis(values) {
  const nonZero = values.filter(v => v > 0);
  console.log('getSimpleYAxis called with:', values, 'nonZero:', nonZero);
  
  if (nonZero.length === 0) {
    console.log('No nonzero values, returning default');
    return { min: 0, max: 1, ticks: [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] };
  }
  
  const min = Math.min(...nonZero);
  const totalSum = nonZero.reduce((sum, v) => sum + v, 0);
  
  console.log('min:', min, 'totalSum:', totalSum);
  
  // 11 ticks: 0, min, then 9 more logarithmic steps to totalSum
  const ticks = [0, min];
  
  // Generate 9 logarithmic steps from min to totalSum
  for (let i = 1; i <= 9; i++) {
    const t = min * Math.pow(totalSum / min, i / 9);
    ticks.push(Math.round(t));
  }
  
  // Ensure last tick is exactly the total sum
  ticks[10] = totalSum;
  
  console.log('Generated ticks:', ticks);
  
  return {
    min: 0,
    max: totalSum,
    ticks: ticks
  };
} 