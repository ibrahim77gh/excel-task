# Cashflow Calculator

A Django web application that converts Excel-based financial calculations into a web interface. The application calculates Expected Death Outflow for employees based on actuarial data.

## Features

- Upload CSV files with employee data and calculation assumptions
- Process employee data with configurable parameters (discount rate, salary increase rate, retirement age)
- Calculate expected death outflows using mortality probability tables
- Download detailed output CSV with projected cashflows
- Track execution history with status monitoring

## Requirements

- Python 3.10+
- Django 5.0+

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd excel-task
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Open your browser and navigate to `http://127.0.0.1:8000/`

## Usage

### Input CSV Format

The input CSV file should contain two sections:

**Assumptions Section:**
```csv
Assumptions
Valuation Date,2024-12-31
Discount Rate,0.07
Salary Increase Rate,0.03
Retirement Age,60
```

**Employee Data Section:**
```csv
Employee Data
Employee ID,Name,Date of Birth,Date of Joining,Annual Salary
E001,John Doe,1990-01-15,2015-06-01,50000
E002,Jane Smith,1985-07-20,2010-03-15,65000
```

See `sample_input.csv` for a complete example.

### Output

The application generates a detailed CSV containing:
- Employee information
- Age and service calculations
- Yearly projections until retirement including:
  - Projected salary
  - Discount factor
  - Survival probability (px)
  - Death probability (qx)
  - Expected death outflow

## Project Structure

```
excel-task/
├── calculator/              # Main Django app
│   ├── models.py           # Execution tracking model
│   ├── views.py            # HTTP request handlers
│   ├── services.py         # Core calculation logic
│   ├── urls.py             # URL routing
│   └── templates/          # HTML templates
├── excel_calculator/        # Django project config
│   ├── settings.py         # Project settings
│   └── urls.py             # Root URL config
├── manage.py               # Django CLI
├── requirements.txt        # Python dependencies
└── sample_input.csv        # Example input file
```

## License

This project is for demonstration purposes.
