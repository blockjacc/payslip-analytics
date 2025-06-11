import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Employees from '../views/Employees.vue'
import DateRange from '../views/DateRange.vue'
import Analytics from '../views/Analytics.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
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
    path: '/analytics/:companyId/:employeeId/:periodFrom/:periodTo',
    name: 'Analytics',
    component: Analytics
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 