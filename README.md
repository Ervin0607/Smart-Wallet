# Smart Wallet with Budget Guardian 🛡️💳

## Overview
**Smart Wallet with Budget Guardian** is a robust, database-driven personal finance management application. Unlike standard digital wallets, this system goes beyond basic transactions; it is engineered to enforce financial discipline through active monitoring of global assets and liabilities. 

The application empowers users to maintain a digital wallet, execute real-time transactions, simulate cryptocurrency investments, and strictly track monthly spending against self-defined budgets using automated backend database logic.

## 🚀 Key Features
* **Digital Wallet & Payments:** Securely maintain a digital balance and perform real-time transactions.
* **Budget Guardian System:** Employs automated **MySQL database triggers** to rigorously track monthly spending and alert users when they approach or exceed self-defined budget thresholds.
* **Asset & Liability Monitoring:** A comprehensive dashboard that actively monitors and visualizes the user's global financial health.
* **Crypto Investment Simulation:** Allows users to simulate cryptocurrency purchases and track portfolio value over time without real financial risk.
* **Responsive Dashboard:** An intuitive, dynamic UI built for seamless navigation and clear data visualization.

## 🛠️ Technology Stack
* **Backend:** Python, Flask
* **Database:** MySQL (utilizing stored procedures and triggers)
* **Frontend:** HTML5, CSS3, JavaScript
* **Version Control:** Git & GitHub

## ⚙️ Installation & Setup

To run this application locally, ensure you have Python 3.x and MySQL Server installed on your machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/YourUsername/Smart-Wallet-Budget-Guardian.git](https://github.com/YourUsername/Smart-Wallet-Budget-Guardian.git)
cd Smart-Wallet-Budget-Guardian
```

### 2. Set Up the Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Configuration

1. Open your MySQL command line or workbench.
2. Create a new database (e.g., smart_wallet_db).
3. Execute the provided SQL schema file to set up the tables, relationships, and custom triggers.

```bash
SOURCE database_schema.sql;
```

Update the database connection credentials in your Flask application (in config.py).

### 5. Run the Application
```bash
flask run
```
The application will be accessible at http://localhost:5000 in your web browser.
