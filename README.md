# Conversational CRM Lead Intelligence Agent

An AI-powered conversational CRM agent that allows users to ask natural-language questions about lead data and receive accurate, database-grounded answers.

The system uses **LangChain**, **LangGraph**, **Groq LLM**, and **SQLite** to convert natural-language questions into SQL, execute them against CRM data, handle errors through a self-correction loop, and generate professional natural-language responses.

## Features

- Natural Language → SQL querying
- CRM scope classification
- Dynamic SQL generation
- Multi-table joins and aggregations
- SQL execution using SQLite
- Automatic SQL error detection and repair
- Multi-turn conversational context
- Partial-scope query handling
- Out-of-scope guardrails
- Natural-language answer generation
- Business-language interpretation

## CRM Database

The project contains eight CRM tables:

1. `leads`
2. `followups`
3. `prospects`
4. `walkin_stages`
5. `registrations`
6. `closed_leads`
7. `lead_remarks`
8. `call_recordings`

These tables represent the lead lifecycle from initial enquiry through follow-up, prospect qualification, walk-in, registration, and closure.

## Architecture

```text
User Question
     |
     v
+------------------+
|   Scope Check    |
+------------------+
     |
     +---------------- OUT_OF_SCOPE ----------------+
     |                                               |
     v                                               v
IN_SCOPE / PARTIAL_SCOPE                       Safe Response
     |
     v
+------------------+
|   Generate SQL   |
+------------------+
     |
     v
+------------------+
|   Execute SQL    |
+------------------+
     |
     +---------- Error ----------+
     |                           |
     |                           v
     |                    +-------------+
     |                    | Repair SQL  |
     |                    +-------------+
     |                           |
     |                           +-----> Execute Again
     |
   Success
     |
     v
+------------------+
| Generate Answer  |
+------------------+
     |
     v
Natural Language Response
```

## LangGraph Workflow

The application uses LangGraph to control the agent workflow.

Main stages:

```text
START
  |
scope_check
  |
  +--> out_of_scope --> END
  |
generate_sql
  |
execute_sql
  |
  +--> repair_sql --> execute_sql
  |
generate_answer
  |
 END
```

The repair cycle allows the agent to recover automatically when generated SQL contains schema or SQL errors.

## Scope Guardrail

Before SQL generation, the agent determines whether the question can be answered using the CRM database.

### In-Scope Example

```text
How many new leads came from LinkedIn and Meta Ads in the last 14 days?
```

### Out-of-Scope Example

```text
What is the weather today?
```

The system does not generate SQL for unrelated questions.

It also prevents unsupported CRM attributes such as employee salary, bonus, exam marks, or grades from being invented.

## Partial-Scope Queries

The agent can answer the supported portion of a mixed question while identifying unavailable information.

Example:

```text
Show the registration fee for Java students and their final exam grade.
```

The CRM contains registration and fee information but does not contain final exam grades.

The agent therefore retrieves the available registration information and states that exam-grade information is unavailable.

## Multi-Turn Conversation

The system maintains conversational context between questions.

Example:

```text
User:
Show students registered under trainer Vikram.

Agent:
Returns the students registered under Vikram.

User:
How many of them paid through UPI or EMI?

Agent:
There are 3 registrations that match the criteria.
```

The second question preserves the previous `trainer_assigned = 'Vikram'` context.

## Business-Language Interpretation

The agent can translate CRM-oriented business language into database conditions.

Example:

```text
Which of our warmest leads are slipping through the cracks?
```

The agent interprets:

```text
warmest leads
→ Hot or Warm prospects

slipping through the cracks
→ overdue follow-up OR no recent call activity
```

The resulting SQL is dynamically generated from the database schema.

## Automatic SQL Self-Correction

If SQL execution fails, the error is returned to a LangGraph repair node.

The repair node receives:

- Original user question
- Failed SQL
- Database error
- Database schema

It generates corrected SQL and retries execution.

A retry limit prevents infinite correction loops.

## Example Questions

```text
How many new leads came from LinkedIn and Meta Ads in the last 14 days?

How many total leads are assigned to counselor Priya Sharma, and how many are new leads?

Compare closures due to competitor and high fees.

Show B2C prospects with budget above 40000 who prefer weekend offline classes.

Which Chennai walk-ins attended a demo but have not registered?

Show registered students with pending fees above 20000 and their batch start dates.

Which leads had a Hesitant or Negative last follow-up and are overdue?

What is the walk-in conversion rate for each counselor?

Show fee-high closures with calls longer than 5 minutes.

Which leads received supervisor feedback but had no calls in the last 7 days?

Which of our warmest leads are slipping through the cracks?

Show students registered under trainer Vikram.
How many of them paid through UPI or EMI?
```

## Project Structure

```text
crm_lead_agent/
│
├── crm_agent.py       # LangGraph conversational CRM agent
├── database.py        # Database schema creation
├── seed_data.py       # Sample CRM data
├── check_db.py        # Database verification
├── crm.db             # SQLite CRM database
├── requirements.txt   # Python dependencies
├── .env.example       # API key template
├── .gitignore         # Files excluded from Git
└── README.md
```

## Installation

### 1. Clone or download the project

Navigate to the project directory:

```bash
cd crm_lead_agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_actual_groq_api_key
```

Never commit the `.env` file to a public repository.

### 5. Create the database

```bash
python database.py
```

### 6. Seed sample CRM data

```bash
python seed_data.py
```

Run the seeding script only when initializing a fresh database to avoid duplicate sample records.

### 7. Run the CRM Agent

```bash
python crm_agent.py
```

The terminal will display:

```text
========================================
   CRM LEAD INTELLIGENCE AGENT
========================================
Ask me questions about CRM lead data.
Type 'exit' to stop.

You:
```

Type natural-language CRM questions directly into the terminal.

To stop:

```text
exit
```

## Technology Stack

- Python
- LangChain
- LangGraph
- Groq LLM
- SQLite
- python-dotenv

## Key Design Principles

The project focuses on:

- Database-grounded answers
- Dynamic SQL rather than predefined query templates
- Preservation of user filters
- Safe scope handling
- Schema-aware SQL generation
- Automatic recovery from SQL errors
- Conversational context across turns
- Prevention of hallucinated CRM information

## Security

API credentials are stored in `.env`.

The repository includes `.env.example` as a template and `.gitignore` prevents the real `.env` file from being committed.

## Author

Swathi P.