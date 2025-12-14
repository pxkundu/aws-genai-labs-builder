# React Native Todo AI - Architecture Guide

## Overview

This document explains the architecture for integrating LLM/AI chat functionality into a React Native mobile application. The design prioritizes simplicity, security, and scalability.

## Architecture Options

### Option 1: Direct API Integration (Development/Prototyping)

Best for: Quick prototypes, learning, small apps

```mermaid
graph LR
    subgraph "Mobile App"
        UI[React Native UI]
        Service[AI Service]
    end
    
    subgraph "External"
        LLM[OpenAI API]
    end
    
    UI --> Service
    Service -->|HTTPS| LLM
    LLM -->|Response| Service
    Service --> UI
```

**Pros**: Simple, fast to implement
**Cons**: API key exposed in app bundle

---

### Option 2: Backend Proxy (Recommended for Production)

Best for: Production apps, secure API key management

```mermaid
graph LR
    subgraph "Mobile App"
        UI[React Native UI]
        API[API Client]
    end
    
    subgraph "Backend Server"
        Server[Express/FastAPI]
        AIService[AI Service]
    end
    
    subgraph "LLM Provider"
        LLM[OpenAI/Bedrock]
    end
    
    UI --> API
    API -->|HTTPS| Server
    Server --> AIService
    AIService -->|Secure| LLM
    LLM --> AIService
    AIService --> Server
    Server --> API
    API --> UI
```

**Pros**: Secure, rate limiting, caching, analytics
**Cons**: Additional infrastructure

---

### Option 3: Serverless Backend (Best Balance)

Best for: Cost-effective production apps

```mermaid
graph TB
    subgraph "Mobile App"
        RN[React Native]
    end
    
    subgraph "AWS Serverless"
        APIGW[API Gateway]
        Lambda[Lambda Function]
        Bedrock[Amazon Bedrock]
    end
    
    RN -->|HTTPS| APIGW
    APIGW --> Lambda
    Lambda --> Bedrock
    Bedrock --> Lambda
    Lambda --> APIGW
    APIGW --> RN
```

**Pros**: Pay-per-use, auto-scaling, secure
**Cons**: Cold starts, AWS dependency

---

## Recommended Architecture (Option 2 Detailed)

### Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        iOS[iOS App]
        Android[Android App]
    end
    
    subgraph "API Layer"
        LB[Load Balancer]
        API1[API Server 1]
        API2[API Server 2]
    end
    
    subgraph "Service Layer"
        Auth[Auth Service]
        Chat[Chat Service]
        Todo[Todo Service]
    end
    
    subgraph "Data Layer"
        Cache[(Redis Cache)]
        DB[(PostgreSQL)]
    end
    
    subgraph "AI Layer"
        OpenAI[OpenAI API]
        Bedrock[AWS Bedrock]
    end
    
    iOS --> LB
    Android --> LB
    LB --> API1
    LB --> API2
    
    API1 --> Auth
    API1 --> Chat
    API1 --> Todo
    API2 --> Auth
    API2 --> Chat
    API2 --> Todo
    
    Chat --> Cache
    Chat --> OpenAI
    Chat --> Bedrock
    
    Todo --> DB
    Auth --> DB
```

---

## Component Architecture

### React Native App Structure

```mermaid
graph TB
    subgraph "React Native App"
        App[App.tsx]
        
        subgraph "Screens"
            Home[HomeScreen]
            ChatScreen[ChatScreen]
        end
        
        subgraph "Components"
            TodoList[TodoList]
            TodoItem[TodoItem]
            ChatBot[ChatBot]
            MessageBubble[MessageBubble]
        end
        
        subgraph "Hooks"
            useAI[useAI]
            useTodos[useTodos]
            useChat[useChat]
        end
        
        subgraph "Services"
            AIService[aiService]
            StorageService[storageService]
            APIService[apiService]
        end
        
        subgraph "State"
            Context[AppContext]
            Reducer[todoReducer]
        end
    end
    
    App --> Home
    App --> ChatScreen
    
    Home --> TodoList
    TodoList --> TodoItem
    
    ChatScreen --> ChatBot
    ChatBot --> MessageBubble
    
    Home --> useTodos
    ChatScreen --> useAI
    ChatScreen --> useChat
    
    useAI --> AIService
    useTodos --> StorageService
    
    useTodos --> Context
    Context --> Reducer
```

---

## Data Flow

### Chat Message Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as React Native UI
    participant Hook as useAI Hook
    participant Service as AI Service
    participant Backend as Backend API
    participant LLM as OpenAI/Bedrock
    
    User->>UI: Type message
    UI->>Hook: sendMessage(text)
    Hook->>Hook: setLoading(true)
    Hook->>Service: chat(message)
    Service->>Backend: POST /api/chat
    Backend->>Backend: Validate & Rate Limit
    Backend->>LLM: API Request
    LLM-->>Backend: AI Response
    Backend-->>Service: JSON Response
    Service-->>Hook: Response text
    Hook->>Hook: setLoading(false)
    Hook-->>UI: Update messages
    UI-->>User: Display response
```

### Todo with AI Assistance Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Todo UI
    participant AI as AI Service
    participant Storage as Local Storage
    
    User->>UI: "Add task: buy groceries tomorrow"
    UI->>AI: parseTaskFromText(input)
    AI->>AI: Extract: title, date, priority
    AI-->>UI: { title: "Buy groceries", dueDate: "tomorrow" }
    UI->>Storage: saveTodo(parsedTask)
    Storage-->>UI: Saved
    UI-->>User: Show new task
```

---

## State Management

### App State Structure

```mermaid
graph TB
    subgraph AppState["App State"]
        subgraph TodosState["Todos State"]
            TodosList["todos: Todo[]"]
            Filter["filter: all/active/completed"]
        end
        
        subgraph ChatState["Chat State"]
            Messages["messages: Message[]"]
            Loading["isLoading: boolean"]
            Session["sessionId: string"]
        end
        
        subgraph UserState["User State"]
            UserInfo["user: User or null"]
            Settings["settings: Settings"]
        end
    end
```

### State Flow with Context

```mermaid
flowchart TD
    A[User Action] --> B{Action Type}
    B -->|ADD_TODO| C[todoReducer]
    B -->|SEND_MESSAGE| D[chatReducer]
    B -->|UPDATE_SETTINGS| E[settingsReducer]
    
    C --> F[Update todos state]
    D --> G[Update messages state]
    E --> H[Update settings state]
    
    F --> I[Re-render TodoList]
    G --> J[Re-render ChatBot]
    H --> K[Re-render Settings]
```

---

## API Design

### REST API Endpoints

```mermaid
graph LR
    subgraph "Chat Endpoints"
        POST_Chat[POST /api/chat]
        GET_History[GET /api/chat/history]
        DELETE_Session[DELETE /api/chat/session]
    end
    
    subgraph "Todo Endpoints"
        GET_Todos[GET /api/todos]
        POST_Todo[POST /api/todos]
        PUT_Todo[PUT /api/todos/:id]
        DELETE_Todo[DELETE /api/todos/:id]
    end
    
    subgraph "AI Endpoints"
        POST_Parse[POST /api/ai/parse-task]
        POST_Suggest[POST /api/ai/suggest]
    end
```

### Request/Response Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Handler
    participant AI
    
    Client->>API: POST /api/chat { message }
    API->>Auth: Validate JWT
    Auth-->>API: Valid
    API->>Handler: Process request
    Handler->>Handler: Rate limit check
    Handler->>AI: Generate response
    AI-->>Handler: AI response
    Handler->>Handler: Log & cache
    Handler-->>API: Response
    API-->>Client: { response, sessionId }
```

---

## Security Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant App
    participant Auth as Auth Service
    participant API
    participant LLM
    
    App->>Auth: Login (email/password)
    Auth-->>App: JWT Token
    App->>App: Store token securely
    
    App->>API: Request + JWT Header
    API->>API: Validate JWT
    API->>API: Check rate limits
    API->>LLM: Forward to AI
    LLM-->>API: Response
    API-->>App: AI Response
```

### Security Layers

```mermaid
graph TB
    subgraph "Client Security"
        SecureStore[Secure Token Storage]
        InputValidation[Input Validation]
        SSL[SSL Pinning]
    end
    
    subgraph "API Security"
        JWT[JWT Authentication]
        RateLimit[Rate Limiting]
        CORS[CORS Policy]
        Sanitize[Input Sanitization]
    end
    
    subgraph "Backend Security"
        EnvVars[Environment Variables]
        Encryption[Data Encryption]
        Logging[Audit Logging]
    end
    
    SecureStore --> JWT
    InputValidation --> Sanitize
    SSL --> CORS
    JWT --> EnvVars
    RateLimit --> Logging
```

---

## Caching Strategy

### Cache Architecture

```mermaid
graph TB
    subgraph "Client Cache"
        AsyncStorage[AsyncStorage]
        MemoryCache[In-Memory Cache]
    end
    
    subgraph "Server Cache"
        Redis[(Redis)]
    end
    
    subgraph "Cache Layers"
        L1[L1: Memory - 1min TTL]
        L2[L2: AsyncStorage - 1hr TTL]
        L3[L3: Redis - 24hr TTL]
    end
    
    Request --> L1
    L1 -->|Miss| L2
    L2 -->|Miss| L3
    L3 -->|Miss| API[API Call]
    
    API --> L3
    L3 --> L2
    L2 --> L1
```

---

## Error Handling

### Error Flow

```mermaid
flowchart TD
    A[API Request] --> B{Success?}
    B -->|Yes| C[Return Data]
    B -->|No| D{Error Type}
    
    D -->|Network| E[Show Offline Message]
    D -->|Auth| F[Redirect to Login]
    D -->|Rate Limit| G[Show Retry Timer]
    D -->|Server| H[Show Error + Retry]
    D -->|AI Error| I[Fallback Response]
    
    E --> J[Queue for Retry]
    G --> K[Exponential Backoff]
    I --> L[Use Cached Response]
```

---

## Build Process

### Step-by-Step Implementation

```mermaid
graph LR
    subgraph "Phase 1: Setup"
        A1[Create Expo Project]
        A2[Install Dependencies]
        A3[Configure Environment]
    end
    
    subgraph "Phase 2: Core Features"
        B1[Build Todo CRUD]
        B2[Add Local Storage]
        B3[Create UI Components]
    end
    
    subgraph "Phase 3: AI Integration"
        C1[Create AI Service]
        C2[Build Chat UI]
        C3[Connect to LLM]
    end
    
    subgraph "Phase 4: Polish"
        D1[Error Handling]
        D2[Loading States]
        D3[Testing]
    end
    
    A1 --> A2 --> A3
    A3 --> B1 --> B2 --> B3
    B3 --> C1 --> C2 --> C3
    C3 --> D1 --> D2 --> D3
```

### Implementation Timeline

| Phase | Tasks | Time |
|-------|-------|------|
| Phase 1 | Project setup, dependencies | 1-2 hours |
| Phase 2 | Todo functionality | 2-4 hours |
| Phase 3 | AI chat integration | 2-4 hours |
| Phase 4 | Polish & testing | 2-4 hours |
| **Total** | **Complete app** | **7-14 hours** |

---

## Deployment Architecture

### Production Deployment

```mermaid
graph TB
    subgraph "App Distribution"
        AppStore[App Store]
        PlayStore[Play Store]
        Expo[Expo Updates]
    end
    
    subgraph "Backend Infrastructure"
        CloudFront[CloudFront CDN]
        ALB[Load Balancer]
        ECS[ECS Containers]
        RDS[(RDS Database)]
        ElastiCache[(ElastiCache)]
    end
    
    subgraph "AI Services"
        OpenAI[OpenAI API]
        Bedrock[AWS Bedrock]
    end
    
    AppStore --> CloudFront
    PlayStore --> CloudFront
    CloudFront --> ALB
    ALB --> ECS
    ECS --> RDS
    ECS --> ElastiCache
    ECS --> OpenAI
    ECS --> Bedrock
```

---

## Summary

### Key Decisions

1. **Use backend proxy** for API key security
2. **Implement caching** to reduce API costs
3. **Add rate limiting** to prevent abuse
4. **Use TypeScript** for type safety
5. **Follow React Native best practices**

### Next Steps

1. Clone the project
2. Install dependencies
3. Configure your API key
4. Run the app
5. Customize for your needs

See the [README.md](./README.md) for detailed setup instructions.
