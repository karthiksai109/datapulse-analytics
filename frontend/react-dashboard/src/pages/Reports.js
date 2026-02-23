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
      console.error('Failed to fetch reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboards = async () => {
    try {
      const res = await api.get('/analytics/dashboards/');
      setDashboards(res.data.results || res.data || []);
    } catch (err) {
      console.error('Failed to fetch dashboards:', err);
    }
  };

  const handleGenerate = async () => {
    try {
      await api.post('/analytics/reports/', formData);
      enqueueSnackbar('Report generation queued', { variant: 'success' });
      setDialogOpen(false);
      setFormData({ title: '', dashboard: '', format: 'pdf' });
      fetchReports();
    } catch (err) {
      enqueueSnackbar('Failed to generate report', { variant: 'error' });
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
