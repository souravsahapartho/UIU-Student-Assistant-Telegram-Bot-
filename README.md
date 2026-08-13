# 🎓 UIU Smart Assistant

**UIU Smart Assistant** is a Telegram bot built to make everyday academic tasks easier for students of **United International University (UIU)**.

The idea behind the project is simple: instead of checking different websites, doing calculations manually, or going through the same information repeatedly, students can get many useful academic tools and resources directly from Telegram.

The bot provides a simple button-based interface and guides users through different tasks step by step.

---

## ✨ Features

### 🧮 CGPA Calculator

The CGPA calculator helps students calculate their current or expected CGPA without doing the calculations manually.

It supports:

- Previous CGPA
- Previous completed credits
- Number of current courses
- Course credits
- Course grades
- Multiple course entries
- UIU grading system

The grading system is also available during the calculation process, so users can check grade points without leaving the calculator.

---

### 💰 Fee Calculator

The fee calculator gives students an estimated idea of how much they may need to pay for a trimester.

It can consider:

- Academic system
- Credit fee
- Trimester fee
- Registered credits
- Retake courses
- Retake credits
- Discount type
- Discount percentage

The result is an estimate based on the information provided by the user and should not be considered an official university bill.

---

### 🎓 Scholarship Chance Estimator

The Scholarship Chance Estimator is designed to give students an idea of their possible merit scholarship outcome based on their academic information.

It takes information such as:

- Previous GPA
- Academic program
- Approximate number of students in the program
- Qualifying credits
- Estimated number of students with a higher GPA

The calculator has two simple options.

#### 📊 I Have an Estimate

If the student already has an idea about how many students may have a higher GPA, they can enter that number.

For example:

```text
18
````

The provided number is then used in the calculation.

#### 🤷 I Don't Know

If the student doesn't know how many students may have a higher GPA, they can simply select:

```text
🤷 I don't know
```

The system will make a statistical estimate based on the available information.

This way, users don't have to guess a number just to use the calculator.

---

## 🧠 How the Scholarship Estimator Works

The current scholarship estimator does **not use an AI or Machine Learning model**.

Instead, it uses a statistical approach combined with **Monte Carlo simulation**.

The basic process is:

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
Calculate Scholarship Outcomes
        ↓
Show Estimated Result
```

The estimator runs around **10,000 simulations** for a calculation.

Each simulation represents a possible ranking scenario. After running the simulations, the results are grouped into the different scholarship categories.

For example, the result may look like:

```text
100% Scholarship → 5%
50% Scholarship  → 65%
25% Scholarship  → 30%
No Scholarship   → <1%
```

These percentages are based on the simulation and are **not official UIU scholarship probabilities**.

---

## 🏆 Scholarship Brackets

The current estimator uses the following ranking structure:

| Ranking   |    Scholarship |
| --------- | -------------: |
| Top 2%    |           100% |
| Next 4%   |            50% |
| Next 4%   |            25% |
| Remaining | No Scholarship |

The system checks the relevant eligibility requirements before estimating the scholarship outcome.

---

## 📈 Confidence

The scholarship estimator also shows an approximate confidence level:

* Low
* Medium
* High

If the user provides more useful information, such as an estimated number of higher-GPA students, the system has more information to work with.

The confidence level is only an indicator of the quality of the available input. It is **not an official statistical confidence interval**.

---

## ⚠️ Important Note About Scholarship Estimates

The scholarship calculator is only an **approximate statistical estimator**.

It is **not**:

* An official UIU ranking system
* An exact ranking calculator
* A guaranteed scholarship prediction
* An official scholarship probability calculator
* A replacement for UIU's actual scholarship decision

Final scholarship decisions are made by UIU according to the university's applicable rules and the actual academic performance of students.

Students should always check the latest official UIU rules before making decisions based on scholarship-related information.

The estimator also considers applicable course and credit restrictions, including exclusions such as:

* Thesis
* Project
* Internship
* Retake
* Repeat courses

where applicable.

---

# 📚 Academic Information

The bot includes an **Academic Information** section where students can quickly find commonly needed UIU information.

Currently available sections include:

### 🎓 Credit System

Provides a simple explanation of:

* Credit hours
* Theory course credits
* Laboratory course credits
* Project / thesis credits
* Degree completion requirements

The bot also reminds users that exact credit requirements may vary depending on the program and curriculum.

---

### 🔄 Retake Course Policy

Provides information about UIU's retake policy, including:

* First-time retake discount
* Retake registration
* Academic record considerations
* Possible CGPA effects
* Important points to verify before registration

---

### 📝 Course Registration

Provides direct access to the UIU registration portals.

The bot includes:

* UCam Cloud
* UCam — UIU

Users can simply tap the appropriate button and open the registration portal.

---

### 📊 Grading System

The bot provides the grading system used by the CGPA calculator so that students can easily understand grades and their corresponding grade points.

---

### 📅 Academic Calendar

The bot also includes an academic calendar checker.

A scheduled background task periodically checks the UIU academic calendar source for updates.

---

# 👤 User Experience

One of the main goals of the project is to keep the bot simple.

Instead of making users type complicated commands, most features are accessible through buttons.

For multi-step features such as:

* CGPA calculation
* Fee calculation
* Scholarship estimation

the bot asks only for the information it actually needs.

Where appropriate, users can cancel an ongoing process using:

```text
❌ Cancel
```

After cancelling, the user can return to the main menu and start another feature.

---

# 🏗️ Project Structure

The project is organized into separate modules so that different parts of the bot can be maintained independently.

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

# 📄 Main Files

### `bot.py`

This is the main entry point of the application.

It is responsible for:

* Starting FastAPI
* Initializing the Telegram bot
* Registering handlers
* Configuring the webhook
* Starting scheduled tasks
* Managing application startup and shutdown
* Providing the health endpoint

---

### `config.py`

Contains the main configuration used by the application.

Some of the configuration values include:

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

Sensitive values such as the bot token are loaded from environment variables.

---

### `database.py`

Handles the database connection and initialization.

The production version of the project uses **TiDB Cloud** as the main database.

---

### `states.py`

Contains the conversation states used by the different multi-step features.

This keeps the ConversationHandlers organized and avoids state conflicts between different parts of the bot.

---

### `keyboards.py`

Contains reusable Telegram keyboards and menu layouts.

Keeping the keyboards in one place makes it easier to update the bot's interface later.

---

### `handlers/`

The `handlers` directory contains the Telegram conversation logic for individual features.

For example:

```text
handlers/cgpa.py
```

handles the CGPA calculation flow.

```text
handlers/scholarship.py
```

handles the scholarship estimation flow.

```text
handlers/fee.py
```

handles the fee calculation flow.

---

### `services/`

The `services` directory contains the actual business logic.

For example:

```text
services/scholarship_service.py
```

contains the scholarship estimation and Monte Carlo simulation logic.

Keeping this logic outside the Telegram handler makes it easier to test and maintain.

---

# 🗄️ Database

The production version of the bot uses:

## TiDB Cloud

TiDB is MySQL-compatible, so the application can connect to it using a MySQL connector.

The database connection is handled through:

```text
database.py
```

The project uses:

```text
mysql-connector-python
```

for the connection.

---

## Database Configuration

The application expects the following environment variables:

```env
TIDB_HOST=YOUR_TIDB_HOST
TIDB_PORT=4000
TIDB_USER=YOUR_TIDB_USER
TIDB_PASSWORD=YOUR_TIDB_PASSWORD
TIDB_DATABASE=YOUR_DATABASE
```

The required tables are initialized when the application starts.

A successful startup produces a message similar to:

```text
TiDB tables initialized successfully.
```

---

## SQLite

Earlier development versions of the project used a local SQLite database.

The old database file was:

```text
uiu_assistant.db
```

The current production version does not depend on this file.

The production database is TiDB Cloud, so the SQLite file does not need to be kept in the repository.

---

# ⚙️ Technology Stack

| Technology             | Used For                        |
| ---------------------- | ------------------------------- |
| Python                 | Main programming language       |
| python-telegram-bot    | Telegram bot                    |
| FastAPI                | Web server and webhook endpoint |
| Uvicorn                | ASGI server                     |
| TiDB Cloud             | Database                        |
| mysql-connector-python | Database connection             |
| HTTPX                  | HTTP requests                   |
| BeautifulSoup4         | Web parsing                     |
| Feedparser             | Feed / RSS parsing              |
| APScheduler            | Scheduled tasks                 |
| python-dotenv          | Environment variables           |
| Render                 | Deployment                      |

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

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/souravsahapartho/Telegram-Uni-Bot.git
```

Then enter the project directory:

```bash
cd Telegram-Uni-Bot
```

---

## 2. Create a Virtual Environment

On Windows:

```bash
python -m venv venv
```

If you are using Git Bash:

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

If required, install the database connector separately:

```bash
python -m pip install mysql-connector-python==9.4.0
```

---

# 🔐 Environment Variables

Create a `.env` file in the root directory.

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

Do not use your real credentials in the README.

Also make sure `.env` is included in `.gitignore`.

---

# ▶️ Run Locally

Start the application with:

```bash
python bot.py
```

A successful local startup should look similar to:

```text
TiDB tables initialized successfully.
Application started.
Academic calendar checker started.
Local mode detected. Webhook configuration skipped.
UIU Smart Assistant is running.
Application startup complete.
```

The local server can run on:

```text
http://0.0.0.0:10000
```

depending on the configured port.

---

# 🧪 Testing

Before running the bot, you can check whether the Python files contain syntax errors.

Check the main application:

```bash
python -m py_compile bot.py
```

Check the CGPA handler:

```bash
python -m py_compile handlers/cgpa.py
```

Check the scholarship handler:

```bash
python -m py_compile handlers/scholarship.py
```

Check the scholarship service:

```bash
python -m py_compile services/scholarship_service.py
```

Check the database module:

```bash
python -m py_compile database.py
```

---

# 🧮 Testing the Scholarship Calculator

The scholarship calculation logic can be tested separately without starting Telegram.

### Without a Higher-GPA Estimate

```bash
python -c "from services.scholarship_service import *; r=generate_estimate(3.80, 'BSCSE', 500, 14, None); print(generate_result_text(r))"
```

### With a Higher-GPA Estimate

```bash
python -c "from services.scholarship_service import *; r=generate_estimate(3.80, 'BSCSE', 500, 14, 18); print(generate_result_text(r))"
```

The second example assumes that approximately 18 students have a higher GPA.

---

# 🌐 Telegram Webhook

For production, the bot uses Telegram Webhooks.

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

The webhook URL follows this format:

```text
https://YOUR-RENDER-SERVICE.onrender.com/telegram/webhook
```

When it is configured successfully, the application logs something similar to:

```text
Webhook configured: https://your-service.onrender.com/telegram/webhook
```

---

# 🖥️ Local vs Production

### Local Development

When the bot is running locally, webhook configuration is skipped.

You may see:

```text
Local mode detected. Webhook configuration skipped.
```

This is normal because a local computer usually does not have a public HTTPS URL.

### Production

When deployed on Render, the application configures the Telegram webhook using the public Render URL.

---

# ☁️ Deployment

The bot is designed to run as a web service on **Render**.

A typical start command is:

```bash
uvicorn bot:app --host 0.0.0.0 --port $PORT
```

The following environment variables should be added to the Render service:

```text
BOT_TOKEN
ADMIN_USER_IDS
TIDB_HOST
TIDB_PORT
TIDB_USER
TIDB_PASSWORD
TIDB_DATABASE
```

After deployment, Render provides a public HTTPS URL that can be used for the Telegram webhook.

---

# ❤️ Health Check

The application provides a health endpoint:

```text
GET /health
```

A successful request returns:

```text
HTTP 200 OK
```

For example:

```text
GET /health HTTP/1.1" 200 OK
```

This endpoint can be used by Render to check whether the application is running properly.

---

# 📅 Academic Calendar Checker

The bot includes a scheduled academic calendar checker.

It periodically checks the UIU academic calendar source for updates.

The task runs through the JobQueue provided by `python-telegram-bot`.

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

to GitHub.

A recommended `.gitignore` is:

```gitignore
.env
venv/
__pycache__/
*.pyc
*.db
```

Never expose:

* Telegram Bot Token
* TiDB Password
* Database credentials
* API keys
* SMTP credentials
* JWT secrets

If a Telegram bot token or another secret is accidentally exposed, revoke or rotate it immediately.

---

# 🧹 Temporary Development Files

During development, small testing files may be created, such as:

```text
test_db.py
test_env.py
test_token.py
test_webhook.py
init_test.py
```

These files are only for testing and do not need to remain in the production repository.

---

# 🐛 Troubleshooting

## FastAPI is not installed

If you see:

```text
ModuleNotFoundError: No module named 'fastapi'
```

run:

```bash
python -m pip install -r requirements.txt
```

---

## Telegram Bot Token Error

If you see:

```text
telegram.error.InvalidToken: Unauthorized
```

check the `BOT_TOKEN` value in `.env` or the Render environment variables.

If the token was revoked, generate a new one and update the application.

---

## TiDB Connection Error

Make sure these values are correct:

```env
TIDB_HOST=
TIDB_PORT=4000
TIDB_USER=
TIDB_PASSWORD=
TIDB_DATABASE=
```

If you see something like:

```text
MySQL server on 'None:4000'
```

the environment variable was not loaded correctly.

---

## TiDB Permission Error

If you see:

```text
CREATE command denied
```

the database user does not have enough permission to create the required tables.

Use a TiDB user with the required permissions during the initial database setup.

---

## Webhook Error

If Telegram reports a webhook or `401 Unauthorized` error:

1. Check the bot token.
2. Test the token using Telegram's `getMe` endpoint.
3. Check the webhook using `getWebhookInfo`.
4. Make sure Render has the latest token.
5. Redeploy after changing environment variables.

---

# 🔮 Future Improvements

The project is still being developed, so there are several things that can be added later.

Some possible improvements include:

* 👤 Student profiles
* 📊 CGPA history
* 💰 Fee calculation history
* 🎓 Scholarship estimation history
* 📚 Course planning
* 📅 Semester planning
* 🔔 Academic notifications
* 📢 UIU announcement monitoring
* 📈 More detailed academic statistics
* 👨‍💼 Improved admin analytics
* 🔗 More UIU service integrations

---

# 🤖 Possible Future Scholarship Improvements

The current scholarship estimator uses statistics and Monte Carlo simulation rather than Machine Learning.

If enough reliable historical data becomes available in the future, the estimator could potentially be improved with an ML model.

Possible approaches could include:

* Logistic Regression
* Random Forest
* Gradient Boosting
* XGBoost

However, using Machine Learning would only make sense if there is enough reliable and representative data.

For now, the statistical approach keeps the system easier to understand and more transparent.

---

# ⚠️ Accuracy Notice

UIU Smart Assistant is an independent student project.

The information and calculations provided by the bot should not replace official information from UIU.

Students should verify important information directly with the university, especially for:

* Scholarship decisions
* Course registration
* Tuition fees
* Academic regulations
* Graduation requirements
* Course prerequisites
* Credit requirements

The bot intentionally presents estimated results as estimates instead of claiming that they are official decisions.

---

# 🤝 Contributing

Suggestions, improvements, and contributions are welcome.

A basic contribution workflow is:

```bash
git clone <repository-url>

cd Telegram-Uni-Bot

git checkout -b feature/your-feature

git add .

git commit -m "Add your feature"

git push origin feature/your-feature
```

After that, open a Pull Request.

Before pushing changes, it is recommended to test the affected Python files using `py_compile`.

---

# 📜 License

Choose the license you want to use for the project and add the corresponding `LICENSE` file to the repository.

For example:

```text
MIT License
```

---

# 👨‍💻 Developer

**Sourav Saha**

Computer Science & Engineering Student
United International University

This project was built with the goal of making commonly used academic tasks and information easier to access for UIU students through Telegram.

---

# 🙏 Built With

This project uses:

* 🐍 Python
* 🤖 python-telegram-bot
* ⚡ FastAPI
* 🚀 Uvicorn
* 🗄️ TiDB Cloud
* 🌐 HTTPX
* 📰 Feedparser
* 🔎 BeautifulSoup4
* ⏰ APScheduler
* ☁️ Render

---

# 📌 Project Status

**Active Development**

The project is still evolving, and new features, improvements, and fixes may be added over time.

Current areas of development include:

* Academic utilities
* Scholarship estimation
* Database reliability
* User experience
* Automation
* Admin features
* Production stability

---

# 🎯 Final Note

The main idea behind UIU Smart Assistant is simple:

> **Make useful academic tools available to UIU students from one familiar place — Telegram.**

Whether a student wants to calculate CGPA, estimate trimester fees, check academic information, access registration links, or get an approximate idea about scholarship chances, the goal is to make the process faster and easier.

---

<p align="center">
  <strong>🎓 UIU Smart Assistant</strong>
  <br>
  Built for UIU students.
</p>
