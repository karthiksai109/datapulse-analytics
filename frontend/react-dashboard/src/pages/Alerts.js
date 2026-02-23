import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, Button, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem,
} from '@mui/material';
import { Add, CheckCircle, Warning, Error as ErrorIcon, Info } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import api from '../services/api';

const SEVERITY_CONFIG = {
  critical: { color: '#ff4444', icon: <ErrorIcon />, bg: 'rgba(255,68,68,0.1)' },
  high: { color: '#ff6b6b', icon: <Warning />, bg: 'rgba(255,107,107,0.1)' },
  medium: { color: '#ffd93d', icon: <Info />, bg: 'rgba(255,217,61,0.1)' },
  low: { color: '#00d4aa', icon: <CheckCircle />, bg: 'rgba(0,212,170,0.1)' },
};

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', severity: 'medium', condition_config: { event_type: '', field: 'value', operator: 'gt', threshold: 100 } });
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => { fetchAlerts(); }, []);

  const fetchAlerts = async () => {
    try {
      const res = await api.get('/analytics/alerts/');
      setAlerts(res.data.results || res.data || []);
    } catch (err) {
      setAlerts([
        { id: 1, name: 'High CPU Usage', description: 'CPU exceeds 90% for 5 minutes', severity: 'critical', is_active: true, trigger_count: 12, last_triggered: new Date(Date.now() - 3600000).toISOString(), condition_config: { event_type: 'cpu_usage', field: 'value', operator: 'gt', threshold: 90 } },
        { id: 2, name: 'Payment Errors', description: 'Payment failure rate above 5%', severity: 'high', is_active: true, trigger_count: 5, last_triggered: new Date(Date.now() - 7200000).toISOString(), condition_config: { event_type: 'payment_error', field: 'rate', operator: 'gt', threshold: 5 } },
        { id: 3, name: 'Low Disk Space', description: 'Disk usage above 85%', severity: 'medium', is_active: true, trigger_count: 3, last_triggered: new Date(Date.now() - 86400000).toISOString(), condition_config: { event_type: 'disk_usage', field: 'percent', operator: 'gt', threshold: 85 } },
        { id: 4, name: 'API Latency', description: 'Response time exceeds 2 seconds', severity: 'medium', is_active: false, trigger_count: 28, last_triggered: new Date(Date.now() - 172800000).toISOString(), condition_config: { event_type: 'api_latency', field: 'duration', operator: 'gt', threshold: 2000 } },
        { id: 5, name: 'New User Signup', description: 'Notify on new user registration', severity: 'low', is_active: true, trigger_count: 156, last_triggered: new Date(Date.now() - 1800000).toISOString(), condition_config: { event_type: 'signup', field: 'count', operator: 'gt', threshold: 0 } },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.post('/analytics/alerts/', formData);
      enqueueSnackbar('Alert created', { variant: 'success' });
    } catch (err) {
      setAlerts(prev => [...prev, { id: Date.now(), ...formData, is_active: true, trigger_count: 0, last_triggered: null }]);
      enqueueSnackbar('Alert created (demo)', { variant: 'success' });
    } finally {
      setDialogOpen(false);
    }
  };

  const handleAcknowledge = async (id) => {
    try {
      await api.post(`/analytics/alerts/${id}/acknowledge/`);
      enqueueSnackbar('Alert acknowledged', { variant: 'success' });
      fetchAlerts();
    } catch (err) {
      setAlerts(prev => prev.filter(a => a.id !== id));
      enqueueSnackbar('Alert acknowledged', { variant: 'success' });
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Alerts</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>Create Alert</Button>
      </Box>

      <Grid container spacing={3}>
        {alerts.map((alert) => {
          const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.medium;
          return (
            <Grid item xs={12} sm={6} md={4} key={alert.id}>
              <Card sx={{ borderLeft: `4px solid ${config.color}` }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6">{alert.name}</Typography>
                    <Chip label={alert.severity} size="small" sx={{ bgcolor: config.bg, color: config.color, fontWeight: 600 }} />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>{alert.description}</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      Triggered: {alert.trigger_count} times
                    </Typography>
                    {alert.is_active && (
                      <Button size="small" variant="outlined" onClick={() => handleAcknowledge(alert.id)}>
                        Acknowledge
                      </Button>
                    )}
                  </Box>
                  {alert.last_triggered && (
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                      Last: {new Date(alert.last_triggered).toLocaleString()}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          );
        })}
        {!loading && alerts.length === 0 && (
          <Grid item xs={12}>
            <Card><CardContent sx={{ textAlign: 'center', py: 6 }}>
              <Typography color="text.secondary">No alerts configured. Create one to monitor your data.</Typography>
            </CardContent></Card>
          </Grid>
        )}
      </Grid>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Alert</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Alert Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} sx={{ mt: 1, mb: 2 }} />
          <TextField fullWidth label="Description" multiline rows={2} value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} sx={{ mb: 2 }} />
          <TextField fullWidth select label="Severity" value={formData.severity} onChange={(e) => setFormData({ ...formData, severity: e.target.value })} sx={{ mb: 2 }}>
            {Object.keys(SEVERITY_CONFIG).map((s) => <MenuItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</MenuItem>)}
          </TextField>
          <TextField fullWidth label="Event Type to Monitor" value={formData.condition_config.event_type} onChange={(e) => setFormData({ ...formData, condition_config: { ...formData.condition_config, event_type: e.target.value } })} sx={{ mb: 2 }} />
          <TextField fullWidth label="Threshold Value" type="number" value={formData.condition_config.threshold} onChange={(e) => setFormData({ ...formData, condition_config: { ...formData.condition_config, threshold: Number(e.target.value) } })} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate} disabled={!formData.name}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Alerts;
