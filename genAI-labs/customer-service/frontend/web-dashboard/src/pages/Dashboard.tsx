import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  Chat,
  People,
  ThumbUp,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Mock data - in real app, this would come from API
const conversationTrends = [
  { name: 'Mon', conversations: 120, resolved: 95 },
  { name: 'Tue', conversations: 150, resolved: 120 },
  { name: 'Wed', conversations: 180, resolved: 145 },
  { name: 'Thu', conversations: 160, resolved: 130 },
  { name: 'Fri', conversations: 200, resolved: 165 },
  { name: 'Sat', conversations: 90, resolved: 75 },
  { name: 'Sun', conversations: 80, resolved: 65 },
];

const sentimentData = [
  { name: 'Positive', value: 65, color: '#4caf50' },
  { name: 'Neutral', value: 25, color: '#ff9800' },
  { name: 'Negative', value: 10, color: '#f44336' },
];

const recentConversations = [
  {
    id: '1',
    customer: 'John Doe',
    message: 'I need help with my order',
    status: 'active',
    time: '2 min ago',
    sentiment: 'positive',
  },
  {
    id: '2',
    customer: 'Jane Smith',
    message: 'My account is locked',
    status: 'escalated',
    time: '5 min ago',
    sentiment: 'negative',
  },
  {
    id: '3',
    customer: 'Bob Johnson',
    message: 'Thank you for the quick response!',
    status: 'resolved',
    time: '10 min ago',
    sentiment: 'positive',
  },
];

const Dashboard: React.FC = () => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '#4caf50';
      case 'negative': return '#f44336';
      default: return '#ff9800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'success';
      case 'escalated': return 'error';
      default: return 'primary';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Chat />
                </Avatar>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Conversations
                  </Typography>
                  <Typography variant="h4">
                    1,234
                  </Typography>
                  <Box display="flex" alignItems="center" mt={1}>
                    <TrendingUp color="success" fontSize="small" />
                    <Typography variant="body2" color="success.main" sx={{ ml: 0.5 }}>
                      +12%
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <CheckCircle />
                </Avatar>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Resolved
                  </Typography>
                  <Typography variant="h4">
                    987
                  </Typography>
                  <Box display="flex" alignItems="center" mt={1}>
                    <TrendingUp color="success" fontSize="small" />
                    <Typography variant="body2" color="success.main" sx={{ ml: 0.5 }}>
                      +8%
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <Warning />
                </Avatar>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Escalated
                  </Typography>
                  <Typography variant="h4">
                    45
                  </Typography>
                  <Box display="flex" alignItems="center" mt={1}>
                    <TrendingUp color="error" fontSize="small" />
                    <Typography variant="body2" color="error.main" sx={{ ml: 0.5 }}>
                      -3%
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                  <ThumbUp />
                </Avatar>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Satisfaction
                  </Typography>
                  <Typography variant="h4">
                    4.2
                  </Typography>
                  <Box display="flex" alignItems="center" mt={1}>
                    <TrendingUp color="success" fontSize="small" />
                    <Typography variant="body2" color="success.main" sx={{ ml: 0.5 }}>
                      +0.3
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Conversation Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={conversationTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="conversations" stroke="#1976d2" strokeWidth={2} />
                  <Line type="monotone" dataKey="resolved" stroke="#4caf50" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Customer Sentiment
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <Box sx={{ mt: 2 }}>
                {sentimentData.map((item) => (
                  <Box key={item.name} display="flex" alignItems="center" mb={1}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        backgroundColor: item.color,
                        borderRadius: '50%',
                        mr: 1,
                      }}
                    />
                    <Typography variant="body2">
                      {item.name}: {item.value}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Conversations */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Conversations
              </Typography>
              <List>
                {recentConversations.map((conversation, index) => (
                  <React.Fragment key={conversation.id}>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: getSentimentColor(conversation.sentiment) }}>
                          {conversation.customer.charAt(0)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={conversation.customer}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {conversation.message}
                            </Typography>
                            <Box display="flex" alignItems="center" mt={1}>
                              <Chip
                                label={conversation.status}
                                size="small"
                                color={getStatusColor(conversation.status) as any}
                                sx={{ mr: 1 }}
                              />
                              <Typography variant="caption" color="textSecondary">
                                {conversation.time}
                              </Typography>
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentConversations.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Performance
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Response Accuracy</Typography>
                  <Typography variant="body2">92%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={92} />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Intent Recognition</Typography>
                  <Typography variant="body2">88%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={88} />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Customer Satisfaction</Typography>
                  <Typography variant="body2">85%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={85} />
              </Box>
              <Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Escalation Rate</Typography>
                  <Typography variant="body2">12%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={12} color="warning" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
