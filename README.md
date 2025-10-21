# The Munger RAG Agent

A RAG (Retrieval-Augmented Generation) agent that answers questions in the style and wisdom of Charlie Munger.

## 🎯 Overview

The Munger RAG Agent is a specialized AI assistant that combines retrieval-augmented generation (RAG) with Charlie Munger's distinctive thinking patterns and communication style. Drawing from Munger's vast knowledge across multiple disciplines, this agent provides insights using his characteristic mental models, analogies, and practical wisdom.

## ✨ Features

- **Charlie Munger's Thinking Style**: Answers questions using Munger's mental models and multidisciplinary approach
- **RAG-Powered Knowledge**: Retrieval-augmented generation from Munger's talks, writings, and wisdom
- **Mental Models Integration**: Applies psychology, economics, business, and investing principles
- **AI Integration**: OpenAI GPT-4 Turbo for advanced language processing
- **Modern Tech Stack**: FastAPI backend, React frontend with TypeScript
- **Vector Storage**: FAISS vector database for efficient knowledge retrieval
- **AI Frameworks**: LangChain, LangGraph, DSPy for multi-agent orchestration

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/the-munger-talks
   cd the-munger-talks
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Start the services**

   ```bash
   # Backend (FastAPI)
   python start_backend.py

   # Frontend (React + Vite) - in a new terminal
   ./start_frontend.sh
   ```

## 🏗️ Project Structure

```
the-munger-talks/
├── backend/                           # Python backend
│   ├── agent/                         # Multi-agent system
│   │   ├── dspy_modules/              # DSPy integration modules
│   │   │   ├── dspy_config.py        # DSPy configuration & LLM adapter
│   │   │   └── simple_modules.py      # DSPy planners, synthesizers, verifiers
│   │   ├── graph/                     # LangGraph workflow orchestration
│   │   │   ├── memory.py              # Conversation memory management
│   │   │   ├── nodes/                 # Specialized agent nodes
│   │   │   │   ├── mental_model_analyzer.py  # Mental model detection & analysis
│   │   │   │   ├── planner.py         # Query planning & strategy determination
│   │   │   │   ├── retriever.py       # Document retrieval & reranking
│   │   │   │   ├── synthesizer.py     # Munger-style response generation
│   │   │   │   └── verifier.py        # Response quality validation
│   │   │   ├── state.py               # Comprehensive state management
│   │   │   └── workflow.py            # LangGraph workflow definitions
│   │   └── llm/                       # LLM client & configuration
│   │       ├── client.py              # OpenAI client wrapper
│   │       └── settings.py            # Model configuration
│   ├── app/                           # FastAPI application
│   │   ├── config/                    # Application configuration
│   │   │   └── config.py              # Settings & environment config
│   │   ├── dependencies.py            # Dependency injection & managers
│   │   ├── routes.py                  # API endpoints
│   │   └── schemas.py                 # Pydantic data models
│   ├── indexing_and_retrieval/        # Document processing pipeline
│   │   ├── indexing.py                # Document ingestion & chunking
│   │   ├── retrieval/                 # Retrieval system
│   │   │   ├── retrieval.py           # FAISS vector search
│   │   │   ├── rerank.py              # Cross-encoder reranking
│   │   │   └── storage.py             # Vector database management
│   │   ├── storage/                   # Data persistence
│   │   │   ├── chunks.json            # Processed document chunks
│   │   │   ├── conversation_memory/    # Session memory storage
│   │   │   └── faiss_db/              # FAISS vector database
│   │   └── kg/                        # Knowledge graph (future)
│   ├── tests/                         # Test suites
│   │   ├── unit/                      # Unit tests
│   │   ├── integration/               # Integration tests
│   │   └── golden/                    # Golden test cases
│   └── main.py                        # Application entry point
├── frontend/                          # React frontend
│   ├── src/
│   │   ├── components/                # React components
│   │   │   ├── ChatInterface.tsx      # Main chat interface
│   │   │   ├── ChatMessage.tsx        # Individual message component
│   │   │   └── ThinkingIndicator.tsx  # Loading state indicator
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── pages/                     # Page components
│   │   ├── types/                     # TypeScript type definitions
│   │   │   └── chat.ts                # Chat-related types
│   │   ├── utils/                     # Frontend utilities
│   │   │   └── api.ts                 # API client functions
│   │   ├── App.tsx                    # Main app component
│   │   └── main.tsx                   # Application entry point
│   ├── public/                        # Static assets
│   │   ├── Charlie_Munger.jpg         # Charlie Munger portrait
│   │   └── charlie-munger-avatar.svg  # Avatar icon
│   ├── package.json                   # Node.js dependencies
│   ├── vite.config.ts                 # Vite build configuration
│   └── tsconfig.json                  # TypeScript configuration
├── docs/                              # Documentation & source material
│   └── PoorCharliesAlmanack_book.pdf  # Primary knowledge source
├── pyproject.toml                     # Python project configuration
├── requirements.txt                    # Python dependencies
├── Makefile                           # Build automation
├── start_backend.py                   # Backend startup script
└── start_frontend.sh                  # Frontend startup script
```

## 🛠️ Technology Stack

### Backend

- **FastAPI**: Modern, fast web framework
- **LangChain**: AI application framework
- **LangGraph**: Multi-agent workflow orchestration
- **FAISS**: Vector database for semantic search
- **OpenAI**: GPT-4 Turbo for language processing
- **DSPy**: Programming with language models
- **HuggingFace**: Cross-encoder models for reranking

### Frontend

- **React**: User interface library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Chakra UI**: Component library

## 🧠 Backend Agent Architecture

The Munger RAG Agent backend is built on a sophisticated multi-agent architecture that combines retrieval-augmented generation with Charlie Munger's distinctive thinking patterns. Here's how it works:

### LLM Integration

- **Primary Model**: GPT-4 Turbo (configurable via `backend/agent/llm/settings.py`)
- **Client**: Custom `LLMClient` wrapper around OpenAI API
- **Configuration**: Temperature, max tokens, and model selection via environment variables
- **Streaming Support**: Real-time response streaming for web interface

### Document Ingestion & Chunking Pipeline

The system processes Charlie Munger's knowledge through a multi-stage pipeline:

1. **Document Loading**: PDF documents loaded using `PyPDFLoader` from LangChain
2. **Text Extraction**: Full text extracted and combined from all pages
3. **Intelligent Chunking**:
   - Uses `RecursiveCharacterTextSplitter` with 4000 token chunks
   - 200 token overlap for context preservation
   - Smart separators: `["\nChapter ", "\n\n", "\n", " ", ""]`
4. **Metadata Enrichment**: Each chunk tagged with source type, document ID, and token count
5. **Storage**: Chunks stored in JSON format for persistence and FAISS vector database

### Retrieval & Reranking System

The retrieval system uses a sophisticated two-stage approach:

1. **Initial Retrieval**:

   - FAISS vector search using `sentence-transformers/all-MiniLM-L6-v2` embeddings
   - Strategy-aware retrieval counts (10-18 documents based on query type)
   - Source preference filtering (speeches, interviews, books, essays)

2. **Reranking**:
   - Cross-encoder reranking using `cross-encoder/ms-marco-MiniLM-L-6-v2`
   - Query-document relevance scoring
   - Top-K selection based on query complexity
   - Metadata extraction for quality assessment

### DSPy Integration

The system leverages DSPy for advanced language model programming:

- **DSPy Planner**: Analyzes queries and determines optimal strategies
- **DSPy Synthesizer**: Generates context-aware responses in Munger's voice
- **DSPy Verifier**: Validates response quality and factual accuracy
- **DSPy Retrieval Decider**: Determines when retrieval is necessary
- **Fallback System**: Graceful degradation to rule-based approaches when DSPy unavailable

### LangGraph Workflow

The agent uses LangGraph to orchestrate a sophisticated workflow with multiple specialized nodes:

#### Workflow Types

1. **Conversational Workflow**: Maintains memory and context across interactions
2. **Standard Workflow**: Single-query processing without memory
3. **Simple Workflow**: Minimal nodes for testing and development

#### Core Nodes

- **Memory Context Node**: Manages conversation history and context
- **Planner Node**: Analyzes queries and determines retrieval strategy
- **Retriever Node**: Coordinates document retrieval and reranking
- **Mental Model Analyzer**: Identifies and explains relevant mental models
- **Synthesizer Node**: Generates Munger-style responses
- **Verifier Node**: Validates response quality and determines retry logic
- **Memory Update Node**: Updates conversation memory

#### Conditional Logic

- **Retrieval Decision**: Determines if document retrieval is needed
- **Mental Model Analysis**: Decides when to analyze mental models
- **Retry Logic**: Handles failures and retry attempts
- **Conversation Flow**: Manages multi-turn conversations

### Specialized Agents

#### Planning Agent (`QueryPlanner`)

- **Query Classification**: Identifies query types (quote, explanation, mental_model, story, decision_framework)
- **Complexity Analysis**: Assesses query complexity (simple, moderate, complex)
- **Mental Model Detection**: Identifies relevant mental models using keyword matching
- **Strategy Determination**: Creates retrieval strategies based on query analysis
- **DSPy Enhancement**: Uses DSPy for advanced query understanding when available

#### Retrieval Agent (`EnhancedRetriever`)

- **Strategy-Aware Retrieval**: Adapts retrieval parameters based on query type
- **Multi-Stage Processing**: Initial retrieval → Reranking → Source filtering
- **Metadata Extraction**: Tracks retrieval performance and document statistics
- **Context Sufficiency**: Validates retrieved context adequacy
- **Caching**: Implements retrieval caching for repeated queries

#### Mental Model Analyzer (`MentalModelAnalyzer`)

- **Model Identification**: Detects applicable mental models from retrieved content
- **Explanation Generation**: Provides clear explanations of mental models
- **Application Notes**: Generates guidance on how to apply models
- **Integration**: Seamlessly integrates with synthesizer for response generation

#### Synthesizer Agent (`MungerSynthesizer`)

- **Style Guidelines**: Enforces Munger's communication characteristics:
  - Directness and straightforwardness
  - Practical wisdom focus
  - Clear analogies and examples
  - Intellectual humility
  - Multidisciplinary connections
  - Simple explanations of complex ideas
  - Brutal honesty about limitations
- **Context Integration**: Combines retrieved documents with mental models
- **DSPy Enhancement**: Uses DSPy for context-aware response generation
- **Quality Metrics**: Tracks response confidence and style consistency

#### Verifier Agent (`ResponseVerifier`)

- **Multi-Criteria Evaluation**: Assesses responses across multiple dimensions:
  - Factual accuracy (30% weight)
  - Style consistency (25% weight)
  - Completeness (20% weight)
  - Practical value (15% weight)
  - Mental model application (10% weight)
- **LLM-Based Validation**: Uses GPT-4 for sophisticated quality assessment
- **Retry Logic**: Determines when responses need regeneration
- **Quality Scoring**: Provides quantitative quality metrics

### State Management

The system uses a comprehensive `MungerState` TypedDict that tracks:

- **Input & Context**: User queries, conversation history, session management
- **Planning & Analysis**: Query types, complexity, mental models, intent
- **Retrieval Pipeline**: Documents, metadata, strategies, decisions
- **Mental Model Analysis**: Applicable models, explanations, application notes
- **Response Generation**: Generated content, confidence, sources, citations
- **Control Flow**: Current step, retry counts, error handling
- **Munger-Specific Features**: Style requirements, voice activation, analogies
- **Quality Metrics**: Response quality, factual accuracy, style consistency
- **Debugging**: Execution traces, performance metrics, debug information

This architecture enables the system to provide authentic, high-quality responses that capture Charlie Munger's distinctive thinking patterns while maintaining robust error handling and quality assurance throughout the process.

### Architecture Flow Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query   │───▶│  Memory Context │───▶│   Planner      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Verifier      │◀───│   Synthesizer   │◀───│   Retriever     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       │                       ▼
┌─────────────────┐              │              ┌─────────────────┐
│ Memory Update   │              │              │ Mental Model    │
└─────────────────┘              │              │ Analyzer        │
         │                       │              └─────────────────┘
         ▼                       │                       │
┌─────────────────┐              │                       │
│   END/CONTINUE  │              │                       │
└─────────────────┘              │                       │
                                  │                       │
                                  ▼                       │
                        ┌─────────────────┐              │
                        │   DSPy Modules  │              │
                        │  - Planner      │              │
                        │  - Synthesizer  │              │
                        │  - Verifier     │              │
                        │  - Retrieval    │              │
                        └─────────────────┘              │
                                                          │
                                  ┌───────────────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │   FAISS Vector  │
                        │   Database      │
                        │                 │
                        │  - Embeddings   │
                        │  - Chunks       │
                        │  - Metadata     │
                        └─────────────────┘
```

### Data Flow

1. **Input Processing**: User query → Memory context analysis → Query planning
2. **Retrieval Pipeline**: Strategy determination → Document retrieval → Reranking → Mental model analysis
3. **Response Generation**: Context synthesis → Munger-style response generation → Quality verification
4. **Output & Memory**: Response validation → Memory update → End or continue conversation
5. **DSPy Enhancement**: All major nodes enhanced with DSPy modules for advanced reasoning
6. **Vector Storage**: FAISS database provides semantic search and retrieval capabilities

## 📚 API Documentation

Once the backend is running, visit:

- **FastAPI docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Streamlit**: http://localhost:8501

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test categories
pytest -m unit
pytest -m integration
```

## 📝 Environment Variables

Create a `.env` file with:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_key_here

# Optional HuggingFace (for cross-encoder reranking)
HUGGINGFACE_API_TOKEN=your_hf_token_here

# Development Settings
DEBUG=true
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## 🙏 Acknowledgments

Inspired by Charlie Munger's multidisciplinary approach to learning and problem-solving.

---

**"The best thing a human being can do is to help another human being know more."** - Charlie Munger
