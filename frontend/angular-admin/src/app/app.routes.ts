import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'admin/dashboard', pathMatch: 'full' },
  {
    path: 'admin/dashboard',
    loadComponent: () =>
      import('./components/dashboard/admin-dashboard.component').then(
        (m) => m.AdminDashboardComponent
      ),
  },
  {
    path: 'admin/users',
    loadComponent: () =>
      import('./components/users/user-management.component').then(
        (m) => m.UserManagementComponent
      ),
  },
  {
    path: 'admin/system',
    loadComponent: () =>
      import('./components/system/system-health.component').then(
        (m) => m.SystemHealthComponent
      ),
  },
];
