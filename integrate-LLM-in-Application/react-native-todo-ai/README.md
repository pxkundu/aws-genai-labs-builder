# 📱 React Native Todo App with AI Chat

> **A simple Todo app with integrated LLM chat assistant - Learn how to add AI to your mobile apps**

[![React Native](https://img.shields.io/badge/React%20Native-0.73-blue?logo=react)](https://reactnative.dev/)
[![Expo](https://img.shields.io/badge/Expo-SDK%2050-black?logo=expo)](https://expo.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green)](https://openai.com/)

## 🎯 What You'll Learn

This project demonstrates the **simplest way to integrate LLM/AI chat** into a React Native mobile application:

1. ✅ Basic Todo CRUD operations
2. 💬 AI chat assistant for task help
3. 🤖 Natural language task creation
4. 📱 Clean, production-ready code structure

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Expo CLI (`npm install -g expo-cli`)
- OpenAI API key (or AWS Bedrock access)

### Installation

```bash
# Navigate to project
cd integrate-LLM-in-Application/react-native-todo-ai

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API key

# Start the app
npx expo start
```

### Run on Device
- **iOS Simulator**: Press `i`
- **Android Emulator**: Press `a`
- **Physical Device**: Scan QR code with Expo Go app

## 📁 Project Structure

```
react-native-todo-ai/
├── App.tsx                 # Main app entry
├── src/
│   ├── components/         # UI components
│   │   ├── TodoList.tsx
│   │   ├── TodoItem.tsx
│   │   ├── AddTodo.tsx
│   │   └── ChatBot.tsx
│   ├── services/           # API services
│   │   └── aiService.ts    # LLM integration
│   ├── hooks/              # Custom hooks
│   │   └── useAI.ts
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   └── utils/              # Utilities
│       └── storage.ts
├── backend/                # Optional backend
│   └── server.ts
├── architecture.md         # Solution architecture
├── package.json
└── .env.example
```

## 🤖 AI Features

### 1. Chat with AI Assistant
Ask the AI for help with your tasks:
- "What should I prioritize today?"
- "Help me break down this project"
- "Remind me about my deadlines"

### 2. Natural Language Task Creation
Create tasks by talking naturally:
- "Add a task to buy groceries tomorrow"
- "Create a reminder to call mom at 5pm"
- "I need to finish the report by Friday"

### 3. Smart Suggestions
AI provides contextual suggestions based on your tasks.

## 🔧 LLM Integration Options

### Option 1: Direct OpenAI API (Simplest)
```typescript
// src/services/aiService.ts
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function chat(message: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: message }]
  });
  return response.choices[0].message.content;
}
```

### Option 2: Backend Proxy (Recommended for Production)
```typescript
// Keeps API key secure on server
const response = await fetch('https://your-api.com/chat', {
  method: 'POST',
  body: JSON.stringify({ message })
});
```

### Option 3: AWS Bedrock
```typescript
// For AWS-based applications
import { BedrockRuntime } from '@aws-sdk/client-bedrock-runtime';
```

## 📊 Architecture

See [architecture.md](./architecture.md) for detailed diagrams and explanations.

```
┌─────────────────────────────────────────────────┐
│              React Native App                    │
│  ┌─────────────┐  ┌─────────────┐               │
│  │  Todo List  │  │  AI Chat    │               │
│  └──────┬──────┘  └──────┬──────┘               │
│         │                │                       │
│         └────────┬───────┘                       │
│                  │                               │
│         ┌───────▼────────┐                       │
│         │   AI Service   │                       │
│         └───────┬────────┘                       │
└─────────────────┼───────────────────────────────┘
                  │
         ┌───────▼────────┐
         │  LLM Provider  │
         │ (OpenAI/Bedrock)│
         └────────────────┘
```

## 🛠️ Key Code Examples

### AI Service Hook
```typescript
// src/hooks/useAI.ts
export function useAI() {
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async (message: string) => {
    setLoading(true);
    try {
      const response = await aiService.chat(message);
      return response;
    } finally {
      setLoading(false);
    }
  };
  
  return { sendMessage, loading };
}
```

### Chat Component
```typescript
// Usage in component
const { sendMessage, loading } = useAI();

const handleSend = async () => {
  const response = await sendMessage(userMessage);
  setMessages([...messages, { role: 'assistant', content: response }]);
};
```

## 📱 Screenshots

| Todo List | AI Chat | Task Creation |
|-----------|---------|---------------|
| Manage tasks | Chat with AI | Natural language input |

## 🔒 Security Best Practices

1. **Never expose API keys in client code**
   - Use environment variables
   - Prefer backend proxy for production

2. **Rate limiting**
   - Implement request throttling
   - Cache common responses

3. **Input validation**
   - Sanitize user inputs
   - Limit message length

## 📈 Performance Tips

- Cache AI responses for common queries
- Use streaming for long responses
- Implement optimistic UI updates
- Debounce user input

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## 📚 Learn More

- [React Native Docs](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [AWS Bedrock Guide](https://docs.aws.amazon.com/bedrock/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**Ready to add AI to your mobile app? Let's go! 🚀**
