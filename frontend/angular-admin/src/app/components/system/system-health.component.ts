import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { AdminApiService } from '../../services/admin-api.service';

@Component({
  selector: 'app-system-health',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatProgressBarModule],
  template: `
    <h2>System Health</h2>
    <div class="health-grid">
      <mat-card *ngFor="let svc of services" class="health-card" [class.healthy]="svc.status === 'healthy'" [class.unhealthy]="svc.status !== 'healthy'">
        <mat-card-content>
          <div class="svc-header">
            <mat-icon>{{ svc.status === 'healthy' ? 'check_circle' : 'error' }}</mat-icon>
            <span class="svc-name">{{ svc.name }}</span>
          </div>
          <div class="svc-details">
            <span>Port: {{ svc.port }}</span>
            <span>Uptime: {{ svc.uptime }}</span>
          </div>
          <mat-progress-bar [mode]="'determinate'" [value]="svc.cpu" [color]="svc.cpu > 80 ? 'warn' : 'primary'"></mat-progress-bar>
          <span class="cpu-label">CPU: {{ svc.cpu }}%</span>
        </mat-card-content>
      </mat-card>
    </div>

    <mat-card class="info-card">
      <mat-card-content>
        <h3>Infrastructure Overview</h3>
        <div class="info-grid">
          <div class="info-item"><span class="info-label">Kubernetes Cluster</span><span class="info-value">datapulse-production</span></div>
          <div class="info-item"><span class="info-label">Region</span><span class="info-value">us-east-1</span></div>
          <div class="info-item"><span class="info-label">Nodes</span><span class="info-value">3 / 10</span></div>
          <div class="info-item"><span class="info-label">Pods Running</span><span class="info-value">12</span></div>
          <div class="info-item"><span class="info-label">Docker Images</span><span class="info-value">5 latest</span></div>
          <div class="info-item"><span class="info-label">Last Deploy</span><span class="info-value">2 hours ago</span></div>
        </div>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    h2 { font-weight: 700; margin-bottom: 24px; color: #e0e0e0; }
    h3 { font-weight: 600; margin-bottom: 16px; color: #e0e0e0; }
    .health-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .health-card { background: #12122a; border: 1px solid rgba(108,99,255,0.1); }
    .health-card.healthy { border-left: 4px solid #00d4aa; }
    .health-card.unhealthy { border-left: 4px solid #ff6b6b; }
    .svc-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
    .svc-header mat-icon { font-size: 20px; width: 20px; height: 20px; }
    .healthy .svc-header mat-icon { color: #00d4aa; }
    .unhealthy .svc-header mat-icon { color: #ff6b6b; }
    .svc-name { font-weight: 600; color: #e0e0e0; }
    .svc-details { display: flex; justify-content: space-between; font-size: 12px; color: #a0a0b0; margin-bottom: 12px; }
    .cpu-label { font-size: 11px; color: #a0a0b0; margin-top: 4px; display: block; }
    .info-card { background: #12122a; border: 1px solid rgba(108,99,255,0.1); }
    .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
    .info-item { display: flex; flex-direction: column; }
    .info-label { font-size: 12px; color: #a0a0b0; }
    .info-value { font-size: 16px; font-weight: 500; color: #e0e0e0; }
  `],
})
export class SystemHealthComponent implements OnInit {
  services = [
    { name: 'Django API', port: 8000, status: 'healthy', uptime: '14d 6h', cpu: 35 },
    { name: 'FastAPI Ingestion', port: 8001, status: 'healthy', uptime: '14d 6h', cpu: 22 },
    { name: 'Flask AI Service', port: 5001, status: 'healthy', uptime: '14d 5h', cpu: 45 },
    { name: 'PostgreSQL', port: 5432, status: 'healthy', uptime: '30d 2h', cpu: 28 },
    { name: 'MongoDB', port: 27017, status: 'healthy', uptime: '30d 2h', cpu: 18 },
    { name: 'Elasticsearch', port: 9200, status: 'healthy', uptime: '14d 6h', cpu: 52 },
    { name: 'Kafka', port: 9092, status: 'healthy', uptime: '14d 6h', cpu: 30 },
    { name: 'RabbitMQ', port: 5672, status: 'healthy', uptime: '14d 6h', cpu: 12 },
    { name: 'Redis', port: 6379, status: 'healthy', uptime: '30d 2h', cpu: 8 },
    { name: 'Grafana', port: 3001, status: 'healthy', uptime: '14d 6h', cpu: 15 },
    { name: 'Kibana', port: 5601, status: 'healthy', uptime: '14d 6h', cpu: 20 },
  ];

  constructor(private adminApi: AdminApiService) {}

  ngOnInit(): void {
    this.adminApi.getSystemHealth().subscribe({
      next: (data: any) => {
        if (data.status === 'healthy') {
          this.services[0].status = 'healthy';
        }
      },
      error: () => {
        this.services[0].status = 'unhealthy';
      },
    });
  }
}
