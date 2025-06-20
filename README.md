# 🎬 Real-Time Movie Intelligence System

A real-time GenAI application powered by **Confluent Kafka**, **CrewAI**, and **Gemini/Groq**. This system intelligently processes user movie queries, extracts intent, enriches context using user profiles, and generates personalized movie recommendations — all streamed live to a dashboard.

---

## 🚀 Overview

This project combines:
- 🔌 **Confluent Kafka** for real-time data ingestion and streaming
- 🧠 **Agentic AI (CrewAI)** for multi-step reasoning using LLMs
- 🤖 **Gemini/Groq** for ultra-fast inference
- 📊 **Streamlit** for live, interactive insights

---

## 🧠 Architecture

User Query → Kafka (movie_queries)
↓
🎭 CrewAI Pipeline
↓
Kafka (movie_insights) → 📊 Streamlit Dashboard


---

## 🧩 Kafka Topics Used

| Topic Name         | Description                                   |
|--------------------|-----------------------------------------------|
| `movie_queries`     | Ingests user prompts for recommendations     |
| `movie_insights`    | Publishes enriched insights & recommendations |
| `topic_movies`      | Movies metadata (from MongoDB)               |
| `topic_users`       | User profile data                            |
| `topic_comments`    | Movie review comments                        |
| `topic_theaters`    | Theater-related data                         |

---

## 🤖 CrewAI Agents

| Agent                  | Purpose                                                  |
|------------------------|----------------------------------------------------------|
| `Intent Classifier`    | Extracts genre, theme, reference movie from query        |
| `User Context Agent`   | Personalizes filters using user profile                  |
| `Recommender Agent`    | Finds matching movies based on enriched filters          |
| `Summary Agent`        | Generates a natural language summary of the recommendation |

LLMs like **Gemini 1.5 Pro** or **Groq Llama3** are used behind each agent for reasoning.

---

## 📦 Project Structure

```
confluent_hackathon/
├── agents/
│ ├── crew_config.py # CrewAI agent definitions and pipeline setup
│ └── tools.py # Custom tools (KafkaDataTool, etc.)
├── dashboard/
│ └── dashboard.py # Streamlit dashboard (real-time view)
├── kafka_producers/
│ └── data_ingestion.py # Pushing data to Kafka
├── static/
│ ├── movies.json # Fallback movie data (from MongoDB)
│ └── users.json # Fallback user profiles
├── client.properties # Kafka credentials (from Confluent Cloud)
├── pipeline.py # Main pipeline (Kafka → LLM → Kafka)
└── README.md
```

---

## 🛠️ How It Works

1. **User sends a query** to the `movie_queries` Kafka topic.
2. **Kafka consumer** picks it up and passes it to CrewAI agents.
3. **CrewAI agents** reason step-by-step using Gemini/Groq.
4. The final summary is **pushed to `movie_insights`** Kafka topic.
5. A **Streamlit dashboard** consumes and displays it live.

---

## 🖥️ How to Run

### 1. Install dependencies


2. Set up Kafka credentials
Create a client.properties file with your Confluent Cloud details:

properties
```
bootstrap.servers=...
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.username=...
sasl.password=...
```

### 3. Start the pipeline
```bash
python pipeline.py
```
### 4. Send a sample query

```bash
python kafka_prdoucers/data_ingestion.py
```

### 5. Run the dashboard
```bash
streamlit run dashboard.py
```

💡 Sample Query

Sent to Kafka topic movie_queries:

```bash
{
  "user_id": "U1",
  "prompt": "Recommend a sci-fi thriller like Interstellar"
}
```

Output on dashboard:

🎯 Query from User U1

🔍 Detected Filters: { "genre": "sci-fi", "theme": "thriller" }

🎬 Recommendations: ["Arrival", "Inception", "Blade Runner 2049"]

🧠 Summary: "Based on your interest in Interstellar..."

🏆 Why This is a Great Hackathon Use Case
✅ Business Value:

Personalized recommendations

Agentic AI reasoning

Real-time feedback via dashboard

✅ Confluent Leverage:

Kafka for stream ingestion & results

Supports multiple sources (Twitter, support chats, etc.)

Optional Flink SQL integration for analytics

✅ LLM Innovation:

Agentic orchestration using CrewAI

Fast inference using Groq or Gemini

📈 Optional Enhancements
Add Flink SQL to join topic data (e.g., comments + movies)

Store movie_insights in a real-time DB (PostgreSQL or MongoDB)

Add feedback/rating loop

Build a WhatsApp bot using Twilio

🙌 Credits
Built with:

🧠 CrewAI

⚡ Groq

🤖 Gemini Pro

☁️ Confluent Cloud

📊 Streamlit
