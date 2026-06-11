import { Routes } from '@angular/router';

export const routes: Routes = [
  // Routes will be registered as features are built
  // { path: 'dashboard', loadChildren: () => import('./features/dashboard/dashboard.module') },
  // { path: 'screening', loadChildren: () => import('./features/screening/screening.module') },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: '/dashboard' },
];
