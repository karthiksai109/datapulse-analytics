import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AdminApiService } from '../../services/admin-api.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatProgressSpinnerModule],
  template: `
    <h2>Admin Dashboard</h2>
    <div class="stats-grid">
      <mat-card class="stat-card">
        <mat-card-content>
          <mat-icon>people</mat-icon>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.dashboards || 0 }}</span>
            <span class="stat-label">Total Dashboards</span>
          </div>
        </mat-card-content>
      </mat-card>
      <mat-card class="stat-card">
        <mat-card-content>
          <mat-icon>event</mat-icon>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.events_today || 0 }}</span>
            <span class="stat-label">Events Today</span>
          </div>
        </mat-card-content>
      </mat-card>
      <mat-card class="stat-card">
        <mat-card-content>
          <mat-icon>notifications_active</mat-icon>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.active_alerts || 0 }}</span>
            <span class="stat-label">Active Alerts</span>
          </div>
        </mat-card-content>
      </mat-card>
      <mat-card class="stat-card">
        <mat-card-content>
          <mat-icon>assessment</mat-icon>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.reports_generated || 0 }}</span>
            <span class="stat-label">Reports Generated</span>
          </div>
        </mat-card-content>
      </mat-card>
    </div>

    <div class="section">
      <h3>System Services</h3>
      <div class="services-grid">
        <mat-card *ngFor="let service of services" class="service-card">
          <mat-card-content>
            <div class="service-header">
              <span class="service-name">{{ service.name }}</span>
              <span class="service-status" [class.healthy]="service.healthy" [class.unhealthy]="!service.healthy">
                {{ service.healthy ? 'Healthy' : 'Down' }}
              </span>
            </div>
            <span class="service-port">Port: {{ service.port }}</span>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    h2 { font-weight: 700; margin-bottom: 24px; color: #e0e0e0; }
    h3 { font-weight: 600; margin-bottom: 16px; color: #e0e0e0; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 32px; }
    .stat-card { background: #12122a; border: 1px solid rgba(108,99,255,0.1); }
    .stat-card mat-card-content { display: flex; align-items: center; gap: 16px; padding: 20px; }
    .stat-card mat-icon { font-size: 36px; width: 36px; height: 36px; color: #6c63ff; }
    .stat-info { display: flex; flex-direction: column; }
    .stat-value { font-size: 28px; font-weight: 700; color: #e0e0e0; }
    .stat-label { font-size: 13px; color: #a0a0b0; }
    .section { margin-top: 24px; }
    .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
    .service-card { background: #12122a; border: 1px solid rgba(108,99,255,0.1); }
    .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .service-name { font-weight: 500; color: #e0e0e0; }
    .service-status { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .healthy { background: rgba(0,212,170,0.15); color: #00d4aa; }
    .unhealthy { background: rgba(255,107,107,0.15); color: #ff6b6b; }
    .service-port { font-size: 12px; color: #a0a0b0; }
  `],
})
export class AdminDashboardComponent implements OnInit {
  stats: any = {};
  services = [
    { name: 'Django API', port: 8000, healthy: true },
    { name: 'FastAPI Ingestion', port: 8001, healthy: true },
    { name: 'Flask AI Service', port: 5001, healthy: true },
    { name: 'PostgreSQL', port: 5432, healthy: true },
    { name: 'MongoDB', port: 27017, healthy: true },
    { name: 'Elasticsearch', port: 9200, healthy: true },
    { name: 'Kafka', port: 9092, healthy: true },
    { name: 'RabbitMQ', port: 5672, healthy: true },
    { name: 'Redis', port: 6379, healthy: true },
  ];

  constructor(private adminApi: AdminApiService) {}

  ngOnInit(): void {
    this.adminApi.getUserStats().subscribe({
      next: (data) => (this.stats = data),
      error: (err) => console.error('Failed to fetch stats:', err),
    });
  }
}
