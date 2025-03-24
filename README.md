# Expense Tracker Monorepo

A personal expense-tracking application built with **Flask** (MongoDB backend) and React/TypeScript frontend, intended for local usage or small-scale deployments.

---

## Contents

- [Expense Tracker Monorepo](#expense-tracker-monorepo)
  - [Contents](#contents)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
    - [1. Clone and Install Dependencies](#1-clone-and-install-dependencies)
    - [2. Environment Variables](#2-environment-variables)
    - [3. Start MongoDB](#3-start-mongodb)
    - [4. Run the Backend (Flask)](#4-run-the-backend-flask)
    - [5. Run the frontend (nextjs)](#5-run-the-frontend-nextjs)
  - [Usage](#usage)
  - [Routes and APIs](#routes-and-apis)

---

## Features

1. **User Authentication**: Sign up, log in, log out, and account deletion via Flask-Login.  
2. **MongoDB** storage:
   - **Users**: Store user credentials and profiles.
   - **Categories**: List of categories and subcategories (embedded or separate, depending on your configuration).
   - **Expenses**: Each expense references a user and has a date, cost, and category info.
3. **React / Next.js 15** front end:
   - Dashboard with charts (Pie and Stacked Bar) via `react-chartjs-2`.
   - Fully **no jQuery** approach using **React-Bootstrap** modals.
4. **Charts**: Display aggregated expense data over time by category.
5. **Responsive UI** with **Bootstrap** styling.

---

## Project Structure

```sh
expense-tracker/
├── README.md
├── backend/
│   ├── run.py
│   ├── .env
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── routes/
│       │   ├── auth.py
│       │   ├── main.py
│       │   └── expenses.py
│       ├── models/
│       │   ├── users.py
│       │   ├── expense.py
│       │   └── ...
│       ├── utils/
│       │   ├── mongodb_connector.py
│       │   ├── _password_utils.py
│       │   ├── _logger.py
│       │   └── _constants.py
│       └── ...
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── login/
    │   │   └── page.tsx
    │   ├── signup/
    │   │   └── page.tsx
    │   ├── dashboard/
    │   │   └── page.tsx
    │   ├── components/
    │   │   ├── AddExpenseModal.tsx
    │   │   ├── EditExpenseModal.tsx
    │   │   └── charts/
    │   │       ├── PieChart.tsx
    │   │       └── StackedBarChart.tsx
    │   └── globals.css
    └── ...
```

- **backend/**  
  - **Flask** application with MongoDB integration.  
  - `app/__init__.py` sets up the Flask app and initializes the MongoDB client.  
  - `routes/` contains the Flask Blueprints (`auth.py`, `main.py`, `expenses.py`).  
  - `models/` or `utils/` for Pydantic models, database logic, etc.

- **frontend/**  
  - **Next.js** 13 app router under `app/`.  
  - Pages: `page.tsx` (Home), `login/page.tsx`, `signup/page.tsx`, and `dashboard/page.tsx`.  
  - Components: Modal components, chart components, etc.

---

## Prerequisites

1. **Python 3.9+**  
2. **Node.js 16+** (for Next.js)  
3. **MongoDB** installed or a remote connection (e.g. Atlas).  
4. **pip** or **poetry** to install Python dependencies.  
5. **npm** or **yarn** to install Node dependencies.

---

## Getting Started

### 1. Clone and Install Dependencies

```sh
git clone https://github.com/YourUsername/expense-tracker.git
cd expense-tracker
```

- Backend:

```sh
cd backend
pip install -r requirements.txt
```

- Frontend:

```sh
cd ../frontend
npm install
```

### 2. Environment Variables

Create a .env file in backend/ (and optionally in frontend/ if needed). Example:

```sh
SECRET_KEY=YourFlaskSecretKey
MONGODB_URI=mongodb://localhost:27017
```

### 3. Start MongoDB

Ensure MongoDB is running locally or connect to your remote cluster (adjust MONGODB_URI accordingly).

### 4. Run the Backend (Flask)

```sh
cd ../backend
python run.py
```

By default, it starts on http://localhost:8000.

### 5. Run the frontend (nextjs)

```sh
cd ../frontend
npm run dev
```

This starts Next.js on http://localhost:3000.
The app calls the Flask backend at http://localhost:8000.

---

## Usage

1. Sign Up at http://localhost:3000/signup.
2. Log In at http://localhost:3000/login.
3. Dashboard: View your expenses, add new expenses, edit or delete them.
4. Charts: Pie chart by category, stacked bar chart by category over time.

---

## Routes and APIs

- Backend (Flask):
  - POST /signup : Create a new user.
  - POST /login : Authenticate a user (username + password).
  - POST /logout : Log out the current user.
  - GET /dashboard : Returns JSON data of expenses & categories for the logged-in user.
  - POST /add_expense : Create a new expense entry.
  - POST /edit_expense/<expense_id> : Update an existing expense.
  - DELETE /delete_expense/<expense_id> : Delete an expense.
  - DELETE /delete_user/<username_> : Delete the user’s account.

- Frontend (Next.js):
  - / : Home page (index).
  - /login : Login page.
  - /signup : Register new user.
  - /dashboard : Main expense overview and charts.
