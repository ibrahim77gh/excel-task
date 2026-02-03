"""
Cashflow calculation service that replicates the Excel model logic.

The Excel model calculates Expected Death Outflow for employees based on:
- Employee data (birth date, joining date, salary)
- Assumptions (valuation date, discount rate, salary increase rate, retirement age)
- Lookup table for mortality probabilities (qx = death, px = survival)

For each employee, from current age to retirement:
- Future Salary = salary * (1 + salary_increase_rate)^years
- survival = px from lookup table
- death = qx from lookup table
- Expected Death Outflow = Future Salary * survival * death
"""

import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import BinaryIO


# Default probability lookup table (age -> (qx, px))
DEFAULT_PROBABILITY_TABLE = {
    20: (0.001152, 0.998848), 21: (0.001152, 0.998848), 22: (0.001152, 0.998848),
    23: (0.001152, 0.998848), 24: (0.001152, 0.998848), 25: (0.001413, 0.998587),
    26: (0.001491, 0.998509), 27: (0.001491, 0.998509), 28: (0.001491, 0.998509),
    29: (0.001492, 0.998509), 30: (0.001492, 0.998509), 31: (0.001492, 0.998509),
    32: (0.001491, 0.998509), 33: (0.001492, 0.998509), 34: (0.001492, 0.998509),
    35: (0.002290, 0.997710), 36: (0.002290, 0.997710), 37: (0.002290, 0.997710),
    38: (0.002290, 0.997710), 39: (0.002290, 0.997710), 40: (0.003211, 0.996789),
    41: (0.003211, 0.996789), 42: (0.003211, 0.996789), 43: (0.003211, 0.996789),
    44: (0.003211, 0.996789), 45: (0.004627, 0.995374), 46: (0.004748, 0.995252),
    47: (0.004748, 0.995252), 48: (0.004748, 0.995252), 49: (0.004748, 0.995252),
    50: (0.007059, 0.992941), 51: (0.007059, 0.992941), 52: (0.007059, 0.992941),
    53: (0.007059, 0.992941), 54: (0.007059, 0.992941), 55: (0.010286, 0.989714),
    56: (0.010286, 0.989714), 57: (0.010286, 0.989714), 58: (0.010286, 0.989714),
    59: (0.010286, 0.989714), 60: (0.000000, 1.000000), 61: (0.000000, 1.000000),
    62: (0.000000, 1.000000), 63: (0.000000, 1.000000), 64: (0.000000, 1.000000),
    65: (0.000000, 1.000000), 66: (0.000000, 1.000000), 67: (0.000000, 1.000000),
    68: (0.000000, 1.000000), 69: (0.000000, 1.000000), 70: (0.000000, 1.000000),
    71: (0.000000, 1.000000), 72: (0.000000, 1.000000), 73: (0.000000, 1.000000),
}


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")


def calculate_age(birth_date: datetime, valuation_date: datetime) -> int:
    """Calculate age in years (matching Excel's INT((valuation_date - birth_date + 1) / 365.25))."""
    days = (valuation_date - birth_date).days + 1
    return int(days / 365.25)


def get_probability(age: int, probability_table: dict) -> tuple:
    """Get death (qx) and survival (px) probabilities for a given age."""
    if age in probability_table:
        return probability_table[age]
    # If age not in table, use closest boundary
    if age < min(probability_table.keys()):
        return probability_table[min(probability_table.keys())]
    return probability_table[max(probability_table.keys())]


def process_cashflow(input_file: BinaryIO) -> tuple[str, int, int]:
    """
    Process the input CSV file and generate cashflow calculations.

    Expected CSV format:
    - First few rows: assumptions (key,value pairs)
    - Then: employee data with columns: emp_id, emp_name, date_birth, date_joining, salary

    Or simpler format:
    - Just employee data with default assumptions

    Returns:
        tuple: (output_csv_string, input_row_count, output_row_count)
    """
    content = input_file.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    lines = content.strip().split('\n')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    # Default assumptions
    valuation_date = datetime(2024, 12, 31)
    discount_rate = 0.0545
    salary_increase_rate = 0.05
    retirement_age = 60
    probability_table = DEFAULT_PROBABILITY_TABLE.copy()

    # Parse the file - detect format
    employees = []
    assumptions_found = False

    for i, row in enumerate(rows):
        if not row or all(not cell.strip() for cell in row):
            continue

        # Check for assumptions section
        if len(row) >= 2:
            key = row[0].strip().lower()
            if key == 'valuation_date':
                valuation_date = parse_date(row[1])
                assumptions_found = True
                continue
            elif key == 'discount_rate':
                discount_rate = float(row[1])
                assumptions_found = True
                continue
            elif key == 'salary_increase_rate':
                salary_increase_rate = float(row[1])
                assumptions_found = True
                continue
            elif key == 'retirement_age':
                retirement_age = int(row[1])
                assumptions_found = True
                continue

        # Check for header row
        if len(row) >= 5:
            first_cell = row[0].strip().lower()
            if first_cell in ('emp_id', 'employee_id', 'id'):
                continue  # Skip header

            # Try to parse as employee data
            try:
                emp_id = row[0].strip()
                emp_name = row[1].strip()
                date_birth = parse_date(row[2])
                date_joining = parse_date(row[3])
                salary = float(row[4].replace(',', ''))

                employees.append({
                    'emp_id': emp_id,
                    'emp_name': emp_name,
                    'date_birth': date_birth,
                    'date_joining': date_joining,
                    'salary': salary,
                })
            except (ValueError, IndexError):
                continue

    input_row_count = len(employees)

    # Calculate cashflows for each employee
    output_rows = []

    for emp in employees:
        current_age = calculate_age(emp['date_birth'], valuation_date)

        # Project from current age to retirement
        future_salary = emp['salary'] * (1 + salary_increase_rate)  # First year projection

        for age in range(current_age, retirement_age):
            qx, px = get_probability(age, probability_table)

            expected_death_outflow = future_salary * px * qx

            output_rows.append({
                'emp_id': emp['emp_id'],
                'emp_name': emp['emp_name'],
                'age': age,
                'future_salary': round(future_salary, 2),
                'survival_prob': px,
                'death_prob': qx,
                'expected_death_outflow': round(expected_death_outflow, 6),
            })

            # Project salary for next year
            future_salary = future_salary * (1 + salary_increase_rate)

    # Generate output CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write summary header
    writer.writerow(['Cashflow Calculation Results'])
    writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])

    # Write assumptions
    writer.writerow(['Assumptions'])
    writer.writerow(['valuation_date', valuation_date.strftime('%Y-%m-%d')])
    writer.writerow(['discount_rate', discount_rate])
    writer.writerow(['salary_increase_rate', salary_increase_rate])
    writer.writerow(['retirement_age', retirement_age])
    writer.writerow([])

    # Write calculation results
    writer.writerow(['Calculation Results'])
    writer.writerow(['emp_id', 'emp_name', 'age', 'future_salary', 'survival_prob', 'death_prob', 'expected_death_outflow'])

    for row in output_rows:
        writer.writerow([
            row['emp_id'],
            row['emp_name'],
            row['age'],
            row['future_salary'],
            row['survival_prob'],
            row['death_prob'],
            row['expected_death_outflow'],
        ])

    output_row_count = len(output_rows)

    return output.getvalue(), input_row_count, output_row_count
