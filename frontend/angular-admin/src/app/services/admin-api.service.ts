import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getUsers(page: number = 1): Observable<any> {
    return this.http.get(`${this.apiUrl}/users/`, { params: { page: page.toString() } });
  }

  getUserStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/users/stats/`);
  }

  getDashboards(): Observable<any> {
    return this.http.get(`${this.apiUrl}/analytics/dashboards/`);
  }

  getDataSources(): Observable<any> {
    return this.http.get(`${this.apiUrl}/analytics/sources/`);
  }

  getAlerts(): Observable<any> {
    return this.http.get(`${this.apiUrl}/analytics/alerts/`);
  }

  getSystemHealth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health/live/`);
  }

  getReadiness(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health/ready/`);
  }
}
