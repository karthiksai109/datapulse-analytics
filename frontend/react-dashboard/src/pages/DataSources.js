import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Button, Grid, Chip, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem,
  Switch, FormControlLabel, Tooltip,
} from '@mui/material';
import { Add, Refresh, PowerSettingsNew, Speed } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import api from '../services/api';

const SOURCE_TYPES = [
  { value: 'api', label: 'REST API' },
  { value: 'webhook', label: 'Webhook' },
  { value: 'csv', label: 'CSV Upload' },
  { value: 'database', label: 'Database Connection' },
  { value: 'streaming', label: 'Streaming Source' },
];

const DataSources = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', source_type: 'api', connection_config: {} });
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => { fetchSources(); }, []);

  const fetchSources = async () => {
    try {
      const res = await api.get('/analytics/sources/');
      setSources(res.data.results || res.data || []);
    } catch (err) {
      console.error('Failed to fetch sources:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await api.post('/analytics/sources/', formData);
      enqueueSnackbar('Data source created', { variant: 'success' });
      setDialogOpen(false);
      setFormData({ name: '', source_type: 'api', connection_config: {} });
      fetchSources();
    } catch (err) {
      enqueueSnackbar('Failed to create source', { variant: 'error' });
    }
  };

  const handleToggle = async (id) => {
    try {
      await api.post(`/analytics/sources/${id}/toggle_active/`);
      enqueueSnackbar('Source status updated', { variant: 'success' });
      fetchSources();
    } catch (err) {
      enqueueSnackbar('Failed to toggle source', { variant: 'error' });
    }
  };

  const handleTestConnection = async (id) => {
    try {
      const res = await api.post(`/analytics/sources/${id}/test_connection/`);
      enqueueSnackbar(`Connection OK - Latency: ${res.data.latency_ms}ms`, { variant: 'success' });
    } catch (err) {
      enqueueSnackbar('Connection test failed', { variant: 'error' });
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Data Sources</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>
          Add Source
        </Button>
      </Box>

      <Grid container spacing={3}>
        {sources.map((source) => (
          <Grid item xs={12} sm={6} md={4} key={source.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">{source.name}</Typography>
                  <Chip
                    label={source.is_active ? 'Active' : 'Inactive'}
                    size="small"
                    color={source.is_active ? 'success' : 'default'}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Type: {SOURCE_TYPES.find(t => t.value === source.source_type)?.label || source.source_type}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Created: {new Date(source.created_at).toLocaleDateString()}
                </Typography>
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Tooltip title="Toggle Active">
                    <IconButton size="small" onClick={() => handleToggle(source.id)}>
                      <PowerSettingsNew color={source.is_active ? 'success' : 'disabled'} />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Test Connection">
                    <IconButton size="small" onClick={() => handleTestConnection(source.id)}>
                      <Speed />
                    </IconButton>
                  </Tooltip>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
        {!loading && sources.length === 0 && (
          <Grid item xs={12}>
            <Card><CardContent sx={{ textAlign: 'center', py: 6 }}>
              <Typography color="text.secondary">No data sources configured. Add one to get started.</Typography>
            </CardContent></Card>
          </Grid>
        )}
      </Grid>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Data Source</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} sx={{ mt: 1, mb: 2 }} />
          <TextField fullWidth select label="Source Type" value={formData.source_type} onChange={(e) => setFormData({ ...formData, source_type: e.target.value })} sx={{ mb: 2 }}>
            {SOURCE_TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate} disabled={!formData.name}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataSources;
