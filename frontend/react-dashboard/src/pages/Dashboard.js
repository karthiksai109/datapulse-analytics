import React, { useState, useEffect } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Chip, Skeleton,
} from '@mui/material';
import { Storage, Event, NotificationsActive, TrendingUp } from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../services/api';

const COLORS = ['#6c63ff', '#00d4aa', '#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff'];

const StatCard = ({ title, value, icon, color, trend }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>{title}</Typography>
          <Typography variant="h4" sx={{ fontWeight: 700, color }}>{value}</Typography>
          {trend && (
            <Chip
              icon={<TrendingUp sx={{ fontSize: 14 }} />}
              label={trend}
              size="small"
              sx={{ mt: 1, bgcolor: 'rgba(0, 212, 170, 0.1)', color: '#00d4aa', fontSize: '0.75rem' }}
            />
          )}
        </Box>
        <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: `${color}15` }}>
          {React.cloneElement(icon, { sx: { color, fontSize: 28 } })}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [eventsOverTime, setEventsOverTime] = useState([]);
  const [eventsByType, setEventsByType] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes] = await Promise.all([
        api.get('/users/stats/'),
      ]);
      setStats(statsRes.data);

      // Mock chart data for display
      setEventsOverTime([
        { time: '00:00', events: 120, processed: 115 },
        { time: '04:00', events: 85, processed: 82 },
        { time: '08:00', events: 340, processed: 330 },
        { time: '12:00', events: 520, processed: 510 },
        { time: '16:00', events: 480, processed: 470 },
        { time: '20:00', events: 290, processed: 285 },
        { time: '23:59', events: 150, processed: 145 },
      ]);

      setEventsByType([
        { name: 'API Calls', value: 4200 },
        { name: 'User Actions', value: 2800 },
        { name: 'System Events', value: 1500 },
        { name: 'Webhooks', value: 900 },
        { name: 'Alerts', value: 350 },
      ]);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setStats({ dashboards: 0, events_today: 0, active_alerts: 0, reports_generated: 0 });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rounded" height={140} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>Dashboard</Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Dashboards" value={stats?.dashboards || 0} icon={<Storage />} color="#6c63ff" trend="+12%" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Events Today" value={stats?.events_today || 0} icon={<Event />} color="#00d4aa" trend="+8%" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Alerts" value={stats?.active_alerts || 0} icon={<NotificationsActive />} color="#ff6b6b" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Reports" value={stats?.reports_generated || 0} icon={<TrendingUp />} color="#ffd93d" trend="+5%" />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Events Over Time</Typography>
              <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={eventsOverTime}>
                  <defs>
                    <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6c63ff" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6c63ff" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorProcessed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00d4aa" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#00d4aa" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="time" stroke="#a0a0b0" fontSize={12} />
                  <YAxis stroke="#a0a0b0" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid rgba(108,99,255,0.3)', borderRadius: 8 }} />
                  <Legend />
                  <Area type="monotone" dataKey="events" stroke="#6c63ff" fill="url(#colorEvents)" strokeWidth={2} />
                  <Area type="monotone" dataKey="processed" stroke="#00d4aa" fill="url(#colorProcessed)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Events by Type</Typography>
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie data={eventsByType} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                    {eventsByType.map((entry, index) => (
                      <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid rgba(108,99,255,0.3)', borderRadius: 8 }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
