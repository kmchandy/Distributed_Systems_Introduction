# Distributed Systems Introduction

A working draft of a course on basic concepts of distributed systems. The course includes examples from different domains including Large Language Model (LLM) agents.

This repository provides weekly modules with interactive Colab notebooks built using tools such as **CrewAI**, 
a framework for building distributed LLM agents

---

## 📚 Course Goals

- Introduce distributed systems concepts.
- Provide examples from different domains.

---

## 🗂️ Repository Structure

```
Distributed_Systems_Introduction_Draft/
├── README.md
├── LICENSE
├── requirements.txt
├── week1/
│   └── week1_inbox_summarizer_crewai.ipynb
├── week2/
│   └── (coming soon)
```
---

## 🗂️  License

This course material is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to use, adapt, and redistribute — even for commercial purposes — with proper attribution.

---

## 📦 Requirements

- Python 3.10+
- Google Colab or Jupyter Notebook
- Install CrewAI:
```bash
pip install crewai
```
---

## COURSE OUTLINE -- DRAFT

---

## 📬 Week 1: Introduction to agents, states, and messages with a simple example.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/kmchandy/distributed-systems-course/blob/main/week1/week1_inbox_summarizer_crewai.ipynb) 

In this lab, students:
- Build a simple **Crew** of two agents.
- Use a `Summarizer` to analyze a set of mock emails.
- Use a `Planner` to generate suggested actions.
- Learn how CrewAI distributes responsibility across agents.

---
