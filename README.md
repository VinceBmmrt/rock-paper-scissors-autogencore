# 🪨✂️📄 Rock-Paper-Scissors Autogen Playground

Welcome to this **Autogen Core playground**! 🚀  
This project is designed to **discover and explore Autogen Core**. It demonstrates how autonomous agents can communicate, handle messages asynchronously, and interact with large language models like OpenAI and Ollama. Think of it as a **playground to experiment and learn**, without any production constraints. 🤖✨

---

## 🔑 Key Concepts

- **Runtime Orchestration:** The SingleThreadedAgentRuntime coordinates all agents and their interactions.  
- **Agent Registration:** Each agent is added with a unique AgentId to enable communication.  
- **Message Handling:** Agents process messages asynchronously via handlers. Responses can be routed to other agents or computed internally.  
- **Agent Communication:** Messages flow between agents, showing delegation, orchestration, and LLM integration. Multi-agent scenarios like Rock-Paper-Scissors illustrate these concepts in action.

---

## 🎯 Project Goal

This playground is a **learning and exploration tool** for developers and AI enthusiasts. It allows you to:

- Understand agent registration and runtime orchestration.
- Explore asynchronous message handling.
- See how multi-agent interactions and LLM delegation work in practice.

---

## ⚙️ Setup

Clone the repository, create and activate a virtual environment, install dependencies for Autogen Core, AgentChat, OpenAI, Ollama, and dotenv, and add your API keys in a `.env` file. For that yo
u can install uv from Oracle and run in your terminal "uv sync"

---

## 🏃 Running the Playground
Run in your terminal "uv run main.py" 
Running this project simulates a **rock-paper-scissors match** between two agents, with results printed in the console. It’s purely educational and gives you a clear view of how agents interact and the runtime orchestrates them.

---