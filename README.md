# 🎓 UIU Student Assistant

A Telegram bot built for **United International University (UIU)** students to make everyday academic tasks easier.

Instead of checking different places for CGPA calculations, fee estimates, academic information, scholarship-related calculations, registration links, and other useful resources, students can access them directly from Telegram through a simple button-based interface.

The project is built with Python and is designed to be lightweight, modular, and easy to maintain.

---

## 📌 What is UIU Student Assistant?

UIU Student Assistant is a student-focused Telegram bot that brings several commonly used academic utilities into one place.

The main idea behind the project is simple:

> **Students should be able to get common academic information and calculations without going through unnecessary steps.**

The bot currently includes:

- 🧮 CGPA Calculator
- 💰 Fee Calculator
- 🎓 Scholarship Chance Estimator
- 📚 Academic Information
- 📊 Grading System
- 🎓 Credit System
- 🔄 Retake Course Policy
- 📝 Course Registration Links
- 🎓 Admission Information
- 🎓 Graduation / Convocation Information
- 📅 Academic Calendar
- ⚙️ User Settings
- 👨‍💼 Admin Features

---

# ✨ Main Features

## 🧮 CGPA Calculator

The CGPA calculator allows students to calculate their CGPA by entering their previous academic information and current course results.

The calculation flow can handle:

- Previous credits
- Previous CGPA
- Number of courses
- Course credits
- Course grades
- Multiple courses
- UIU grading system

The grading system can also be accessed while using the calculator, so students do not have to leave the calculation flow just to check a grade point.

The goal is to keep the process simple and avoid asking unnecessary questions.

---

## 💰 Fee Calculator

The fee calculator provides an estimated academic fee based on the information provided by the student.

It can take into account:

- Academic system
- Credit fee
- Trimester fee
- Registered credits
- Retake courses
- Retake credits
- Discount type
- Discount percentage

Since fees can depend on different academic and university-specific conditions, the result should be treated as an estimate rather than an official billing amount.

---

# 🎓 Scholarship Chance Estimator

One of the more interesting features of the bot is the scholarship chance estimator.

The purpose of this feature is not to claim an exact ranking. Instead, it gives students an idea of how their scholarship chances may look based on the information they provide.

The estimator uses:

- Previous GPA
- Academic program
- Approximate program size
- Qualifying credits
- Estimated number of students with a higher GPA

---

## Two Ways to Use the Estimator

### 📊 I Have an Estimate

If a student has an idea of how many students might have a higher GPA, they can enter that number.

For example:

```text
18
```

The number is then used by the estimation system to simulate possible ranking outcomes.

---

### 🤷 I Don't Know

If the student has no idea how many students may have a higher GPA, they can simply choose:

```text
🤷 I don't know
```

The system then makes a statistical estimate using the available information, mainly the student's GPA and the approximate program size.

This means students don't have to guess a number just to use the calculator.

---

# 🧠 How the Scholarship Estimator Works

The current scholarship estimator **does not use an AI or Machine Learning model**.

It uses a statistical approach combined with Monte Carlo simulation.

In simple terms, the system does not say:

> "Your exact position is X."

Instead, it considers a range of possible situations and checks how often the student falls into each scholarship bracket.

The process roughly looks like this:

```text
Student Information
       ↓
Eligibility Check
       ↓
Estimate Higher-GPA Students
       ↓
Generate Possible Ranking Scenarios
       ↓
Run Monte Carlo Simulation
       ↓
Classify Each Result
       ↓
Calculate Estimated Chances
       ↓
Show Result
```

---

## 🎲 Monte Carlo Simulation

The current implementation runs around:

```text
10,000 simulations
```

for an estimation.

For each simulation, the system generates a possible ranking scenario.

After all simulations are completed, the results are grouped into scholarship categories.

For example, the output may look like:

```text
100% Scholarship → 5%
50% Scholarship  → 65%
25% Scholarship  → 30%
No Scholarship   → <1%
```

These numbers describe the simulated outcomes.

They are **not official UIU scholarship probabilities**.

---

# 🏆 Scholarship Brackets

The current estimator follows this ranking structure:

| Ranking            |    Scholarship |
| ------------------ | -------------: |
| Top 2%             |           100% |
| Next 4%            |            50% |
| Next 4%            |            25% |
| Remaining students | No Scholarship |

Eligibility requirements are checked before the ranking estimation.

---

# 📈 Confidence

The estimator also shows an approximate confidence level:

- Low
- Medium
- High

For example, when the student provides an estimated number of higher-GPA students, the system has more information to work with and may produce a higher confidence level.

This confidence value is simply an indicator of how much information was available to the estimator.

It is **not an official statistical confidence interval**.

---

# ⚠️ Important Scholarship Disclaimer

The scholarship estimator is only an **approximate statistical estimate**.

It is not:

- An official UIU ranking
- An exact position
- A guaranteed scholarship
- An official scholarship probability
- A replacement for UIU's actual scholarship decision

Final scholarship decisions are made by UIU according to the university's applicable rules and the actual academic performance of students.

Students should always verify the latest official UIU regulations before relying on scholarship-related information.

The estimator also considers applicable eligibility requirements and excludes courses such as:

- Thesis
- Project
- Internship
- Retake
- Repeat

where applicable to the estimation.

---

# 📚 Academic Information

The bot provides commonly needed academic information directly through the Academic Information menu.

Currently available sections include:

### 🎓 Credit System

Provides an overview of UIU's credit-hour-based academic system, including:

- Credit hour concept
- Typical theory course credits
- Typical laboratory course credits
- Project / thesis credit information
- Degree completion requirements

The bot also reminds students that exact credit requirements can vary by program and curriculum revision.

---

### 🔄 Retake Course Policy

Provides information about UIU retake courses, including the first-time retake discount.

The bot explains:

- First-time retake discount
- Retake registration
- Effect on academic records
- Possible CGPA implications
- The need to verify the latest university rules

---

### 📝 Course Registration

Provides direct access to UIU's registration-related portals.

Students can access:

- UCam Cloud
- UCam — UIU

The bot provides the links directly so students can quickly open the required portal.

---

### 📊 Grading System

The bot provides the grading system used by the CGPA calculator so students can easily understand the relationship between grades and grade points.

---

### 📅 Academic Calendar

The bot also includes an academic calendar checking system.

A scheduled background job periodically checks the UIU academic calendar source for relevant updates.

---

# ⚙️ User Experience

A major focus of the project is keeping the bot easy to use.

The interface is mainly button-based, so users don't have to remember complicated commands.

For multi-step features such as CGPA, fee, and scholarship calculations, the bot guides the user through the required information one step at a time.

Where appropriate, users can cancel the current operation using:

```text
❌ Cancel
```

This prevents users from getting stuck inside a calculation flow.

---

# 🏗️ Project Architecture

The project is divided into several parts so that each feature can be maintained independently.

```text
Telegram User
      │
      ▼
Telegram Bot API
      │
      ▼
FastAPI
      │
      ▼
python-telegram-bot
      │
      ├───────────────┐
      │               │
      ▼               ▼
  Handlers         Services
      │               │
      └───────┬───────┘
              │
              ▼
           TiDB
```

The main idea is to keep Telegram-specific interaction code separate from the actual calculation and business logic.

---

# 📁 Project Structure

```text
Telegram-Uni-Bot/
│
├── bot.py
├── config.py
├── database.py
├── states.py
├── keyboards.py
├── requirements.txt
├── .gitignore
├── .env
│
├── handlers/
│   ├── admin.py
│   ├── academic.py
│   ├── calendar.py
│   ├── cgpa.py
│   ├── fee.py
│   ├── general.py
│   └── scholarship.py
│
└── services/
    ├── scholarship_service.py
    └── ...
```

---

# 📄 Important Files

## `bot.py`

This is the main entry point of the application.

It handles things such as:

- FastAPI setup
- Telegram application setup
- Handler registration
- Webhook configuration
- Scheduled jobs
- Application startup
- Application shutdown
- Health endpoint

---

## `config.py`

Stores application-level configuration.

Some of the important settings include:

```python
BOT_TOKEN
ADMIN_USER_IDS

DEFAULT_CREDIT_FEE
DEFAULT_TRIMESTER_FEE
DEFAULT_OTHER_FEES
DEFAULT_MINIMUM_PAYMENT

DEFAULT_SCHOLARSHIP_CREDIT_LIMIT
DEFAULT_SCHOLARSHIP_GPA_THRESHOLD
DEFAULT_PROBATION_THRESHOLD

DEFAULT_FIRST_RETAKE_DISCOUNT_PERCENT

INSTALLMENT_1_PERCENT
INSTALLMENT_2_PERCENT
INSTALLMENT_3_PERCENT
```

The bot token is loaded from the environment:

```python
BOT_TOKEN = os.getenv("BOT_TOKEN")
```

---

## `database.py`

Handles the database connection and initialization.

The production application uses TiDB Cloud through its MySQL-compatible interface.

---

## `states.py`

Contains the conversation state constants used by different ConversationHandlers.

This keeps state management organized and prevents different features from accidentally using conflicting state values.

---

## `keyboards.py`

Contains reusable Telegram keyboards.

Keeping keyboards in one place makes it easier to maintain the bot's interface.

---

## `handlers/`

This directory contains the Telegram interaction logic.

For example:

```text
handlers/cgpa.py
```

handles the CGPA conversation.

```text
handlers/scholarship.py
```

handles the scholarship conversation.

```text
handlers/fee.py
```

handles the fee calculation flow.

---

## `services/`

This directory contains the actual business logic.

For example:

```text
services/scholarship_service.py
```

contains the scholarship estimation engine.

This means the scholarship calculation can be tested independently without running the Telegram bot.

---

# 🗄️ Database

The current production database is:

## TiDB Cloud

TiDB is MySQL-compatible, which makes it convenient to use with Python's MySQL connectors.

The project uses:

```text
mysql-connector-python
```

for database connectivity.

The database configuration is loaded from environment variables.

---

## Environment Variables

The application expects:

```env
TIDB_HOST=YOUR_TIDB_HOST
TIDB_PORT=4000
TIDB_USER=YOUR_TIDB_USER
TIDB_PASSWORD=YOUR_TIDB_PASSWORD
TIDB_DATABASE=YOUR_DATABASE
```

The database tables are initialized when the application starts.

A successful startup produces a message similar to:

```text
TiDB tables initialized successfully.
```

---

# 🗑️ SQLite Database

Earlier development versions used a local SQLite database.

The old file was:

```text
uiu_assistant.db
```

The current production version does not depend on that file.

The production database is TiDB Cloud.

Therefore, the SQLite database file does not need to be kept in the repository.

---

# ⚙️ Technology Stack

| Technology             | Purpose                         |
| ---------------------- | ------------------------------- |
| Python                 | Main programming language       |
| python-telegram-bot    | Telegram bot framework          |
| FastAPI                | Web server and webhook endpoint |
| Uvicorn                | ASGI server                     |
| TiDB Cloud             | Production database             |
| mysql-connector-python | Database connection             |
| HTTPX                  | HTTP requests                   |
| BeautifulSoup4         | Web content parsing             |
| Feedparser             | Feed / RSS parsing              |
| APScheduler            | Scheduled tasks                 |
| python-dotenv          | Environment configuration       |
| Render                 | Deployment / hosting            |

---

# 📦 Requirements

The main dependencies are:

```text
python-telegram-bot[job-queue,webhooks]==22.8
python-dotenv==1.2.2
feedparser==6.0.11
fastapi==0.111.0
uvicorn==0.30.1
httpx==0.28.1
beautifulsoup4==4.14.2
mysql-connector-python==9.4.0
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/souravsahapartho/Telegram-Uni-Bot.git
```

Then:

```bash
cd Telegram-Uni-Bot
```

---

## 2. Create a Virtual Environment

On Windows:

```bash
python -m venv venv
```

For Git Bash:

```bash
source venv/Scripts/activate
```

For Windows CMD:

```cmd
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

If needed:

```bash
python -m pip install mysql-connector-python==9.4.0
```

---

# 🔐 Environment Configuration

Create a `.env` file in the project root.

Example:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

ADMIN_USER_IDS=123456789,987654321

TIDB_HOST=YOUR_TIDB_HOST
TIDB_PORT=4000
TIDB_USER=YOUR_TIDB_USER
TIDB_PASSWORD=YOUR_TIDB_PASSWORD
TIDB_DATABASE=YOUR_DATABASE
```

Do not commit this file to GitHub.

---

# ▶️ Run the Bot Locally

Start the application with:

```bash
python bot.py
```

A successful startup should look similar to:

```text
TiDB tables initialized successfully.
Application started.
Academic calendar checker started.
Local mode detected. Webhook configuration skipped.
UIU Student Assistant is running.
Application startup complete.
```

The FastAPI server may run locally at:

```text
http://0.0.0.0:10000
```

---

# 🧪 Checking the Code Before Running

You can use Python's built-in compiler to check individual files.

For `bot.py`:

```bash
python -m py_compile bot.py
```

For the CGPA handler:

```bash
python -m py_compile handlers/cgpa.py
```

For the scholarship handler:

```bash
python -m py_compile handlers/scholarship.py
```

For the scholarship service:

```bash
python -m py_compile services/scholarship_service.py
```

For the database module:

```bash
python -m py_compile database.py
```

---

# 🧮 Testing the Scholarship Engine

The scholarship calculation can be tested without opening Telegram.

### Without a Higher-GPA Estimate

```bash
python -c "from services.scholarship_service import *; r=generate_estimate(3.80, 'BSCSE', 500, 14, None); print(generate_result_text(r))"
```

### With a Higher-GPA Estimate

```bash
python -c "from services.scholarship_service import *; r=generate_estimate(3.80, 'BSCSE', 500, 14, 18); print(generate_result_text(r))"
```

The second example assumes approximately 18 students have a higher GPA.

---

# 🌐 Telegram Webhook

For production, the bot uses Telegram's webhook system.

The request flow is:

```text
Telegram
   ↓
Render
   ↓
FastAPI
   ↓
/telegram/webhook
   ↓
python-telegram-bot
   ↓
Handler
```

The production webhook looks like:

```text
https://YOUR-SERVICE.onrender.com/telegram/webhook
```

When the webhook is configured successfully, the application logs something similar to:

```text
Webhook configured: https://your-service.onrender.com/telegram/webhook
```

---

# 🖥️ Local and Production Modes

The bot behaves differently depending on where it is running.

### Local

When running on a local machine:

```text
Local mode detected. Webhook configuration skipped.
```

This is expected because a local machine normally does not have a public HTTPS endpoint.

### Production

On Render, the bot detects the production environment and configures the Telegram webhook automatically.

---

# ☁️ Deployment on Render

The application can be deployed as a Render Web Service.

A typical start command is:

```bash
uvicorn bot:app --host 0.0.0.0 --port $PORT
```

Set the following environment variables in Render:

```text
BOT_TOKEN
ADMIN_USER_IDS
TIDB_HOST
TIDB_PORT
TIDB_USER
TIDB_PASSWORD
TIDB_DATABASE
```

After deployment, Render provides a public HTTPS URL which is used for the Telegram webhook.

---

# ❤️ Health Check

The application provides:

```text
GET /health
```

A successful request returns:

```text
HTTP 200 OK
```

Render can use this endpoint to check whether the service is alive.

---

# 📅 Academic Calendar Checker

The bot has a scheduled academic calendar checker.

It periodically checks the UIU academic calendar source for changes.

The scheduled task runs through the Telegram application's JobQueue.

Typical logs include:

```text
Academic calendar checker started.
```

and:

```text
Job "academic-calendar-check" executed successfully
```

---

# 🔒 Security

The project uses environment variables for sensitive information.

Never commit:

```text
.env
```

or credentials directly into the repository.

A recommended `.gitignore` includes:

```gitignore
.env
venv/
__pycache__/
*.pyc
*.db
```

Never expose:

- Telegram Bot Token
- TiDB Password
- Database Credentials
- API Keys
- SMTP Credentials
- JWT Secrets

If a token or credential is accidentally exposed, revoke or rotate it immediately.

---

# 🧹 Development Files

Temporary testing files such as:

```text
test_db.py
test_env.py
test_token.py
test_webhook.py
init_test.py
```

can be used during development.

They do not need to remain in the production repository after testing is complete.

---

# 🐛 Troubleshooting

## FastAPI Not Found

If you see:

```text
ModuleNotFoundError: No module named 'fastapi'
```

run:

```bash
python -m pip install -r requirements.txt
```

---

## Telegram Token Error

If the bot reports:

```text
telegram.error.InvalidToken: Unauthorized
```

check the `BOT_TOKEN` environment variable.

If the token has been revoked, generate a new token and update it in both local and production environments.

---

## TiDB Connection Error

Check all TiDB environment variables:

```env
TIDB_HOST=
TIDB_PORT=4000
TIDB_USER=
TIDB_PASSWORD=
TIDB_DATABASE=
```

If the application shows something like:

```text
MySQL server on 'None:4000'
```

then the environment variable was not loaded correctly.

---

## TiDB Permission Error

If you see:

```text
CREATE command denied
```

the database user does not have sufficient permission to create the required tables.

Use a database user with the necessary permissions during initial setup.

---

## Webhook Error

If Telegram reports a webhook or `401 Unauthorized` error:

1. Check the current bot token.
2. Verify that the token works with Telegram's `getMe` endpoint.
3. Check the current webhook using `getWebhookInfo`.
4. Make sure Render contains the latest token.
5. Redeploy after changing environment variables.

---

# 🔮 Future Plans

There are several directions in which the project can be improved.

Some possible additions include:

- 👤 Student profiles
- 📊 CGPA history
- 💰 Fee calculation history
- 🎓 Scholarship estimation history
- 📚 Course planning
- 📅 Semester planning
- 🔔 Academic notifications
- 📢 UIU announcement monitoring
- 📈 More detailed academic statistics
- 👨‍💼 Better admin analytics
- 🔗 Additional UIU service integrations

---

# 🤖 Future Scholarship Model

The current scholarship estimator is intentionally statistical rather than AI-based.

If a sufficiently large and reliable historical dataset becomes available, the system could eventually be improved with a Machine Learning model.

Possible approaches could include:

- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost

However, an ML model should only be introduced when there is enough reliable historical data to make its predictions meaningful.

For now, the statistical Monte Carlo approach is easier to understand and explain to students.

---

# ⚠️ Accuracy Notice

This bot is an independent student project.

Information and calculations provided by the bot should not be treated as a replacement for official university information.

For important academic decisions, students should verify information directly with UIU.

This is especially important for:

- Scholarship decisions
- Course registration
- Tuition fees
- Academic regulations
- Graduation requirements
- Course prerequisites
- Credit requirements

The bot intentionally labels estimated results as estimates rather than presenting them as official decisions.

---

# 🤝 Contributing

Contributions and suggestions are welcome.

A basic workflow is:

```bash
git clone <repository-url>

cd Telegram-Uni-Bot

git checkout -b feature/your-feature

git add .

git commit -m "Add your feature"

git push origin feature/your-feature
```

Then create a Pull Request.

Before submitting changes, make sure the relevant Python files compile successfully.

---

# 📜 License

The project can be released under the license chosen by the developer.

If using MIT License, include a `LICENSE` file containing the standard MIT License text.

---

# 👨‍💻 Developer

**Sourav Saha**

UIU Student
Computer Science & Engineering

This project was developed as a student-focused tool to make everyday academic tasks and information easier to access through Telegram.

---

# 🙏 Built With

This project uses:

- 🐍 Python
- 🤖 python-telegram-bot
- ⚡ FastAPI
- 🚀 Uvicorn
- 🗄️ TiDB Cloud
- 🌐 HTTPX
- 📰 Feedparser
- 🔎 BeautifulSoup4
- ⏰ APScheduler
- ☁️ Render

---

# 📌 Project Status

**Active Development**

The project is still being improved and new features may be added over time.

Current focus areas include:

- Academic utilities
- Scholarship estimation
- Database reliability
- User experience
- Automation
- Admin features
- Production stability

---

# 🎯 Final Note

UIU Student Assistant is built around a simple idea:

> **Make useful academic tools available to UIU students from one familiar place — Telegram.**

From calculating CGPA and estimating academic fees to checking academic information and exploring scholarship possibilities, the goal is to reduce unnecessary steps and make everyday academic tasks a little easier.

---

<p align="center">
  <strong>🎓 UIU Student Assistant</strong>
  <br>
  Built for UIU students.
</p>
