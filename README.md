# Income & Expense Tracker

## Flask + SQLAlchemy ORM

A modern and extensible Income & Expense Tracker built with Flask and SQLAlchemy, designed to help users record, organize, and analyze their financial activities using a clean relational database structure.

This project is ideal for learning full-stack backend development, database relationships, and dashboard-driven financial reporting.

## Features
### User Management
- Role-based user accounts (Admin / User).
- Secure authentication system.
- Each user owns their financial records.

### Profile Management
- One-to-one relationship between User and Profile.
- Profile avatar and personal information.

### Income & Expense Tracking
- Classify transactions as Income or Expense.
- Assign categories and descriptions.
- Store amounts with timestamps.
- Link all records to individual users.

## Tech Stack
* Backend:   Flask 
* ORM:       Flask-SQLAlchemy                  
* Database:  SQLite 
* Forms:     WTForms and Flask-WTF  
* Charts:    Chart.js                    
* UI         Bootstrap  

## Example Use Cases
- Track monthly income vs expenses.
- Generate category-based summaries.
- Build interactive financial dashboards.
- Export reports to PDF and Excel.
- Apply role-based access control.
- Extend to multi-tenant finance systems.

## Setup Instructions
1. Clone the repository:
 ```bash
https://github.com/Owaboye/IncomeExpenseTracker.git
```
2. Navigate into the project folder:
 ```bash
cd income-expense-tracker
```
3. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```
4. Install dependencies
```bash
pip install -r requirements.txt
```
5. Run the application
```bash
python run.py
```

## Future Enhancements
- JWT authentication
- Email verification
- Role-based dashboards
- API integration
- Mobile UI

## License
This project is open-source and free to use for learning and development.