/**
 * AI Service - LLM Integration
 * 
 * This service handles all AI/LLM interactions.
 * Supports multiple providers: OpenAI, AWS Bedrock, or Backend Proxy
 */

import { AIResponse, Todo } from '../types';

// Configuration
const CONFIG = {
  // Option 1: Direct OpenAI (for development/prototyping)
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
  
  // Option 2: Backend Proxy (recommended for production)
  API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:3001/api',
  
  // Default model
  MODEL: 'gpt-4',
};

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

Always be concise and helpful. If asked to create a task, respond with the task details in a structured way.`;

/**
 * Option 1: Direct OpenAI API Integration
 * Best for: Development, prototyping, small apps
 * Note: API key is exposed in app bundle - use backend proxy for production
 */
export async function chatWithOpenAI(message: string, context?: string): Promise<AIResponse> {
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${CONFIG.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: CONFIG.MODEL,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          ...(context ? [{ role: 'system', content: `Current tasks: ${context}` }] : []),
          { role: 'user', content: message },
        ],
        max_tokens: 500,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const aiMessage = data.choices[0].message.content;

    return {
      message: aiMessage,
      suggestions: extractSuggestions(aiMessage),
      parsedTask: extractTaskFromResponse(aiMessage),
    };
  } catch (error) {
    console.error('OpenAI API error:', error);
    throw error;
  }
}

/**
 * Option 2: Backend Proxy (Recommended for Production)
 * Best for: Production apps, secure API key management
 * The backend handles API key security, rate limiting, and caching
 */
export async function chatWithBackend(message: string, context?: string): Promise<AIResponse> {
  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Add auth token if needed
        // 'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        message,
        context,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Backend API error:', error);
    throw error;
  }
}

/**
 * Parse natural language into a task
 * Example: "Add task to buy groceries tomorrow" -> { title: "Buy groceries", dueDate: tomorrow }
 */
export async function parseTaskFromText(text: string): Promise<Partial<Todo> | null> {
  const prompt = `Parse this into a task. Extract title, dueDate (YYYY-MM-DD format), and priority (low/medium/high).
  
Input: "${text}"

Respond ONLY with JSON: {"title": "...", "dueDate": "...", "priority": "..."}
If no date mentioned, omit dueDate. If no priority mentioned, use "medium".`;

  try {
    const response = await chatWithOpenAI(prompt);
    
    // Try to parse JSON from response
    const jsonMatch = response.message.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        title: parsed.title,
        dueDate: parsed.dueDate ? new Date(parsed.dueDate) : undefined,
        priority: parsed.priority || 'medium',
      };
    }
    
    return null;
  } catch (error) {
    console.error('Parse task error:', error);
    return null;
  }
}

/**
 * Get AI suggestions based on current tasks
 */
export async function getSuggestions(todos: Todo[]): Promise<string[]> {
  const incompleteTasks = todos.filter(t => !t.completed);
  
  if (incompleteTasks.length === 0) {
    return ['Great job! All tasks completed. Add a new task to stay productive.'];
  }

  const taskList = incompleteTasks.map(t => `- ${t.title}`).join('\n');
  const prompt = `Based on these tasks, give 2-3 brief productivity suggestions (one line each):
${taskList}`;

  try {
    const response = await chatWithOpenAI(prompt);
    return extractSuggestions(response.message);
  } catch (error) {
    return ['Focus on your highest priority task first.'];
  }
}

/**
 * Main chat function - uses the configured provider
 */
export async function chat(message: string, context?: string): Promise<AIResponse> {
  // Use backend proxy if API_BASE_URL is configured, otherwise use direct OpenAI
  if (CONFIG.API_BASE_URL && !CONFIG.OPENAI_API_KEY) {
    return chatWithBackend(message, context);
  }
  return chatWithOpenAI(message, context);
}

// Helper: Extract suggestions from AI response
function extractSuggestions(text: string): string[] {
  const lines = text.split('\n').filter(line => line.trim());
  const suggestions = lines
    .filter(line => line.match(/^[-•*\d.]/))
    .map(line => line.replace(/^[-•*\d.]\s*/, '').trim())
    .slice(0, 3);
  
  return suggestions.length > 0 ? suggestions : [];
}

// Helper: Try to extract task from AI response
function extractTaskFromResponse(text: string): Partial<Todo> | undefined {
  // Look for JSON in response
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[0]);
      if (parsed.title) {
        return {
          title: parsed.title,
          dueDate: parsed.dueDate ? new Date(parsed.dueDate) : undefined,
          priority: parsed.priority,
        };
      }
    } catch {
      // Not valid JSON, ignore
    }
  }
  return undefined;
}

export default {
  chat,
  chatWithOpenAI,
  chatWithBackend,
  parseTaskFromText,
  getSuggestions,
};
