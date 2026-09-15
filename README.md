# 🤖 AI-Powered Daily Aptitude Practice Agent

An automated AI-powered learning agent that generates a fresh daily aptitude and placement-practice quiz, validates the questions, stores them in Supabase, and delivers them directly to a Telegram group.

The system is designed for **daily practice with friends** and requires no laptop/server to remain online.

---

## 🚀 What This Project Does

Every day, the system automatically:

1. Selects a practice topic
2. Generates 5 AI-powered multiple-choice questions using Google Gemini
3. Creates exactly:
   - 🟢 1 Easy question
   - 🟡 2 Moderate questions
   - 🔴 2 Hard questions
4. Validates the generated quiz
5. Performs additional AI quality checking for logical-reasoning questions
6. Stores the quiz and questions in Supabase
7. Sends the quiz automatically to a Telegram group
8. Allows users to submit their answers
9. Calculates the score automatically
10. Stores user submissions and results

---

## 🧠 Topics

The project is designed for placement and competitive-exam preparation across:

### Aptitude
- Percentages
- Profit & Loss
- Time & Work
- Time, Speed & Distance
- Ratio & Proportion
- Averages
- Probability
- Permutations & Combinations
- Number Systems
- And more

### Logical Reasoning
- Syllogisms
- Coding-Decoding
- Blood Relations
- Directions
- Seating Arrangement
- Series
- Logical Deduction
- And more

### DSA
- Binary Search
- Arrays
- Sorting
- Searching
- Complexity
- Data Structures
- Algorithms
- And more

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   GitHub Actions    │
                    │   Daily Scheduler   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Topic Rotation   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Google Gemini    │
                    │   Quiz Generation   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Quiz Validation &   │
                    │   Quality Review    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Supabase       │
                    │ Quiz + Questions +  │
                    │    Submissions      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Telegram      │
                    │    Daily Quiz       │
                    └──────────┬──────────┘
                               │
                         User Answers
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Telegram Webhook    │
                    │ Answer Processing   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Score Calculation   │
                    │ & Result Delivery   │
                    └─────────────────────┘
