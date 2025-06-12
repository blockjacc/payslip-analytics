import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import FieldSelection from '../views/FieldSelection.vue'
import Employees from '../views/Employees.vue'
import DateRange from '../views/DateRange.vue'
import Analytics from '../views/Analytics.vue'
import AggregationChoice from '../views/AggregationChoice.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 