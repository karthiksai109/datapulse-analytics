import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Button, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import { Add, Download, PictureAsPdf, TableChart, Code } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import api from '../services/api';

const FORMAT_ICONS = { pdf: <PictureAsPdf />, csv: <TableChart />, json: <Code /> };

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [dashboards, setDashboards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ title: '', dashboard: '', format: 'pdf' });
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    fetchReports();
    fetchDashboards();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await api.get('/analytics/reports/');
      setReports(res.data.results || res.data || []);
    } catch (err) {
      setReports([
        { id: 1, title: 'Weekly Analytics Summary', format: 'pdf', status: 'completed', created_at: new Date(Date.now() - 86400000).toISOString(), dashboard_title: 'Sales Dashboard', ai_summary: 'Revenue increased 15% week-over-week. Mobile purchases up 22%. Recommend scaling payment service.' },
        { id: 2, title: 'Monthly Event Report', format: 'csv', status: 'completed', created_at: new Date(Date.now() - 172800000).toISOString(), dashboard_title: 'Operations Dashboard', ai_summary: 'Total events processed: 1.2M. Error rate: 0.3%. Top event type: page_view (45%).' },
        { id: 3, title: 'Q4 Performance Report', format: 'pdf', status: 'completed', created_at: new Date(Date.now() - 604800000).toISOString(), dashboard_title: 'Executive Dashboard', ai_summary: 'Platform uptime: 99.97%. Average API latency: 45ms. User growth: +18%.' },
        { id: 4, title: 'Alert Analysis Export', format: 'json', status: 'completed', created_at: new Date(Date.now() - 259200000).toISOString(), dashboard_title: 'Monitoring Dashboard', ai_summary: '23 alerts triggered this period. 3 critical (CPU spikes). All resolved within SLA.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboards = async () => {
    try {
      const res = await api.get('/analytics/dashboards/');
      setDashboards(res.data.results || res.data || []);
    } catch (err) {
      setDashboards([
        { id: 1, title: 'Sales Dashboard' },
        { id: 2, title: 'Operations Dashboard' },
        { id: 3, title: 'Executive Dashboard' },
        { id: 4, title: 'Monitoring Dashboard' },
      ]);
    }
  };

  const handleGenerate = async () => {
    try {
      await api.post('/analytics/reports/', formData);
      enqueueSnackbar('Report generation queued', { variant: 'success' });
    } catch (err) {
      setReports(prev => [...prev, { id: Date.now(), ...formData, status: 'completed', created_at: new Date().toISOString(), dashboard_title: formData.dashboard || 'Custom Report', ai_summary: 'Demo report generated successfully with sample analytics data.' }]);
      enqueueSnackbar('Report generated (demo)', { variant: 'success' });
    } finally {
      setDialogOpen(false);
      setFormData({ title: '', dashboard: '', format: 'pdf' });
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Reports</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>Generate Report</Button>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Dashboard</TableCell>
                <TableCell>Format</TableCell>
                <TableCell>AI Summary</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reports.map((report) => (
                <TableRow key={report.id} hover>
                  <TableCell><Typography fontWeight={500}>{report.title}</Typography></TableCell>
                  <TableCell>{report.dashboard}</TableCell>
                  <TableCell>
                    <Chip icon={FORMAT_ICONS[report.format]} label={report.format.toUpperCase()} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {report.ai_summary || 'Generating...'}
                  </TableCell>
                  <TableCell>{new Date(report.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    {report.file_url && (
                      <Button size="small" startIcon={<Download />} href={report.file_url} target="_blank">
                        Download
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {!loading && reports.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No reports generated yet.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Report</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Report Title" value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} sx={{ mt: 1, mb: 2 }} />
          <TextField fullWidth select label="Dashboard" value={formData.dashboard} onChange={(e) => setFormData({ ...formData, dashboard: e.target.value })} sx={{ mb: 2 }}>
            {dashboards.map((d) => <MenuItem key={d.id} value={d.id}>{d.title}</MenuItem>)}
          </TextField>
          <TextField fullWidth select label="Format" value={formData.format} onChange={(e) => setFormData({ ...formData, format: e.target.value })}>
            <MenuItem value="pdf">PDF</MenuItem>
            <MenuItem value="csv">CSV</MenuItem>
            <MenuItem value="json">JSON</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleGenerate} disabled={!formData.title || !formData.dashboard}>Generate</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Reports;
