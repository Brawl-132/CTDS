# CTDS Food Ordering System

A web-based food ordering system built with FastAPI, SQLModel, and Dash for data visualization. The system allows students to place food orders via roll number authentication, provides admin views for order management, and includes automated backup functionality.

## Features

- **Student Interface**: Login with roll number to view and place food orders
- **Admin Dashboard**: View all orders with filtering and export capabilities
- **Individual Reports**: View order history for specific roll numbers
- **Data Visualization**: Interactive Dash dashboard showing order statistics
- **Automated Backups**: Periodic database backups with manual trigger option
- **Responsive Design**: Works on desktop and mobile devices
- **Logging**: Comprehensive logging for application, database, and backup activities

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **Database**: SQLModel (ORM) with SQLite/MySQL fallback
- **Frontend**: HTML/CSS/Jinja2 templates
- **Data Visualization**: Plotly Dash
- **Data Processing**: Pandas
- **Environment**: Python 3.8+
- **Dependencies**: See `requirements.txt`

## Project Structure

```
CTDS/
├── main.py                            # Main FastAPI application
├── models.py                          # Database models (Order)
├── database.py                        # Database connection and initialization
├── config.py                          # Application settings
├── simple_logging.py                  # Logging configuration
├── backup.py                          # Backup functionality
├── requirements.txt                   # Python dependencies
├── .env                               # Environment variables
├── static/                            # Static assets (CSS, JS, images)
│   └── photos/                        # Student photos (named by rollno.jpg)
├── templates/                         # HTML templates
│   ├── admin.html                     # Admin order view
│   ├── aup.html                       # Order form
│   ├── backup.html                    # Backup trigger page
│   ├── home.html                      # Home page
│   ├── individualreport.html          # Individual order report
│   ├── individualreportlogin.html     # Report login
│   ├── login.html                     # Login page
│   ├── order_success.html             # Order confirmation
│   └── user.html                      # User profile page
└── logs/                              # Log files (generated)
    ├── app.log                        # Application logs
    ├── database.log                   # Database logs
    └── backup.log                     # Backup logs
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CTDS
   ```

2. **Set up Python environment**
   Choose your preferred method:
   
   **Standard venv:**
   ```bash
   python -m venv venv
   # Activate:
   # macOS/Linux: source venv/bin/activate
   # Windows: venv\Scripts\activate
   ```
   
   **Using uv (faster alternative):**
   ```bash
   # Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv
   # Activate:
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\.venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Standard pip:
   pip install -r requirements.txt
   
   # OR with uv:
   uv pip install -r requirements.txt
   ```

4. **Configure environment**
   Create a `.env` file in the project root. For SQLite (default), you can leave this file empty or explicitly set:
   
   ```bash
   DATABASE_URL=sqlite:///orders.db
   ```
   
   For MySQL configuration (Recomended), use:
   ```bash
   DATABASE_URL=mysql+pymysql://root:root@localhost:3306/baabu 
   MYSQLDUMP_PATH="C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqldump.exe"
   #These are just examples, please set the appropriate paths according to the systems
   MYSQL_USER="root"
   MYSQL_PASSWORD="root"
   MYSQL_DB="baabu"
   MYSQL_TABLE="order"
   BACKUP_INTERVAL=1800
   ```


5. **Prepare student data**
   - Create a `Rollno.xlsx` file in the root directory with the following columns:
     - `rollno`: Student roll number (string)
     - `studentName`: Full name of student
     - `residence`: Hostel/residence name
     - `occupancy`: Room type or occupancy details
   - Note: This file contains sensitive student information and should never be committed to version control (it's already in `.gitignore`)

6. **Prepare student photos (optional)**
   - Place student photos in `static/photos/` directory
   - Name each photo as `{rollno}.jpg` (e.g., `2021001.jpg`)

7. **Run the application**
   ```bash
   python main.py
   ```

   The application will initialize the database, start the server at http://localhost:8000, and begin automated backups if configured.

## Environment Variables

The application uses environment variables from `.env` for configuration:

**Key variables:**
- `DATABASE_URL` - Database connection (SQLite: `sqlite:///orders.db`, MySQL: SQLAlchemy format)
- `MYSQLDUMP_PATH` - Path to mysqldump (MySQL only)
- `MYSQL_USER`/`MYSQL_PASSWORD` - MySQL credentials
- `MYSQL_DB` - MySQL database name
- `MYSQL_TABLE` - Orders table name (MySQL only)
- `BACKUP_INTERVAL` - Backup interval in seconds (default: 1800)
- `DEBUG` - Enable debug mode (True/False)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

**Notes:**
- SQLite is used by default if `DATABASE_URL` is unset
- Never commit `.env` to version control (it's in `.gitignore`)
- The app will fall back to SQLite if MySQL is unavailable

## API Endpoints

### Authentication
- `GET /` - Login page
- `POST /login` - Process login with roll number

### Order Management
- `GET /home` - Home page after login
- `GET /order_form?rollno={rollno}` - Show order form for a student
- `POST /auc` - Submit food order

### Administration
- `GET /admin` - View all orders (admin interface)
- `GET /download` - Download orders as Excel file
- `GET /report_form` - Individual report login form
- `POST /report_form` - Submit roll number for individual report
- `GET /report/{rollno}` - View individual order report

### Utilities
- `GET /trigger-backup` - Manually trigger database backup
- `GET /dashboard/` - Access the Dash dashboard
- `GET /documentation` - View system documentation

## Database Model

The system uses a single `Order` model defined in `models.py`:

```python
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rollno: str = Field(index=True)  # Indexed for faster lookups
    
    # Food items with default quantities
    cheese_roll: int = 0
    paneer_tikka: int = 0
    schezwan_paneer: int = 0
    extra_cheese: int = 0
    normal_brownie: int = 0
    brownie_with_icecream: int = 0
    lime_juice: int = 0
    lemon_soda: int = 0
    margherita: int = 0
    peppy_paneer: int = 0
    farmhouse: int = 0
    choco_lava_cake: int = 0
    french_fries: int = 0
    cheese_nuggets: int = 0
    corn: int = 0
    spiral_potato: int = 0
    rabadi_kulfi: int = 0
    shahi_gulab: int = 0
    strawberry: int = 0
    choclate: int = 0
    pista_badam: int = 0
    malai_kulfi: int = 0
    
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## Menu Prices

Food item prices are defined in `main.py` as a dictionary:
- cheese_roll: 125
- paneer_tikka: 125
- schezwan_paneer: 125
- extra_cheese: 30
- normal_brownie: 60
- brownie_with_icecream: 80
- lime_juice: 20
- lemon_soda: 30
- margherita: 225
- peppy_paneer: 375
- farmhouse: 375
- choco_lava_cake: 180
- french_fries: 70
- cheese_nuggets: 70
- corn: 50
- spiral_potato: 70
- rabadi_kulfi: 70
- shahi_gulab: 70
- strawberry: 70
- choclate: 70
- pista_badam: 70
- malai_kulfi: 70

## Logging

The application uses three separate log files:
- `logs/app.log`: Application events (logins, orders, errors)
- `logs/database.log`: Database operations and connections
- `logs/backup.log`: Backup task activities

Log rotation is configured to prevent excessive disk usage.

### Log Configuration
All loggers are configured in `simple_logging.py` with the following settings:
- App logger: 10 MB max size, 3 backup files
- Database logger: 20 MB max size, 2 backup files  
- Backup logger: 5 MB max size, 5 backup files

Log format: `%(asctime)s - %(levelname)s - %(message)s`

## Backup System

The system includes automated database backups:
- Configurable interval (default: 30 minutes)
- Uses `mysqldump` for MySQL databases
- Falls back to file copy for SQLite
- Manual backup can be triggered via `/trigger-backup` endpoint
- Backup files are stored in the root directory with timestamps

## Dashboard

The Dash dashboard (`/dashboard/`) provides:
- Real-time updating bar chart of ordered items
- Automatic refresh every 10 seconds
- Visual representation of popular food items
- Responsive design
