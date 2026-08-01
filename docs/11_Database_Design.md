# Database Design

## Purpose

The database stores all runtime information required for intelligent decision making.

Instead of simply storing users, Nexus Runtime stores execution history, agent performance, runtime metrics, trust scores, and learning data.

---

# Main Tables

## Users

Stores user accounts.

Fields

- user_id
- name
- email
- password_hash
- role
- created_at

---

## Agents

Stores every AI provider.

Fields

- agent_id
- provider_name
- model_name
- endpoint
- api_key_reference
- status
- created_at

---

## Tasks

Stores every incoming request.

Fields

- task_id
- user_id
- task_type
- prompt
- priority
- budget_limit
- security_level
- created_at

---

## Runtime Decisions

Stores which AI was selected.

Fields

- decision_id
- task_id
- selected_agent
- confidence_score
- reason
- fallback_agent
- decision_time

---

## Executions

Stores execution results.

Fields

- execution_id
- task_id
- agent_id
- latency
- execution_cost
- success
- response_time
- created_at

---

## Agent Metrics

Stores continuously updated AI statistics.

Fields

- metric_id
- agent_id
- average_latency
- average_cost
- success_rate
- trust_score
- availability

---

## Learning History

Stores learning information.

Fields

- learning_id
- agent_id
- previous_score
- updated_score
- learning_reason
- updated_at

---

# Relationships

One User

↓

Many Tasks

↓

One Runtime Decision

↓

One Selected Agent

↓

One Execution

↓

Metrics Updated

↓

Learning History Updated

---

# Benefits

- Historical Analysis

- Runtime Learning

- Trust Calculation

- Performance Monitoring

- Failure Analysis

- Dashboard Analytics

- AI Optimization