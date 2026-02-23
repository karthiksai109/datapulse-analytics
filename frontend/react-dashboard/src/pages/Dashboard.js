import React, { useState, useEffect } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Chip, Skeleton,
} from '@mui/material';
import { Storage, Event, NotificationsActive, TrendingUp } from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../services/api';

const COLORS = ['#e8913a', '#5b8def', '#34d399', '#f87171', '#fbbf24', '#a78bfa'];

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
              sx={{ mt: 1, bgcolor: 'rgba(52,211,153,0.1)', color: '#34d399', fontSize: '0.75rem' }}
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
    } catch (err) {
      setStats({ dashboards: 8, events_today: 12847, active_alerts: 3, reports_generated: 24 });
    } finally {
      setEventsOverTime([
        { time: 'Mon', events: 2400, processed: 2350 },
        { time: 'Tue', events: 1800, processed: 1760 },
        { time: 'Wed', events: 3200, processed: 3150 },
        { time: 'Thu', events: 2780, processed: 2720 },
        { time: 'Fri', events: 4100, processed: 4020 },
        { time: 'Sat', events: 1500, processed: 1470 },
        { time: 'Sun', events: 980, processed: 960 },
      ]);
      setEventsByType([
        { name: 'API Calls', value: 4200 },
        { name: 'User Actions', value: 2800 },
        { name: 'System Events', value: 1500 },
        { name: 'Webhooks', value: 900 },
        { name: 'Alerts', value: 350 },
      ]);
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
          <StatCard title="Dashboards" value={stats?.dashboards || 0} icon={<Storage />} color="#5b8def" trend="+12%" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Events Today" value={(stats?.events_today || 0).toLocaleString()} icon={<Event />} color="#e8913a" trend="+8%" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Alerts" value={stats?.active_alerts || 0} icon={<NotificationsActive />} color="#f87171" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Reports" value={stats?.reports_generated || 0} icon={<TrendingUp />} color="#34d399" trend="+5%" />
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
                      <stop offset="5%" stopColor="#e8913a" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#e8913a" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorProcessed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#5b8def" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#5b8def" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="time" stroke="#8892a4" fontSize={12} />
                  <YAxis stroke="#8892a4" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: '#1a2332', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8 }} />
                  <Legend />
                  <Area type="monotone" dataKey="events" stroke="#e8913a" fill="url(#colorEvents)" strokeWidth={2} />
                  <Area type="monotone" dataKey="processed" stroke="#5b8def" fill="url(#colorProcessed)" strokeWidth={2} />
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
                  <Tooltip contentStyle={{ backgroundColor: '#1a2332', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8 }} />
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
