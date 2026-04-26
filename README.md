# AI-Based Smart Study Planner

> An AI-powered study schedule optimizer built with **Genetic Algorithms** — because your time deserves better than a random timetable.

---

## Overview

Students often struggle to balance multiple subjects, varying difficulty levels, and limited time. Manual planning leads to inefficient time allocation and poor prioritization.

The **AI-Based Smart Study Planner** solves this by automatically generating an **optimized, personalized study timetable** using a **Genetic Algorithm** — an AI technique inspired by natural evolution. The system iteratively improves schedules across generations, converging on the most balanced and efficient plan for you.

---

## Features

- Input your subjects, available hours, and priority/difficulty levels
- Generates an initial population of random schedules
- Applies Genetic Algorithm operations: **Selection → Crossover → Mutation**
- Evolves schedules over multiple generations for continuous improvement
- Outputs the best optimized timetable with highest fitness score
- Visualizes fitness improvement over generations
- Clean GUI built with Tkinter

---

## Technologies Used

| Category | Tool / Library |
|---|---|
| Language | Python |
| GUI | Tkinter |
| Visualization | Matplotlib |
| Algorithm | Genetic Algorithm (custom) |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/MuhammadShayanFaisal/AI-Smart-Study-Planner.git
cd AI-Smart-Study-Planner
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```

---

## Visualizations

The system provides two visual outputs:

- **Fitness Graph** — Shows how schedule quality improves across generations
- **Optimized Timetable** — Displays the final subject-to-time-slot allocation

---

## Target Users

| User | Benefit |
|---|---|
| Students | Get a balanced, AI-generated study plan |
| Teachers | Help guide students in effective scheduling |
| Self-Learners | Manage time efficiently across multiple topics |

---

## Project Structure

```
AI-Smart-Study-Planner/
│
├── main.py               # Entry point
├── genetic_algorithm.py  # Core GA logic
├── fitness.py            # Fitness function
├── gui.py                # Tkinter GUI
├── visualization.py      # Matplotlib graphs
├── requirements.txt      # Dependencies
└── README.md
```

---


