import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import DataSources from './pages/DataSources';
import Events from './pages/Events';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';
import AIInsights from './pages/AIInsights';
import Settings from './pages/Settings';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6c63ff' },
    secondary: { main: '#00d4aa' },
    background: {
      default: '#0a0a1a',
      paper: '#12122a',
    },
    text: {
      primary: '#e0e0e0',
      secondary: '#a0a0b0',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 500 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(108, 99, 255, 0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 500 },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <AuthProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="sources" element={<DataSources />} />
                <Route path="events" element={<Events />} />
                <Route path="alerts" element={<Alerts />} />
                <Route path="reports" element={<Reports />} />
                <Route path="ai-insights" element={<AIInsights />} />
                <Route path="settings" element={<Settings />} />
              </Route>
            </Routes>
          </Router>
        </AuthProvider>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
