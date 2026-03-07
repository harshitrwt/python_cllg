# SmartPriceWatcher 

### AI-Powered Product Price Tracker with RAG Insights

SmartPriceWatcher is a lightweight AI-powered application that allows users to track product prices from e-commerce platforms like Amazon and Flipkart.

Users can:

* Create accounts
* Add product URLs to a watchlist
* Track real-time price updates
* View price history trends
* Receive alerts when prices drop below a target
* Ask an AI assistant questions about their price data

The project combines **web scraping, price monitoring, visualization, and (RAG)** to generate insights from collected price history.

---

# Features

### Core Features

✔ User signup and login
✔ Add product URLs to a watchlist
✔ Automatic price scraping
✔ Price history tracking
✔ Target price alerts
✔ Price trend visualization

### AI Features

✔ Ask AI about product prices
✔ AI-generated price insights
✔ Cheapest product detection
✔ Price drop analysis
✔ Buying recommendation

---


# System Architecture

```
            ┌───────────────────┐
            │      User UI      │
            │  (Streamlit App)  │
            └─────────┬─────────┘
                      │
                      │
             User Interaction
                      │
          ┌───────────▼───────────┐
          │     Backend Logic     │
          │                       │
          │  • Authentication     │
          │  • Watchlist Manager  │
          │  • Price Tracker      │
          └───────┬───────┬───────┘
                  │       │
                  │       │
        ┌─────────▼─┐   ┌─▼──────────┐
        │  Scraper  │   │  Database  │
        │BeautifulSoup│ │  SQLite    │
        └──────┬─────┘   └─────┬─────┘
               │               │
               │               │
         Product Pages     Price History
               │               │
               ▼               ▼
        ┌─────────────────────────┐
        │      Vector Store       │
        │  (FAISS / ChromaDB)     │
        └───────────┬─────────────┘
                    │
                    ▼
              AI Assistant
        (Lightweight LLM + RAG)
```

---

# Application Workflow

```
User Login
     │
     ▼
Add Product URL
     │
     ▼
Scraper Fetches Price
     │
     ▼
Store Price in Database
     │
     ▼
Update Price History
     │
     ▼
Check Target Price
     │
     ├── Price > Target → Continue tracking
     │
     └── Price ≤ Target → Alert User
     │
     ▼
Generate Price Insights (AI)
```

---

# User Interface Navigation

The UI is designed to be **minimal and intuitive**.

### 1️⃣ Login / Signup Page

Users can:

* Create account
* Login
* Access dashboard

---

### 2️⃣ Dashboard

Users see:

```
-----------------------------------
Welcome, Username

Add Product
[ Product URL ]
[ Target Price ]
[ Add Button ]

-----------------------------------

Your Watchlist

Product | Current Price | Target | Status
------------------------------------------
Laptop  | ₹52000        | ₹50000 | Tracking
Shoes   | ₹2200         | ₹2000  | Tracking
```

---

### 3️⃣ Price Trend Visualization

Users can open a product to view history.

```
Price Trend

6000 ┤
5500 ┤   █
5000 ┤   █      █
4500 ┤   █      █
4000 ┤   █      █
3500 ┤   █      █
```

Or view **Matplotlib graphs**.

---

### 4️⃣ AI Assistant Panel

Users can ask questions like:

```
Which product is cheapest?
Did any product drop recently?
Should I buy the laptop now?
Show me biggest price drop.
```

AI retrieves relevant price history and answers.

---

# Project Structure

```
SmartPriceWatcher/

app.py
scraper.py
tracker.py
database.py
alerts.py

rag/
   embeddings.py
   vector_store.py
   qa.py

data/
   prices.db

README.md
requirements.txt
```

---

# Data Storage

The system uses **SQLite**.

### Users Table

| id | username | password |

---

### Watchlist Table

| id | user_id | url | product_name | target_price | last_price |

---

### Price History Table

| id | product_id | price | timestamp |

---

#  AI Model Choice

To keep the system **lightweight**, we use small embedding models.

Recommended models:

### Embeddings Model

```
all-MiniLM-L6-v2
```

Size:

```
~90MB
```

Advantages:

✔ Fast
✔ Low memory usage
✔ Works on CPU

---

### LLM Options

#### Option 1 (Local)

```
Ollama + Llama3 8B
```

Pros:

* Private
* Free

Cons:

* Requires ~8GB RAM

---

#### Option 2 (Lightweight Cloud)

```
OpenAI GPT-4o-mini
```

Pros:

* Cheap
* Very fast
* High quality answers

---

Recommended for this project:

```
Embeddings: all-MiniLM-L6-v2
LLM: GPT-4o-mini
Vector DB: FAISS
```

---

# Price Monitoring Scheduler

The application runs a background scheduler.

```
Every 30 minutes
      │
      ▼
Fetch product page
      │
      ▼
Extract price
      │
      ▼
Save price history
      │
      ▼
Check alert condition
```

---

# Price Insight Generation

Example stored data:

```
Product: Headphones

Price History:
5000
4800
4700
4500
4200
```

AI analysis:

```
The product has dropped 16% in the past week.
The current price is the lowest recorded.
This may be a good time to purchase.
```

---

---

# Future Enhancements

Possible upgrades:

### Browser Extension

Track prices automatically while browsing.

### Multi-site Comparison

Compare Amazon vs Flipkart prices.

### AI Price Prediction

Predict future prices using ML.

### Telegram Alerts

Send alerts via Telegram bot.

### Deal Detection

AI finds unusually low prices.

---



#  Installation

Install dependencies:

```
pip install requests beautifulsoup4 pandas numpy matplotlib streamlit schedule sentence-transformers faiss-cpu
```

Run application:

```
streamlit run app.py
```

---

# Project Goal

The goal of SmartPriceWatcher is to demonstrate:

* Web scraping
* Data pipelines
* Price analytics
* AI integration
* Retrieval-Augmented Generation
* Full application architecture

It serves as a **complete AI-powered data product project** suitable for portfolios and learning modern AI application design.

---

### in progress ...
