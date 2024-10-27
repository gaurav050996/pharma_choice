# Pharma Choice Web App

Pharma Choice Web App is a Django-based application designed to manage pharmacy stock and allow users to purchase drugs online. The project includes an **Admin Dashboard** for stock management and a **User Interface** for ordering drugs.

## Features

- **Admin Dashboard**: Manage drugs, inventory, prices, and discounts.
- **User Shop**: Users can browse available drugs, view prices, and place orders.
- **Inventory Management**: Stock updates automatically when orders are placed.
- **Search and Filter**: Users can search for drugs and filter by category.

---

## Prerequisites

- **Python 3.x**: Ensure you have Python 3 installed. You can download it from [Python’s website](https://www.python.org/downloads/).
- **Django**: The project is built with Django, which will be installed in the virtual environment.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pharma-choice.git
cd pharma-choice

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```

Admin Dashboard: Go to http://127.0.0.1:8000/admin-dashboard/ and log in using the superuser credentials.
User Shop: Go to http://127.0.0.1:8000/drugs/ to browse and order drugs.
