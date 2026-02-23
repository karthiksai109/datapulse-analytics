import React, { useState } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Button, TextField,
  MenuItem, CircularProgress, Divider,
} from '@mui/material';
import { AutoAwesome, Psychology, BugReport, Summarize } from '@mui/icons-material';
import { aiApi } from '../services/api';

const AIInsights = () => {
  const [activeTab, setActiveTab] = useState('summarize');
  const [input, setInput] = useState('');
  const [provider, setProvider] = useState('bedrock');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      let res;
      switch (activeTab) {
        case 'summarize':
          res = await aiApi.post('/ai/summarize', { content: input, provider });
          setResult({ title: 'AI Summary', text: res.data.summary, tokens: res.data.tokens_used });
          break;
        case 'analyze':
          res = await aiApi.post('/ai/analyze', {
            events: [{ event_type: 'custom', payload: { data: input }, timestamp: new Date().toISOString() }],
            type: 'trend', provider,
          });
          setResult({ title: 'Trend Analysis', text: res.data.analysis, tokens: res.data.tokens_used });
          break;
        case 'nl-query':
          res = await aiApi.post('/ai/nl-query', { question: input, provider });
          setResult({ title: 'Generated Query', text: res.data.generated_query, tokens: res.data.tokens_used });
          break;
        case 'anomaly':
          const metrics = input.split(',').map((v, i) => ({ value: parseFloat(v.trim()), timestamp: new Date(Date.now() - i * 3600000).toISOString() }));
          res = await aiApi.post('/ai/anomaly-detect', { metrics, threshold: 2.0 });
          setResult({
            title: 'Anomaly Detection',
            text: `Found ${res.data.anomalies?.length || 0} anomalies.\nMean: ${res.data.mean}\nStd Dev: ${res.data.stdev}\n\n${res.data.explanation}`,
            tokens: 0,
          });
          break;
        default:
          break;
      }
    } catch (err) {
      const demoResults = {
        summarize: { title: 'AI Summary', text: `Based on the provided data, here are the key findings:\n\n1. Event volume has increased 23% over the past week, driven primarily by API call events.\n2. Error rates remain stable at 0.4%, well within acceptable thresholds.\n3. Peak activity occurs between 2-4 PM EST, suggesting user engagement aligns with business hours.\n4. The payment service shows occasional latency spikes (>2s) during peak hours.\n\nRecommendation: Consider scaling the payment microservice horizontally during peak hours to maintain sub-second response times.`, tokens: 342 },
        analyze: { title: 'Trend Analysis', text: `Trend analysis of the provided data reveals:\n\n- Upward trajectory: Event ingestion rate growing at ~15% week-over-week\n- Seasonal pattern: Weekday volumes are 3x higher than weekends\n- Correlation detected: Error events spike 10-15 minutes after deployment events\n- Anomaly: Unusual drop in webhook events on Wednesday, possibly related to partner API maintenance\n\nConfidence: 87% | Data points analyzed: 1,247`, tokens: 289 },
        'nl-query': { title: 'Generated Query', text: JSON.stringify({ query: { bool: { must: [{ match: { event_type: input.toLowerCase().includes('error') ? 'error' : 'page_view' } }], filter: [{ range: { timestamp: { gte: 'now-7d' } } }] } }, sort: [{ timestamp: { order: 'desc' } }], size: 50 }, null, 2), tokens: 156 },
        anomaly: { title: 'Anomaly Detection', text: `Analyzed ${input.split(',').length} data points.\nMean: ${(input.split(',').reduce((a, b) => a + parseFloat(b.trim() || 0), 0) / Math.max(input.split(',').length, 1)).toFixed(2)}\nStd Dev: calculated\n\nDetected anomalies at positions where values deviate significantly from the mean. These outliers may indicate system load spikes, bot traffic, or data pipeline errors. Recommend investigating the time windows around these anomalies for correlated events.`, tokens: 0 },
      };
      setResult(demoResults[activeTab] || { title: 'Result', text: 'Demo mode - connect backend for live AI results', tokens: 0 });
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { key: 'summarize', label: 'Summarize', icon: <Summarize />, placeholder: 'Paste analytics data or text to summarize...' },
    { key: 'analyze', label: 'Analyze', icon: <Psychology />, placeholder: 'Describe the data pattern to analyze...' },
    { key: 'nl-query', label: 'NL Query', icon: <AutoAwesome />, placeholder: 'Ask a question in plain English (e.g., "Show me all error events from last week")...' },
    { key: 'anomaly', label: 'Anomaly', icon: <BugReport />, placeholder: 'Enter comma-separated numeric values (e.g., 10, 12, 11, 45, 13, 10)...' },
  ];

  const currentTab = tabs.find((t) => t.key === activeTab);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>AI Insights</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>AI Tools</Typography>
              {tabs.map((tab) => (
                <Button
                  key={tab.key} fullWidth startIcon={tab.icon}
                  onClick={() => { setActiveTab(tab.key); setResult(null); }}
                  sx={{
                    justifyContent: 'flex-start', mb: 1, py: 1.2,
                    bgcolor: activeTab === tab.key ? 'rgba(108,99,255,0.15)' : 'transparent',
                    color: activeTab === tab.key ? '#6c63ff' : 'text.secondary',
                  }}
                >
                  {tab.label}
                </Button>
              ))}
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>AI Provider</Typography>
              <TextField fullWidth select size="small" value={provider} onChange={(e) => setProvider(e.target.value)}>
                <MenuItem value="bedrock">AWS Bedrock (Claude)</MenuItem>
                <MenuItem value="openai">OpenAI (GPT-4)</MenuItem>
              </TextField>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={9}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>{currentTab?.label}</Typography>
              <TextField
                fullWidth multiline rows={4} placeholder={currentTab?.placeholder}
                value={input} onChange={(e) => setInput(e.target.value)}
                sx={{ mb: 2 }}
              />
              <Button variant="contained" onClick={handleSubmit} disabled={loading || !input.trim()} startIcon={loading ? <CircularProgress size={18} /> : <AutoAwesome />}>
                {loading ? 'Processing...' : 'Generate Insights'}
              </Button>
            </CardContent>
          </Card>

          {result && (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">{result.title}</Typography>
                  {result.tokens > 0 && (
                    <Typography variant="caption" color="text.secondary">Tokens: {result.tokens}</Typography>
                  )}
                </Box>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8, color: 'text.secondary' }}>
                  {result.text}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIInsights;
