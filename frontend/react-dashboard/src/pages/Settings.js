import React, { useState } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, TextField, Button,
  Divider, Switch, FormControlLabel, Alert,
} from '@mui/material';
import { Save, Key, Person } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const Settings = () => {
  const { user, fetchProfile } = useAuth();
  const { enqueueSnackbar } = useSnackbar();
  const [profile, setProfile] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    bio: user?.bio || '',
    organization: user?.organization || '',
  });
  const [passwords, setPasswords] = useState({ old_password: '', new_password: '', confirm: '' });
  const [apiKey, setApiKey] = useState(user?.api_key || '');

  const handleProfileUpdate = async () => {
    try {
      await api.patch('/users/profile/', profile);
      await fetchProfile();
      enqueueSnackbar('Profile updated', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar('Failed to update profile', { variant: 'error' });
    }
  };

  const handlePasswordChange = async () => {
    if (passwords.new_password !== passwords.confirm) {
      enqueueSnackbar('Passwords do not match', { variant: 'error' });
      return;
    }
    try {
      await api.put('/users/change-password/', {
        old_password: passwords.old_password,
        new_password: passwords.new_password,
      });
      setPasswords({ old_password: '', new_password: '', confirm: '' });
      enqueueSnackbar('Password changed', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar(err.response?.data?.old_password?.[0] || 'Failed to change password', { variant: 'error' });
    }
  };

  const handleGenerateApiKey = async () => {
    try {
      const res = await api.post('/users/api-key/');
      setApiKey(res.data.api_key);
      enqueueSnackbar('API key generated', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar('Failed to generate API key', { variant: 'error' });
    }
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>Settings</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Person color="primary" />
                <Typography variant="h6">Profile</Typography>
              </Box>
              <TextField fullWidth label="First Name" value={profile.first_name} onChange={(e) => setProfile({ ...profile, first_name: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth label="Last Name" value={profile.last_name} onChange={(e) => setProfile({ ...profile, last_name: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth label="Email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth label="Organization" value={profile.organization} onChange={(e) => setProfile({ ...profile, organization: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth label="Bio" multiline rows={3} value={profile.bio} onChange={(e) => setProfile({ ...profile, bio: e.target.value })} sx={{ mb: 2 }} />
              <Button variant="contained" startIcon={<Save />} onClick={handleProfileUpdate}>Save Profile</Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Change Password</Typography>
              <TextField fullWidth type="password" label="Current Password" value={passwords.old_password} onChange={(e) => setPasswords({ ...passwords, old_password: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth type="password" label="New Password" value={passwords.new_password} onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth type="password" label="Confirm New Password" value={passwords.confirm} onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })} sx={{ mb: 2 }} />
              <Button variant="contained" onClick={handlePasswordChange} disabled={!passwords.old_password || !passwords.new_password}>Update Password</Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Key color="primary" />
                <Typography variant="h6">API Key</Typography>
              </Box>
              {apiKey && (
                <Alert severity="info" sx={{ mb: 2, wordBreak: 'break-all' }}>
                  {apiKey}
                </Alert>
              )}
              <Button variant="outlined" startIcon={<Key />} onClick={handleGenerateApiKey}>
                {apiKey ? 'Regenerate' : 'Generate'} API Key
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;
