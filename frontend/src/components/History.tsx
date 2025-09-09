import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  MenuItem,
} from '@mui/material';
import {
  Search as SearchIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface TranslationSession {
  id: string;
  timestamp: string;
  translation_type: 'body-to-text' | 'text-to-body';
  input_data: string;
  output_data: string;
  confidence: number;
  language: string;
  duration: number;
  status: 'completed' | 'failed' | 'processing';
}

const History: React.FC = () => {
  const [sessions, setSessions] = useState<TranslationSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedSession, setSelectedSession] = useState<TranslationSession | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/sessions');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
      // Mock data for demonstration
      setSessions([
        {
          id: '1',
          timestamp: '2024-01-15T10:30:00Z',
          translation_type: 'body-to-text',
          input_data: 'Video recording of hand gestures',
          output_data: 'Hello, how are you today?',
          confidence: 0.85,
          language: 'en',
          duration: 2.5,
          status: 'completed',
        },
        {
          id: '2',
          timestamp: '2024-01-15T09:15:00Z',
          translation_type: 'text-to-body',
          input_data: 'I need help urgently',
          output_data: 'Raise both hands above head, wave frantically',
          confidence: 0.92,
          language: 'en',
          duration: 1.8,
          status: 'completed',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filteredSessions = sessions.filter(session => {
    const inputData = session.input_data || '';
    const outputData = session.output_data || '';
    const searchLower = searchTerm.toLowerCase();
    
    const matchesSearch = inputData.toLowerCase().includes(searchLower) ||
                         outputData.toLowerCase().includes(searchLower);
    const matchesFilter = filterType === 'all' || session.translation_type === filterType;
    return matchesSearch && matchesFilter;
  });

  const paginatedSessions = filteredSessions.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const handleViewSession = (session: TranslationSession) => {
    setSelectedSession(session);
    setDialogOpen(true);
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setSessions(prev => prev.filter(s => s.id !== sessionId));
      }
    } catch (err) {
      setError('Failed to delete session');
    }
  };

  const handleDownloadSession = (session: TranslationSession) => {
    const dataStr = JSON.stringify(session, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `translation_session_${session.id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleShareSession = async (session: TranslationSession) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Translation Session',
          text: `Translation: ${session.output_data}`,
          url: window.location.href,
        });
      } catch (err) {
        console.error('Error sharing:', err);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(session.output_data);
    }
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        Translation History
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>      
            <Box sx={{ flex: '1 1 300px', minWidth: 0 }}>
              <TextField
                fullWidth
                placeholder="Search sessions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Box>
            <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
              <TextField
                select
                fullWidth
                label="Filter by type"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="body-to-text">Body → Text</MenuItem>
                <MenuItem value="text-to-body">Text → Body</MenuItem>
              </TextField>
            </Box>
            <Box sx={{ flex: '1 1 300px', minWidth: 0 }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  onClick={fetchSessions}
                  startIcon={<RefreshIcon />}
                >
                  Refresh
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setSearchTerm('');
                    setFilterType('all');
                  }}
                >
                  Clear Filters
                </Button>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date & Time</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Input</TableCell>
                      <TableCell>Output</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paginatedSessions.map((session) => (
                      <TableRow
                        key={session.id}
                        component={motion.tr}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <TableCell>
                          {new Date(session.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={session.translation_type === 'body-to-text' ? 'Body → Text' : 'Text → Body'}
                            color={session.translation_type === 'body-to-text' ? 'primary' : 'secondary'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {session.input_data || 'No input data'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {session.output_data || 'No output data'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${((session.confidence || 0) * 100).toFixed(1)}%`}
                            color={(session.confidence || 0) > 0.8 ? 'success' : (session.confidence || 0) > 0.6 ? 'warning' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={session.status}
                            color={session.status === 'completed' ? 'success' : session.status === 'failed' ? 'error' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                onClick={() => handleViewSession(session)}
                              >
                                <ViewIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Download">
                              <IconButton
                                size="small"
                                onClick={() => handleDownloadSession(session)}
                              >
                                <DownloadIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Share">
                              <IconButton
                                size="small"
                                onClick={() => handleShareSession(session)}
                              >
                                <ShareIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDeleteSession(session.id)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <TablePagination
                component="div"
                count={filteredSessions.length}
                page={page}
                onPageChange={(_, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => {
                  setRowsPerPage(parseInt(e.target.value, 10));
                  setPage(0);
                }}
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* Session Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Session Details
          <Typography variant="subtitle2" color="text.secondary">
            {selectedSession && new Date(selectedSession.timestamp).toLocaleString()}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedSession && (
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Box sx={{ flex: '1 1 300px', minWidth: 0 }}>
                <Typography variant="h6" gutterBottom>
                  Input Data
                </Typography>
                <Paper sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
                  <Typography variant="body2">
                    {selectedSession.input_data || 'No input data available'}
                  </Typography>
                </Paper>
              </Box>
              <Box sx={{ flex: '1 1 300px', minWidth: 0 }}>
                <Typography variant="h6" gutterBottom>
                  Output Data
                </Typography>
                <Paper sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
                  <Typography variant="body2">
                    {selectedSession.output_data || 'No output data available'}
                  </Typography>
                </Paper>
              </Box>
              <Box sx={{ width: '100%' }}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    label={`Type: ${selectedSession.translation_type}`}
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    label={`Language: ${selectedSession.language || 'Unknown'}`}
                    color="secondary"
                    variant="outlined"
                  />
                  <Chip
                    label={`Duration: ${selectedSession.duration || 0}s`}
                    color="info"
                    variant="outlined"
                  />
                  <Chip
                    label={`Confidence: ${((selectedSession.confidence || 0) * 100).toFixed(1)}%`}
                    color={(selectedSession.confidence || 0) > 0.8 ? 'success' : 'warning'}
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          {selectedSession && (
            <>
              <Button
                onClick={() => handleDownloadSession(selectedSession)}
                startIcon={<DownloadIcon />}
              >
                Download
              </Button>
              <Button
                onClick={() => handleShareSession(selectedSession)}
                startIcon={<ShareIcon />}
              >
                Share
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default History;
