# Decision Scoring Algorithm

## Purpose

The Decision Engine evaluates every available AI provider and calculates a final score.

The provider with the highest score is selected.

---

# Inputs

Each provider contains:

- Cost
- Latency
- Reliability
- Trust Score
- Availability
- Historical Success Rate
- Security Level

---

# Weight Distribution

Cost = 20%

Latency = 20%

Reliability = 20%

Historical Success = 15%

Trust Score = 10%

Availability = 10%

Security = 5%

Total = 100%

---

# Final Score

Final Score =

(Cost × 0.20)

+

(Latency × 0.20)

+

(Reliability × 0.20)

+

(Historical Success × 0.15)

+

(Trust × 0.10)

+

(Availability × 0.10)

+

(Security × 0.05)

---

# Example

GPT

Cost Score = 60

Latency = 90

Reliability = 99

History = 95

Trust = 95

Availability = 99

Security = 100

Final Score

= 88.6

Claude

Final Score

= 91.4

Gemini

Final Score

= 82.1

Selected

Claude

---

# Tie Breaking

If two providers have the same score

↓

Choose lower latency

↓

If still equal

↓

Choose lower cost

↓

If still equal

↓

Choose higher trust

---

# Failure Handling

Selected Provider

↓

Health Check

↓

Success

↓

Execute

↓

Failure

↓

Select next highest score

↓

Retry

↓

Update historical score

---

# Continuous Learning

After every request

Update

- Success Rate

- Average Latency

- Cost

- Trust

This continuously improves future decisions.