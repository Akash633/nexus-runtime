# API Specification

## Purpose

This document defines all REST APIs exposed by Nexus Runtime.

These APIs allow the frontend dashboard, AI runtime, and monitoring services to communicate securely.

---

# Authentication APIs

## Register

POST /api/v1/auth/register

Description

Create a new user account.

---

## Login

POST /api/v1/auth/login

Description

Authenticate user and return JWT token.

---

## Logout

POST /api/v1/auth/logout

Description

Invalidate current session.

---

# User APIs

## Get Profile

GET /api/v1/users/profile

Description

Returns authenticated user information.

---

# Project APIs

## Create Project

POST /api/v1/projects

Description

Creates a new AI project.

---

## Get Projects

GET /api/v1/projects

Description

Returns all projects.

---

# Task APIs

## Create Task

POST /api/v1/tasks

Description

Creates a new AI task.

---

## Get Task

GET /api/v1/tasks/{task_id}

Description

Returns task details.

---

## Execute Task

POST /api/v1/tasks/{task_id}/execute

Description

Starts Runtime execution.

---

# Runtime APIs

## Runtime Decision

GET /api/v1/runtime/decision/{task_id}

Description

Returns why ARI selected a specific AI model.

---

## Runtime Status

GET /api/v1/runtime/status

Description

Returns current runtime health.

---

# Agent APIs

## List Agents

GET /api/v1/agents

Description

Returns all registered AI providers.

---

## Agent Health

GET /api/v1/agents/health

Description

Returns live health information.

---

# Analytics APIs

## Dashboard

GET /api/v1/dashboard

Description

Returns runtime statistics.

---

## Metrics

GET /api/v1/metrics

Description

Returns latency, cost, reliability and execution statistics.

---

# Monitoring APIs

## Logs

GET /api/v1/logs

Description

Returns runtime logs.

---

## Audit History

GET /api/v1/audit

Description

Returns complete execution history.