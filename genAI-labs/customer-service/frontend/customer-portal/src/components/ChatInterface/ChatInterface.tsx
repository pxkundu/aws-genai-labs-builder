import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  AttachFile as AttachFileIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    intent?: string;
    confidence?: number;
    escalation_needed?: boolean;
  };
}

interface ChatResponse {
  response: string;
  intent: string;
  confidence: number;
  escalation_needed: boolean;
  suggested_actions: string[];
  session_id: string;
  timestamp: string;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [customerId] = useState(() => `customer_${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message
  useEffect(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Hello! I\'m your AI assistant. How can I help you today?',
        timestamp: new Date(),
      },
    ]);
  }, []);

  const sendMessageMutation = useMutation(
    async (message: string) => {
      const response = await axios.post('/api/v1/chat', {
        message,
        customer_id: customerId,
        session_id: sessionId,
        channel: 'web',
      });
      return response.data as ChatResponse;
    },
    {
      onSuccess: (data) => {
        const assistantMessage: Message = {
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date(data.timestamp),
          metadata: {
            intent: data.intent,
            confidence: data.confidence,
            escalation_needed: data.escalation_needed,
          },
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
      },
      onError: (error) => {
        console.error('Error sending message:', error);
        setIsLoading(false);
      },
    }
  );

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    sendMessageMutation.mutate(inputMessage);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceRecording = () => {
    // Voice recording implementation would go here
    setIsRecording(!isRecording);
  };

  const handleFileUpload = () => {
    // File upload implementation would go here
  };

  const getIntentColor = (intent: string) => {
    switch (intent.toLowerCase()) {
      case 'technical support':
        return 'warning';
      case 'billing question':
        return 'info';
      case 'complaint':
        return 'error';
      case 'general inquiry':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Header */}
      <Paper elevation={1} sx={{ p: 2, borderRadius: 0 }}>
        <Box display="flex" alignItems="center" gap={2}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <BotIcon />
          </Avatar>
          <Box>
            <Typography variant="h6">AI Customer Support</Typography>
            <Typography variant="body2" color="textSecondary">
              Online • Ready to help
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Messages Area */}
      <Box
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          p: 2,
          backgroundColor: '#f8f9fa',
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 1,
                maxWidth: '70%',
                flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <Avatar
                sx={{
                  bgcolor: message.role === 'user' ? 'secondary.main' : 'primary.main',
                  width: 32,
                  height: 32,
                }}
              >
                {message.role === 'user' ? <PersonIcon /> : <BotIcon />}
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  backgroundColor: message.role === 'user' ? 'primary.main' : 'white',
                  color: message.role === 'user' ? 'white' : 'text.primary',
                  borderRadius: 2,
                }}
              >
                <Typography variant="body1">{message.content}</Typography>
                {message.metadata && (
                  <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {message.metadata.intent && (
                      <Chip
                        label={message.metadata.intent}
                        size="small"
                        color={getIntentColor(message.metadata.intent) as any}
                        variant="outlined"
                      />
                    )}
                    {message.metadata.confidence && (
                      <Chip
                        label={`${Math.round(message.metadata.confidence * 100)}% confidence`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                    {message.metadata.escalation_needed && (
                      <Chip
                        label="Escalation needed"
                        size="small"
                        color="error"
                        variant="outlined"
                      />
                    )}
                  </Box>
                )}
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 1,
                    opacity: 0.7,
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Paper>
            </Box>
          </Box>
        ))}
        
        {isLoading && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'flex-start',
              mb: 2,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                <BotIcon />
              </Avatar>
              <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
                <Box display="flex" alignItems="center" gap={1}>
                  <CircularProgress size={16} />
                  <Typography variant="body2">AI is thinking...</Typography>
                </Box>
              </Paper>
            </Box>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper elevation={2} sx={{ p: 2, borderRadius: 0 }}>
        <Box display="flex" alignItems="center" gap={1}>
          <IconButton onClick={handleFileUpload} color="primary">
            <AttachFileIcon />
          </IconButton>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            disabled={isLoading}
            variant="outlined"
            size="small"
          />
          <IconButton
            onClick={handleVoiceRecording}
            color={isRecording ? 'error' : 'primary'}
            disabled={isLoading}
          >
            {isRecording ? <MicOffIcon /> : <MicIcon />}
          </IconButton>
          <IconButton
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            color="primary"
          >
            <SendIcon />
          </IconButton>
        </Box>
        
        {/* Quick Actions */}
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            size="small"
            variant="outlined"
            onClick={() => setInputMessage('I need help with my account')}
            disabled={isLoading}
          >
            Account Help
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => setInputMessage('I have a billing question')}
            disabled={isLoading}
          >
            Billing
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => setInputMessage('Technical support needed')}
            disabled={isLoading}
          >
            Technical Support
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
