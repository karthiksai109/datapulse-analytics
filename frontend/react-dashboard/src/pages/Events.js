import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, TextField, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  TablePagination, InputAdornment, CircularProgress,
} from '@mui/material';
import { Search, Refresh } from '@mui/icons-material';
import api from '../services/api';

const Events = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [total, setTotal] = useState(0);

  useEffect(() => { fetchEvents(); }, [page, rowsPerPage]);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const res = await api.get('/analytics/events/', {
        params: { page: page + 1, page_size: rowsPerPage },
      });
      setEvents(res.data.results || res.data || []);
      setTotal(res.data.count || 0);
    } catch (err) {
      const demoEvents = [
        { id: 1, event_type: 'page_view', source: 'Web App', timestamp: new Date().toISOString(), processed: true, payload: { page: '/dashboard', duration: 3.2, user_agent: 'Chrome/120' } },
        { id: 2, event_type: 'purchase', source: 'Mobile API', timestamp: new Date(Date.now() - 60000).toISOString(), processed: true, payload: { product_id: 'SKU-4521', amount: 49.99, currency: 'USD' } },
        { id: 3, event_type: 'error', source: 'Payment Service', timestamp: new Date(Date.now() - 120000).toISOString(), processed: false, payload: { error: 'timeout', service: 'stripe', retry: 2 } },
        { id: 4, event_type: 'signup', source: 'Web App', timestamp: new Date(Date.now() - 180000).toISOString(), processed: true, payload: { method: 'google_oauth', plan: 'pro' } },
        { id: 5, event_type: 'api_call', source: 'Partner API', timestamp: new Date(Date.now() - 240000).toISOString(), processed: true, payload: { endpoint: '/v2/analytics', method: 'GET', status: 200 } },
        { id: 6, event_type: 'alert_trigger', source: 'Monitoring', timestamp: new Date(Date.now() - 300000).toISOString(), processed: true, payload: { alert: 'High CPU', severity: 'warning', value: 87 } },
        { id: 7, event_type: 'data_sync', source: 'ETL Pipeline', timestamp: new Date(Date.now() - 360000).toISOString(), processed: true, payload: { records: 15420, source_db: 'postgres', duration_ms: 2340 } },
        { id: 8, event_type: 'page_view', source: 'Web App', timestamp: new Date(Date.now() - 420000).toISOString(), processed: true, payload: { page: '/reports', duration: 1.8 } },
        { id: 9, event_type: 'webhook', source: 'GitHub', timestamp: new Date(Date.now() - 480000).toISOString(), processed: true, payload: { action: 'push', repo: 'datapulse-analytics', branch: 'main' } },
        { id: 10, event_type: 'purchase', source: 'Mobile API', timestamp: new Date(Date.now() - 540000).toISOString(), processed: true, payload: { product_id: 'SKU-1102', amount: 129.00, currency: 'USD' } },
        { id: 11, event_type: 'error', source: 'Auth Service', timestamp: new Date(Date.now() - 600000).toISOString(), processed: false, payload: { error: 'invalid_token', user_id: 'usr_382' } },
        { id: 12, event_type: 'api_call', source: 'Internal', timestamp: new Date(Date.now() - 660000).toISOString(), processed: true, payload: { endpoint: '/health', method: 'GET', status: 200 } },
      ];
      setEvents(demoEvents);
      setTotal(demoEvents.length);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return fetchEvents();
    setLoading(true);
    try {
      const res = await api.get('/analytics/events/search/', { params: { q: searchQuery } });
      setEvents(res.data.results || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      fetchEvents();
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (type) => {
    const colors = { error: '#ff6b6b', warning: '#ffd93d', info: '#6c63ff', success: '#00d4aa' };
    return colors[type] || '#a0a0b0';
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>Analytics Events</Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            fullWidth placeholder="Search events by type, payload..."
            value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            size="small"
            InputProps={{
              startAdornment: <InputAdornment position="start"><Search /></InputAdornment>,
            }}
          />
          <Button variant="contained" onClick={handleSearch} sx={{ minWidth: 100 }}>Search</Button>
          <Button variant="outlined" onClick={fetchEvents} startIcon={<Refresh />}>Refresh</Button>
        </CardContent>
      </Card>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Event Type</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Payload Preview</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    <CircularProgress size={32} />
                  </TableCell>
                </TableRow>
              ) : events.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No events found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                events.map((event) => (
                  <TableRow key={event.id} hover>
                    <TableCell>
                      <Chip label={event.event_type} size="small" sx={{ bgcolor: 'rgba(232,145,58,0.12)', color: '#e8913a' }} />
                    </TableCell>
                    <TableCell>{event.source || 'N/A'}</TableCell>
                    <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={event.processed ? 'Processed' : 'Pending'}
                        size="small"
                        color={event.processed ? 'success' : 'warning'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {JSON.stringify(event.payload).substring(0, 80)}...
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div" count={total} page={page} rowsPerPage={rowsPerPage}
          onPageChange={(e, p) => setPage(p)}
          onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
          rowsPerPageOptions={[10, 20, 50]}
        />
      </Card>
    </Box>
  );
};

export default Events;
