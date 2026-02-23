import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule, RouterOutlet, RouterLink, RouterLinkActive,
    MatSidenavModule, MatToolbarModule, MatListModule, MatIconModule, MatButtonModule,
  ],
  template: `
    <mat-toolbar color="primary" class="toolbar">
      <button mat-icon-button (click)="sidenavOpen = !sidenavOpen">
        <mat-icon>menu</mat-icon>
      </button>
      <span class="brand">DataPulse Admin</span>
      <span class="spacer"></span>
      <button mat-icon-button><mat-icon>notifications</mat-icon></button>
      <button mat-icon-button><mat-icon>account_circle</mat-icon></button>
    </mat-toolbar>

    <mat-sidenav-container class="sidenav-container">
      <mat-sidenav [opened]="sidenavOpen" mode="side" class="sidenav">
        <mat-nav-list>
          <a mat-list-item routerLink="/admin/dashboard" routerLinkActive="active">
            <mat-icon matListItemIcon>dashboard</mat-icon>
            <span matListItemTitle>Dashboard</span>
          </a>
          <a mat-list-item routerLink="/admin/users" routerLinkActive="active">
            <mat-icon matListItemIcon>people</mat-icon>
            <span matListItemTitle>User Management</span>
          </a>
          <a mat-list-item routerLink="/admin/system" routerLinkActive="active">
            <mat-icon matListItemIcon>settings</mat-icon>
            <span matListItemTitle>System Health</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>

      <mat-sidenav-content class="content">
        <router-outlet></router-outlet>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    .toolbar { position: fixed; z-index: 1000; background: linear-gradient(135deg, #1a1a2e, #16213e); }
    .brand { font-weight: 700; margin-left: 8px; background: linear-gradient(135deg, #6c63ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .spacer { flex: 1 1 auto; }
    .sidenav-container { position: absolute; top: 64px; bottom: 0; left: 0; right: 0; }
    .sidenav { width: 240px; background: #0d0d20; border-right: 1px solid rgba(108,99,255,0.1); }
    .content { padding: 24px; background: #0a0a1a; min-height: 100%; }
    .active { background: rgba(108,99,255,0.15) !important; }
  `],
})
export class AppComponent {
  sidenavOpen = true;
}
