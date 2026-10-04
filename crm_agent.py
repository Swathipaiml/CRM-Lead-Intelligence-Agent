from typing import TypedDict, Optional, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_community.utilities import SQLDatabase

DEBUG = False

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)
db = SQLDatabase.from_uri("sqlite:///crm.db")

class CRMState(TypedDict):
    question: str
    scope: Optional[str]

    supported_question: Optional[str]
    unsupported_part: Optional[str]

    conversation_history: Optional[str]

    sql_query: Optional[str]
    query_result: Optional[Any]
    error: Optional[str]
    final_answer: Optional[str]
    retry_count: int
    


def scope_check_node(state: CRMState):
    question = state["question"]
    history = state.get("conversation_history") or "No previous conversation."

    prompt = f"""
You are a scope classifier for a CRM Lead Management database.

The CRM contains:
- leads and counselors
- follow-ups and sentiments
- prospects, budgets and interest ratings
- walk-ins and demo attendance
- registrations
- course enrollment
- total, paid and pending fees
- payment modes
- trainers and batch dates
- closed leads and closure reasons
- lead remarks and supervisor feedback
- call recordings and transcript summaries
- prospect preferred batch type: weekday, weekend, fastrack
- prospect preferred class mode: offline, online, hybrid
- prospect budget
- prospect interest rating: Hot, Warm, Cold
- lead type: B2C or B2B
- call recordings including caller name, call duration in seconds, call status, transcript summary and call timestamp
- follow-up records including call status, discussion summary,
  sentiment and next follow-up date

- call recordings including caller name, call duration,
  call status, transcript summary and call timestamp

It DOES NOT contain unrelated information such as:
- weather
- politics
- general knowledge
- employee salary or bonus
- exams, marks or final exam grades

Previous conversation:
{history}

User question:
{question}

Classify it as exactly one of:

IN_SCOPE
PARTIAL_SCOPE
OUT_OF_SCOPE

Use PARTIAL_SCOPE when part of the question can be answered
from the CRM but another requested field is unavailable.
CRM lead source/channel information IS supported.
Examples include LinkedIn, Meta Ads, Google Ads, Website, and Referral.

Questions asking how many leads came from a particular source are IN_SCOPE.

Do not classify a question as OUT_OF_SCOPE merely because it contains
company/platform names such as LinkedIn, Meta Ads, Google Ads, or Website
when they are being used as CRM lead sources.

Return exactly 3 lines:

SCOPE: <classification>
SUPPORTED: <answerable part of the question, or NONE>
UNSUPPORTED: <unavailable part, or NONE>
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        text = response.content[0]["text"].strip()
    else:
        text = response.content.strip()

    scope = "OUT_OF_SCOPE"
    supported = "NONE"
    unsupported = "NONE"

    for line in text.splitlines():

        if line.startswith("SCOPE:"):
            scope = line.replace("SCOPE:", "").strip()

        elif line.startswith("SUPPORTED:"):
            supported = line.replace("SUPPORTED:", "").strip()

        elif line.startswith("UNSUPPORTED:"):
            unsupported = line.replace("UNSUPPORTED:", "").strip()

    return {
        "scope": scope,
        "supported_question": supported,
        "unsupported_part": unsupported
    }
def out_of_scope_node(state: CRMState):

    return {
        "final_answer":
        "Sorry, I can only answer questions related to CRM lead management data."
    }

def route_scope(state: CRMState):

    if state["scope"] == "IN_SCOPE":
        return "in_scope"

    if state["scope"] == "PARTIAL_SCOPE":
        return "in_scope"

    return "out_of_scope"

def generate_sql_node(state: CRMState):
    history = state.get("conversation_history") or "No previous conversation."
    if state["scope"] == "PARTIAL_SCOPE":
        question = state["supported_question"]
    else:
        question = state["question"]
    schema = db.get_table_info()

    prompt = f"""
You are an expert SQLite query generator for a CRM Lead Management system.

Database schema:

{schema}

Previous conversation:
{history}

Current user question:
{question}

CRM SEMANTIC RULES:
- "new leads" means leads where current_stage = 'newlead'.
- "follow-up leads" means current_stage = 'followup'.
- "prospects" may require the prospects table and/or current_stage = 'prospect'.
- "walk-ins" may require the walkin_stages table and/or current_stage = 'walkin'.
- "registered students" means registration information should come from the registrations table.
- "closed leads" means closure information should come from the closed_leads table.
- When the user mentions a CRM stage, do not ignore that stage condition.
- Preserve ALL filters mentioned in the user's question.
- Call duration is stored in call_recordings.call_duration_seconds.
- Convert durations expressed in minutes to seconds before filtering.
- Example: "more than 5 minutes" means call_duration_seconds > 300.
- "call summary" means call_recordings.transcript_summary.
- "caller name" means call_recordings.caller_name.
- "follow-up calls", "calls", "phone calls", and "call activity"
  refer to the call_recordings table.
- To determine whether a lead had a call within a time period,
  use call_recordings.call_timestamp.
- The followups table represents CRM follow-up records/tasks,
  not actual phone call activity.
- "zero calls" or "no calls" should check for the absence of
  matching call_recordings, preferably using NOT EXISTS or LEFT JOIN.
- "warmest leads" or "high-interest leads" means prospects with
  interest_rating IN ('Hot', 'Warm').
- "warmest leads" means BOTH Hot and Warm interest ratings.
  Hot leads must not be excluded.
- "slipping through the cracks" means a Hot/Warm prospect that needs
  attention because either:
  1. their next follow-up date is overdue, OR
  2. they have had no call/contact in the last 7 days.

- For overdue follow-up, use followups.next_followup_date < date('now').

- For no recent call/contact, check call_recordings.call_timestamp
  and determine whether there is no call within the last 7 days.

- When multiple conditions are connected by OR, preserve the OR logic
  rather than requiring every condition to be true.

IMPORTANT CONVERSATION RULE:
If the current question refers to previous results using words such as
"them", "those", "these", "they", or "those students",
you MUST preserve all relevant filters and conditions from the previous
conversation.

Example:
Previous question: Show students registered under trainer Vikram
Current question: How many of them paid through UPI or EMI?

The SQL MUST still include the condition:
trainer_assigned = 'Vikram'

Rules:
- Generate a valid SQLite query.
- Use ONLY tables and columns present in the schema.
- Do not invent columns.
- Use JOINs when information is stored across multiple tables.
- Resolve references in the current question using the previous conversation.
- Preserve relevant filters from previous turns.
- Return ONLY the SQL query.
- Do not explain anything.
- Do not use markdown code blocks.
- Use ALL rows returned in the database result unless the user explicitly
  asks for a limited number of records.

- Do not silently remove, filter, rank, or reinterpret rows returned
  by the SQL query.

- If the database result contains both Hot and Warm leads, include both.

- Never claim that a record is the "only" matching record unless that
  conclusion is directly supported by the complete database result.

- Preserve categorical values exactly as returned by the database.

- Do not rename database fields in a misleading way.
  For example:
  preferred_course means preferred course,
  budget means budget,
  interest_rating means interest rating.

- Base every factual statement in the answer ONLY on the database result
  and the user's question.
-The SQL query has already determined which records satisfy the user's
conditions.

Present ALL records from the database result accurately.
Do not perform another filtering step.

Before generating SQL:
- Identify every condition explicitly requested by the user.
- Map each condition to the correct schema column.
- Include every supported condition in the WHERE clause.
- Do not silently drop filters.
RESULT SELECTION RULES:
- Never use SELECT *.
- Select only the columns needed to answer the user's question.
- Always include human-readable identifying fields such as lead name when
  returning individual leads.
- Include the fields used to explain why a record matched when useful.

Examples of CRM mappings:
- "weekend" -> preferred_batch_type = 'weekend'
- "weekday" -> preferred_batch_type = 'weekday'
- "offline" -> preferred_class_mode = 'offline'
- "online" -> preferred_class_mode = 'online'
- "hybrid" -> preferred_class_mode = 'hybrid'
- "Hot", "Warm", or "Cold" -> interest_rating
- budget conditions -> prospects.budget
- "B2C" -> leads.lead_type = 'B2C'
- "B2B" -> leads.lead_type = 'B2B'
IMPORTANT:
The database result is already the final filtered result produced by SQL.

You MUST report every row in the database result.
You are NOT allowed to apply additional filtering yourself.

Do not decide that Hot, Warm, or any other returned category should be
excluded.

If 4 rows are returned, your answer must represent all 4 rows.
If 2 rows are returned, your answer must represent both rows.

The SQL/database decides which records match.
Your job is ONLY to explain the returned records accurately.
FILTER PRESERVATION RULE:

Extract EVERY explicit condition from the user's question before writing SQL.

Examples of conditions include:
- lead source
- current stage
- counselor
- trainer
- course
- lead type
- payment mode
- date/time range
- budget
- interest rating
- batch type
- class mode
- closure reason
- call duration

Every supported condition mentioned by the user MUST appear in the SQL.

Example:
Question:
"How many new leads came from LinkedIn and Meta Ads in the last 14 days?"

Required conditions:
1. "new leads" -> current_stage = 'newlead'
2. "LinkedIn and Meta Ads" -> source IN ('LinkedIn', 'Meta Ads')
3. "last 14 days" -> created_at >= datetime('now', '-14 days')

Do not omit any of these conditions.
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        sql_query = response.content[0]["text"].strip()
    else:
        sql_query = response.content.strip()

    # Clean markdown just in case
    sql_query = sql_query.replace("```sql", "")
    sql_query = sql_query.replace("```", "")
    sql_query = sql_query.strip()

    return {
        "sql_query": sql_query,
        "error": None
    }

def execute_sql_node(state: CRMState):

    sql_query = state["sql_query"]

    if DEBUG:
        print("\n[EXECUTING SQL]")
        print(sql_query)

    try:
        result = db.run(sql_query)

        return {
            "query_result": result,
            "error": None
        }

    except Exception as e:

        return {
            "query_result": None,
            "error": str(e)
        }

def route_after_execution(state: CRMState):

    if state["error"] is None:
        return "success"

    if state["retry_count"] >= 2:
        return "failed"

    return "retry"

def repair_sql_node(state: CRMState):

    question = state["question"]
    bad_sql = state["sql_query"]
    error = state["error"]

    schema = db.get_table_info()

    prompt = f"""
You are an expert SQLite developer.

A SQL query generated for a CRM system failed.

User question:
{question}

Database schema:
{schema}

Failed SQL:
{bad_sql}

Database error:
{error}

Correct the SQL query.

Rules:
- Use ONLY tables and columns from the schema.
- Fix the database error.
- Preserve the user's original intent.
- Return ONLY valid SQLite SQL.
- Do not explain anything.
- Do not use markdown code blocks.
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        corrected_sql = response.content[0]["text"].strip()
    else:
        corrected_sql = response.content.strip()

    corrected_sql = corrected_sql.replace(
        "```sql", ""
    ).replace(
        "```", ""
    ).strip()

    if DEBUG:
        print("\n[REPAIRED SQL]")
        print(corrected_sql)

    return {
        "sql_query": corrected_sql,
        "error": None,
        "retry_count": state["retry_count"] + 1
    }

def sql_failed_node(state: CRMState):

    return {
        "final_answer":
        "I couldn't complete the CRM query after multiple attempts."
    }
def generate_answer_node(state: CRMState):

    question = state["question"]
    result = state["query_result"]
    scope = state["scope"]
    unsupported_part = state["unsupported_part"]
    sql_query = state["sql_query"]

    prompt = f"""
You are a CRM assistant whose ONLY job is to describe the result
of an already-executed SQL query.

User question:
{question}

Executed SQL:
{sql_query}

Database result:
{result}

Scope:
{scope}

Unsupported part:
{unsupported_part}

IMPORTANT:
The SQL query has already decided which database records match
the user's request.

Therefore EVERY ROW in Database result is a matching record.

You MUST NOT:
- filter the rows again
- remove rows based on your own interpretation
- change Hot into Warm or Warm into Hot
- omit Hot rows when both Hot and Warm were returned
- invent information
- make claims not present in the result

You MUST:
- represent EVERY returned row in the answer
- preserve categorical values exactly
- use the database result as the source of truth
- clearly answer the user's question
- mention unavailable information if scope is PARTIAL_SCOPE

Before producing the answer, internally verify that the number of
individual records represented in your answer equals the number
of rows in the database result.

If the database result is empty, say that no matching CRM records
were found.
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        final_answer = response.content[0]["text"].strip()
    else:
        final_answer = response.content.strip()

    return {"final_answer": final_answer}

builder = StateGraph(CRMState)

builder.add_node("scope_check", scope_check_node)
builder.add_node("generate_sql", generate_sql_node)
builder.add_node("out_of_scope", out_of_scope_node)
builder.add_node("execute_sql", execute_sql_node)
builder.add_node("repair_sql", repair_sql_node)
builder.add_node("sql_failed", sql_failed_node)
builder.add_node("generate_answer", generate_answer_node)

builder.add_edge(START, "scope_check")

builder.add_conditional_edges(
    "scope_check",
    route_scope,
    {
    "in_scope": "generate_sql",
    "out_of_scope": "out_of_scope"
    }
)

builder.add_edge("generate_sql", "execute_sql")
builder.add_conditional_edges(
    "execute_sql",
    route_after_execution,
    {
        "success": "generate_answer",
        "retry": "repair_sql",
        "failed": "sql_failed"
    }
)

builder.add_edge("repair_sql", "execute_sql")
builder.add_edge("generate_answer", END)
builder.add_edge("sql_failed", END)


graph = builder.compile()

# ==========================================
# CRM CONVERSATIONAL CHAT INTERFACE
# ==========================================

print("\n========================================")
print("   CRM LEAD INTELLIGENCE AGENT")
print("========================================")
print("Ask me questions about CRM lead data.")
print("Type 'exit' to stop.\n")

conversation_history = ""

while True:

    question = input("You: ").strip()
    if question.lower().startswith("you:"):
        question = question[4:].strip()

    if question.lower() in ["exit", "quit", "bye"]:
        print("\nAgent: Goodbye!")
        break

    if not question:
        continue

    state = {
        "question": question,
        "scope": None,
        "supported_question": None,
        "unsupported_part": None,
        "conversation_history": conversation_history,
        "sql_query": None,
        "query_result": None,
        "error": None,
        "final_answer": None,
        "retry_count": 0
    }

    result = graph.invoke(state)

    answer = result["final_answer"]

    print("\nAgent:")
    print(answer)
    print()

    conversation_history += f"""
User: {question}
Assistant: {answer}
"""
