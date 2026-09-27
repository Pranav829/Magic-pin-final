# Vera Bot - Codebase Architecture & Overview

Welcome to the `finalbotmagicpin` project! This document provides a comprehensive overview of the **Vera Bot** repository built for the magicpin AI Challenge. It explains the project's structure, its core functional components, how they interact, and how the system maintains context to engage merchants intelligently.

---

## 1. High-Level Architecture

The Vera Bot is an AI-powered conversational agent designed to send proactive, context-aware messages to merchants and handle intelligent multi-turn replies. 

It exposes a **FastAPI** interface that strictly adheres to the judge simulation harness API. Below the API layer, it maintains an **In-Memory State** of the external world (Merchant Profiles, Category Rules, Customer Data, and Triggers) and uses an **LLM-powered Composer** to format personalized, high-converting messages.

### Core Workflows
1. **Context Ingestion (`/v1/context`)**: The system stores continuously updated context profiles in a thread-safe store.
2. **Proactive Outreach (`/v1/tick`)**: When requested, the bot analyzes available \"triggers\" (e.g., Low Stock, Customer Review) and generates personalized, targeted messages.
3. **Reactive Responses (`/v1/reply`)**: Handles multi-turn conversations when merchants or customers reply, keeping track of conversation history and intents (like opting out).

---

## 2. Directory Structure

```text
finalbotmagicpin/
├── bot/
│   ├── __init__.py
│   ├── bot.py                  # Main FastAPI Application & Endpoints
│   ├── composer.py             # LLM Prompt Generation, Inference & Fallbacks
│   ├── context_store.py        # Thread-safe in-memory Context storage (4-context model)
│   ├── conversation_tracker.py # Thread-safe State management for Multi-turn Conversations
│   ├── index.py                # Serverless entry point (e.g., for Vercel)
│   ├── requirements.txt        # Python Dependencies
│   └── test_e2e.py             # End-to-End Testing Suite
├── dataset/                    # Sample data (categories, merchants, triggers, etc.)
├── examples/                   # Example scenarios and interactions
├── .env.example                # Environment variables template
├── judge_simulator.py          # Local simulation script mirroring the competition judge
├── requirements.txt            # Main project dependencies
├── run_local.py                # Script to run bot + test simulation locally
└── ... (markdown docs)         # Internal READMEs, Challenge Briefs, etc.
```

---

## 3. Core Functional Components

### A. The Server Layer (`bot/bot.py`)
This is the entry point for incoming HTTP requests. It uses FastAPI to expose three critical endpoints required by the challenge:
- **`POST /v1/context`**: Receives asynchronous pushes of metadata. It delegates the data to `context_store.py`.
- **`POST /v1/tick`**: Receives a simulation \"tick\" (time update) along with a list of available triggers. It looks up the associated context, asks `composer.py` to generate a proactive message, and initiates tracking via `conversation_tracker.py`.
- **`POST /v1/reply`**: Takes incoming messages from merchants or customers, appends them to the conversation history, and invokes the `composer` to generate an AI reply. It handles suppression rules automatically.

### B. The Context Store (`bot/context_store.py`)
Because the bot needs to generate deeply personalized messages, it cannot rely solely on the immediate prompt. `ContextStore` provides a **thread-safe, in-memory key-value store** that manages the **4-Context Framework**:
1. **Category Context**: Slang, tone guidelines, language taboos, etc.
2. **Merchant Context**: The business's persona, languages spoken, location, and operating style.
3. **Trigger Context**: The event that caused the outreach (e.g., 15 orders dropped off).
4. **Customer Context**: Information regarding a specific end-user (if applicable).

It uses versioning to ensure that concurrent updates gracefully replace old data without locking up the agent.

### C. The LLM Composer Engine (`bot/composer.py`)
This is the \"brain\" of the bot. It transforms structured context data into natural sounding, conversion-optimized messages. 
- **Proactive Messages (`compose_message`)**: Takes the 4 contexts and injects them into a strict prompt template that forces the LLM to output a precise, culturally accurate message and a distinct CTA (Call to Action).
- **Reactive Messages (`compose_reply`)**: Takes the current context *plus* the conversation history to generate an appropriate response.
- **Intent Signals (`detect_intent_signals`)**: Employs rapid, rule-based Regex (e.g., identifying \"ha proceed\" or \"stop calling\") before the LLM pass, filtering out basic intents or opt-outs dynamically.
- **Fallback System (`_fallback_compose`)**: In the rare event the main LLM call fails, hallucinated, or throws an exception, this tier supplies deterministic, templated messages to avoid breaking the simulation.

### D. Multi-turn Tracker (`bot/conversation_tracker.py`)
Managing back-and-forth chatter requires state. The `ConversationTracker`:
- Records individual `Turn` objects (who spoke, when, and what was said).
- Aggregates conversation history under unique `conversation_id`s.
- Counts **Consecutive Auto-Replies**: Triggers logic to suppress or block merchants who get stuck in an AI loop or who explicitly request to be left alone.

---

## 4. Interaction Flow Overview

1. **Initialization:**
   The `judge_simulator.py` (or the real judge) spins up and fires dozens of `POST /v1/context` events. The `ContextStore` populates its memory.
2. **The Tick (Proactive Outreach):**
   The judge sends `POST /v1/tick` with `trigger_id=\"T-123\"`. The bot:
   - Queries `ContextStore` for `T-123` details.
   - Discovers it's for merchant `M-456`.
   - Queries `ContextStore` for `M-456` and their relevant category.
   - Passes all 3 records to `composer.compose_message`.
   - The Composer returns the drafted message.
   - The bot creates a new state block in `ConversationTracker` and responds to the API.
3. **The Back-and-Forth (Reactive Reply):**
   The merchant responds with "Ok, let's start." (`POST /v1/reply`). The bot:
   - Finds the conversation in `ConversationTracker`.
   - Uses `composer.detect_intent_signals` to see it's a positive confirmation.
   - Dispatches `composer.compose_reply`, fetching the latest turn.
   - AI generates the response acknowledging the start.
   - `bot.py` sends the payload back and updates `ConversationTracker` with its new reply.

---

## 5. Running the Project

For a detailed guide on how to setup and run the environment locally, see `README.md` and `RUN-GEMINI.md`. Typical execution uses:
```bash
python run_local.py
```
This script launches both the FastAPI bot and a mock simulator instance that tests all the endpoint integration locally.
