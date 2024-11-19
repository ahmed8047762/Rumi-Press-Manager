# Rumi Press Manager

A comprehensive book distribution and expense tracking system built for Rumi Press using Django and Chart.js.

## Features

- **Book Management**
  - Bulk import from Excel files
  - Automated data validation
  - Category management
  - ISBN standardization

- **Expense Tracking**
  - Distribution expense monitoring
  - Category-wise analysis
  - Historical trend tracking

- **Interactive Dashboard**
  - Daily expense & book count trends
  - Monthly performance overview
  - Category distribution visualization

## Tech Stack

- Django 4.2.16
- Bootstrap 5.3
- Chart.js
- Pandas
- SQLite (PostgreSQL-ready)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ahmed8047762/Rumi-Press-Manager.git
cd Rumi-Press-Manager
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start development server:
```bash
python manage.py runserver
```

## Usage

1. **Import Books**
   - Navigate to Import Books page
   - Upload Excel file with book data
   - Review import summary

2. **View Dashboard**
   - Monitor daily and monthly trends
   - Analyze category distributions
   - Track expense patterns

3. **Manage Categories**
   - Create/edit categories
   - View category statistics
   - Monitor category-wise expenses

## Excel Import Format

Required columns in the Excel file:
- ISBN
- Title
- Authors
- Publisher
- Published Date
- Category
- Distribution Expense

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Ahmed - [@ahmed8047762](https://github.com/ahmed8047762)

Project Link: [https://github.com/ahmed8047762/Rumi-Press-Manager](https://github.com/ahmed8047762/Rumi-Press-Manager)
