# My Expense Tracker

A comprehensive expense tracker that allows users to record and monitor their expenses. Built using Flask for the backend, interfacing with an SQL database.

## Folder Structure

```bash
│   .env
│   .gitignore
│   config.py
│   package-lock.json
│   package.json
│   README.md
│   run.py
│   tests.ipynb
│
├───app
│   │   sql_connector.py
│   │   _constants.py
│   │   __init__.py
│   │
│   ├───models
│   │   │   categories.py
│   │   │   expense.py
│   │   │   initdb.py
│   │   │   user.py
│   │   └   __init__.py
│   │
│   ├───routes
│   │   │   auth.py
│   │   │   expenses.py
│   │   │   main.py
│   │   └   __init__.py
│   │
│   ├───static
│   │   │   styles.css
│   │   │
│   │   └───js
│   │           main.js
│   │
│   ├───templates
│   │       dashboard.html
│   │       index.html
│   │       login.html
│   │       register.html
│   └       scripts.js
│
├───local_dev
│       add_expense.py
│       expenses.json
│       generate_secret_key.py
```

## Features

### Models
- **Category & SubCategory**: Represents the different types of expense categories and their respective subcategories. These are predefined and there are currently no functionality to add new categories/subcategories.
- **Expense**: Represents individual expenses, including details like description, category, date, and cost.
- **User**: Represents the users of the application, this is a simple authentication using a modified SHA256 encryption.

### Routes
#### Authentication (`auth.py`)
- **Login**: Authenticate users based on their username or email.
- **Signup**: Register a new user.
- **Logout**: Log out the currently authenticated user.
- **Delete User**: Allows users to delete their accounts.

#### Expense Management (`expenses.py`)
- **Add Expense**: Add a new expense record.
- **Delete Expense**: Remove an existing expense record.
- **Edit Expense**: Modify the details of an existing expense.
- **Get Subcategories**: Fetch subcategories for a given category.

#### Main (`main.py`)
- **Index**: The landing page.
- **Dashboard**: Display a view of user expenses, including graphical representations. New expenses added are immediately displayed. ***Currently line chart does not work as intended.***

