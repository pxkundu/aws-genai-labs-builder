/**
 * Backend Server - Secure API Proxy for AI Services
 * 
 * This server acts as a secure proxy between the mobile app and AI providers.
 * Benefits:
 * - API keys are never exposed to the client
 * - Rate limiting and caching
 * - Request logging and analytics
 * - Easy provider switching
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import OpenAI from 'openai';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Middleware
app.use(cors());
app.use(express.json());

// Rate limiting - 20 requests per minute per IP
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 20,
  message: { error: 'Too many requests, please try again later.' },
});
app.use('/api/', limiter);

// Simple in-memory cache
const cache = new Map<string, { response: string; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// System prompt for the todo assistant
const SYSTEM_PROMPT = `You are a helpful AI assistant for a todo/task management app. Your role is to:

1. Help users manage their tasks effectively
2. Parse natural language into structured tasks
3. Provide productivity tips and suggestions
4. Answer questions about task management

When users want to create a task, extract:
- title: The main task description
- dueDate: Any mentioned date/time (format: YYYY-MM-DD)
- priority: low, medium, or high based on urgency words

Always be concise and helpful.`;

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Chat endpoint
app.post('/api/chat', async (req: Request, res: Response) => {
  try {
    const { message, context } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Check cache
    const cacheKey = `${message}:${context || ''}`;
    const cached = cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      console.log('Cache hit for:', message.substring(0, 50));
      return res.json({
        message: cached.response,
        cached: true,
      });
    }

    // Build messages
    const messages: OpenAI.Chat.ChatCompletionMessageParam[] = [
      { role: 'system', content: SYSTEM_PROMPT },
    ];

    if (context) {
      messages.push({
        role: 'system',
        content: `Current user tasks:\n${context}`,
      });
    }

    messages.push({ role: 'user', content: message });

    // Call OpenAI
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4',
      messages,
      max_tokens: 500,
      temperature: 0.7,
    });

    const aiResponse = completion.choices[0].message.content || '';

    // Cache the response
    cache.set(cacheKey, {
      response: aiResponse,
      timestamp: Date.now(),
    });

    // Log for analytics (in production, use proper logging)
    console.log(`Chat request: "${message.substring(0, 50)}..." -> ${aiResponse.length} chars`);

    res.json({
      message: aiResponse,
      suggestions: extractSuggestions(aiResponse),
      parsedTask: extractTask(aiResponse),
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({
      error: 'Failed to process chat request',
      message: "I'm having trouble connecting. Please try again.",
    });
  }
});

// Parse task endpoint
app.post('/api/parse-task', async (req: Request, res: Response) => {
  try {
    const { text } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    const prompt = `Parse this into a task. Extract title, dueDate (YYYY-MM-DD format), and priority (low/medium/high).

Input: "${text}"

Respond ONLY with JSON: {"title": "...", "dueDate": "...", "priority": "..."}
If no date mentioned, omit dueDate. If no priority mentioned, use "medium".`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 200,
      temperature: 0.3,
    });

    const response = completion.choices[0].message.content || '';
    
    // Try to parse JSON
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      res.json(parsed);
    } else {
      res.json({ title: text, priority: 'medium' });
    }

  } catch (error) {
    console.error('Parse task error:', error);
    res.status(500).json({ error: 'Failed to parse task' });
  }
});

// Suggestions endpoint
app.post('/api/suggestions', async (req: Request, res: Response) => {
  try {
    const { todos } = req.body;

    if (!todos || !Array.isArray(todos)) {
      return res.status(400).json({ error: 'Todos array is required' });
    }

    const incompleteTasks = todos.filter((t: any) => !t.completed);
    
    if (incompleteTasks.length === 0) {
      return res.json({
        suggestions: ['Great job! All tasks completed. Add a new task to stay productive.'],
      });
    }

    const taskList = incompleteTasks.map((t: any) => `- ${t.title}`).join('\n');
    const prompt = `Based on these tasks, give 2-3 brief productivity suggestions (one line each):\n${taskList}`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 200,
      temperature: 0.7,
    });

    const response = completion.choices[0].message.content || '';
    
    res.json({
      suggestions: extractSuggestions(response),
    });

  } catch (error) {
    console.error('Suggestions error:', error);
    res.json({
      suggestions: ['Focus on your highest priority task first.'],
    });
  }
});

// Helper: Extract suggestions from text
function extractSuggestions(text: string): string[] {
  const lines = text.split('\n').filter(line => line.trim());
  const suggestions = lines
    .filter(line => line.match(/^[-•*\d.]/))
    .map(line => line.replace(/^[-•*\d.]\s*/, '').trim())
    .slice(0, 3);
  
  return suggestions.length > 0 ? suggestions : [];
}

// Helper: Extract task from response
function extractTask(text: string): { title?: string; dueDate?: string; priority?: string } | undefined {
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[0]);
      if (parsed.title) {
        return parsed;
      }
    } catch {
      // Not valid JSON
    }
  }
  return undefined;
}

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Todo AI Backend running on port ${PORT}`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Chat:   POST http://localhost:${PORT}/api/chat`);
});

export default app;
