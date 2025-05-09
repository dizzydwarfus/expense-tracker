# Expense Tracker Backend

## Overview
The backend of the Expense Tracker application is built using Go and provides a RESTful API for managing expenses. It interacts with a MongoDB database to store and retrieve expense data.

## To-Dos

- [ ] Create data models for expenses, categories, subcategories, and users.
- [ ] Implement authentication and authorization for users.
- [ ] Implement endpoints
  - [ ] dashboard data (GET /api/v1/dashboard)
  - [ ] expense data (GET /api/v1/expenses)
    - [ ] add expense (POST /api/v1/expenses/add)
    - [ ] edit expense (PUT /api/v1/expenses/edit)
    - [ ] delete expense (DELETE /api/v1/expenses/delete)
    - [ ] get categories (GET /api/v1/expenses/categories)
    - [ ] get subcategories (GET /api/v1/expenses/subcategories)
  - [ ] bank account endpoints
    - [ ] link bank account (POST /api/v1/bank/auth/link)
    - [ ] import transactions (POST /api/v1/bank/import)
    - [ ] callback URL for bank transactions (GET /api/v1/bank/callback)
    - [ ] refresh bank transactions (POST /api/v1/bank/auth/refresh)
  - [ ] auth endpoints
    - [ ] login (POST /api/v1/auth/login)
    - [ ] register (POST /api/v1/auth/register)
    - [ ] logout (POST /api/v1/auth/logout)
- [ ] Implement mongodb connection
- [ ] Implement middleware for logging and error handling.