import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { AdminApiService } from '../../services/admin-api.service';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatIconModule, MatButtonModule, MatChipsModule],
  template: `
    <h2>User Management</h2>
    <mat-card class="table-card">
      <table mat-table [dataSource]="users" class="user-table">
        <ng-container matColumnDef="username">
          <th mat-header-cell *matHeaderCellDef>Username</th>
          <td mat-cell *matCellDef="let user">{{ user.username }}</td>
        </ng-container>
        <ng-container matColumnDef="email">
          <th mat-header-cell *matHeaderCellDef>Email</th>
          <td mat-cell *matCellDef="let user">{{ user.email }}</td>
        </ng-container>
        <ng-container matColumnDef="role">
          <th mat-header-cell *matHeaderCellDef>Role</th>
          <td mat-cell *matCellDef="let user">
            <mat-chip-option [class]="'role-' + user.role">{{ user.role }}</mat-chip-option>
          </td>
        </ng-container>
        <ng-container matColumnDef="organization">
          <th mat-header-cell *matHeaderCellDef>Organization</th>
          <td mat-cell *matCellDef="let user">{{ user.organization || 'N/A' }}</td>
        </ng-container>
        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>Status</th>
          <td mat-cell *matCellDef="let user">
            <span class="status" [class.active]="user.is_active">{{ user.is_active ? 'Active' : 'Inactive' }}</span>
          </td>
        </ng-container>
        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>
    </mat-card>
  `,
  styles: [`
    h2 { font-weight: 700; margin-bottom: 24px; color: #e0e0e0; }
    .table-card { background: #12122a; border: 1px solid rgba(108,99,255,0.1); overflow: auto; }
    .user-table { width: 100%; background: transparent; }
    th { color: #a0a0b0 !important; font-weight: 600; }
    td { color: #e0e0e0; }
    .status { font-size: 12px; padding: 2px 8px; border-radius: 4px; background: rgba(255,107,107,0.15); color: #ff6b6b; }
    .status.active { background: rgba(0,212,170,0.15); color: #00d4aa; }
  `],
})
export class UserManagementComponent implements OnInit {
  users: any[] = [];
  displayedColumns = ['username', 'email', 'role', 'organization', 'status'];

  constructor(private adminApi: AdminApiService) {}

  ngOnInit(): void {
    this.adminApi.getUsers().subscribe({
      next: (data: any) => (this.users = data.results || data || []),
      error: (err: any) => console.error('Failed to fetch users:', err),
    });
  }
}
