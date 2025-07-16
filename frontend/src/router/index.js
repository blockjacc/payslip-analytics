import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ModuleSelection from '../views/ModuleSelection.vue'
import FieldSelection from '../views/FieldSelection.vue'
import Employees from '../views/Employees.vue'
import DateRange from '../views/DateRange.vue'
import Analytics from '../views/Analytics.vue'
import AggregationChoice from '../views/AggregationChoice.vue'
import DrillDown from '../views/DrillDown.vue'
import ShiftsSelection from '../views/ShiftsSelection.vue'
import ShiftsScheduleTypeSelection from '../views/ShiftsScheduleTypeSelection.vue'
import ShiftsScheduleTypeAnalytics from '../views/ShiftsScheduleTypeAnalytics.vue'
import ShiftsChangesDatePicker from '../views/ShiftsChangesDatePicker.vue'
import ShiftsChangesResults from '../views/ShiftsChangesResults.vue'
import ShiftsAllocationSelection from '../views/ShiftsAllocationSelection.vue'
import ShiftsAllocationAnalytics from '../views/ShiftsAllocationAnalytics.vue'
import ShiftsAllocationDrilldown from '../views/ShiftsAllocationDrilldown.vue'
import ShiftsAllocationDrilldownPicker from '../views/ShiftsAllocationDrilldownPicker.vue'
import ShiftsAllocationDrilldownTable from '../views/ShiftsAllocationDrilldownTable.vue'
import ShiftsStartTimeInput from '../views/ShiftsStartTimeInput.vue'
import ShiftsStartTimeConfigSelection from '../views/ShiftsStartTimeConfigSelection.vue'
import ShiftsStartTimeAnalytics from '../views/ShiftsStartTimeAnalytics.vue'
import EmployeeShifts from '../views/EmployeeShifts.vue'
import EmployeeShiftHistory from '../views/EmployeeShiftHistory.vue'
import EmployeeScheduleChanges from '../views/EmployeeScheduleChanges.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/module-selection/:companyId',
    name: 'ModuleSelection',
    component: ModuleSelection
  },
  {
    path: '/field-selection/:companyId',
    name: 'FieldSelection',
    component: FieldSelection
  },
  {
    path: '/employees/:companyId',
    name: 'Employees',
    component: Employees
  },
  {
    path: '/dates/:companyId/:employeeId',
    name: 'DateRange',
    component: DateRange
  },
  {
    path: '/aggregation/:companyId/:employeeId/:periodFrom/:periodTo',
    name: 'AggregationChoice',
    component: AggregationChoice
  },
  {
    path: '/analytics/:companyId/:employeeId/:periodFrom/:periodTo/:aggregationType?',
    name: 'Analytics',
    component: Analytics
  },
  {
    path: '/analytics-prefetch-test',
    name: 'AnalyticsPrefetchTest',
    component: () => import('../views/AnalyticsPrefetchTest.vue')
  },
  {
    path: '/drilldown/:companyId/:employeeId/:periodFrom/:periodTo/:aggregationType',
    name: 'DrillDown',
    component: DrillDown
  },
  {
    path: '/shifts-selection/:companyId',
    name: 'ShiftsSelection',
    component: ShiftsSelection
  },
  {
    path: '/shifts-schedule-type-selection/:companyId',
    name: 'ShiftsScheduleTypeSelection',
    component: ShiftsScheduleTypeSelection
  },
  {
    path: '/shifts-schedule-type-analytics/:companyId',
    name: 'ShiftsScheduleTypeAnalytics',
    component: ShiftsScheduleTypeAnalytics
  },
  {
    path: '/shifts-changes-date-picker/:companyId',
    name: 'ShiftsChangesDatePicker',
    component: ShiftsChangesDatePicker
  },
  {
    path: '/shifts-changes-results/:companyId/:fromDate/:toDate',
    name: 'ShiftsChangesResults',
    component: ShiftsChangesResults
  },
  {
    path: '/shifts-allocation-selection/:companyId',
    name: 'ShiftsAllocationSelection',
    component: ShiftsAllocationSelection
  },
  {
    path: '/shifts-allocation-analytics/:companyId/:scheduleType/:shiftIds',
    name: 'ShiftsAllocationAnalytics',
    component: ShiftsAllocationAnalytics
  },
  {
    path: '/shifts-allocation-drilldown/:companyId/:scheduleType/:shiftIds',
    name: 'ShiftsAllocationDrilldownPicker',
    component: ShiftsAllocationDrilldownPicker
  },
  {
    path: '/shifts-allocation-drilldown/:companyId/:scheduleType/:shiftIds/:shiftId',
    name: 'ShiftsAllocationDrilldownTable',
    component: ShiftsAllocationDrilldownTable
  },
  {
    path: '/shifts-start-time-input/:companyId',
    name: 'ShiftsStartTimeInput',
    component: ShiftsStartTimeInput
  },
  {
    path: '/shifts-start-time-config-selection/:companyId',
    name: 'ShiftsStartTimeConfigSelection',
    component: ShiftsStartTimeConfigSelection
  },
  {
    path: '/shifts-start-time-analytics/:companyId/:startTime',
    name: 'ShiftsStartTimeAnalytics',
    component: ShiftsStartTimeAnalytics
  },
  {
    path: '/shifts-start-time-drilldown/:companyId/:shiftId',
    name: 'ShiftsStartTimeDrilldown',
    component: () => import('../views/ShiftsStartTimeDrilldown.vue')
  },
  {
    path: '/employee-shifts/:companyId',
    name: 'EmployeeShifts',
    component: EmployeeShifts
  },
  {
    path: '/employee-shift-history/:companyId/:empId',
    name: 'EmployeeShiftHistory',
    component: EmployeeShiftHistory
  },
  {
    path: '/employee-schedule-changes/:companyId/:empId',
    name: 'EmployeeScheduleChanges',
    component: EmployeeScheduleChanges
  },
  {
    path: '/deepdive/:company_id/:emp_id/:date',
    name: 'DeepDive',
    component: () => import('../views/DeepDive.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 