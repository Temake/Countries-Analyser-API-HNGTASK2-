# Country Currency & Exchange API

A RESTful API that fetches country data from external APIs, stores it in a database, and provides CRUD operations with exchange rate calculations.

## Features

- Fetch and cache country data with currency exchange rates
- CRUD operations for country records
- Filter countries by region or currency
- Sort by GDP, population, or name
- Automatic GDP estimation based on population and exchange rates
- Generate summary images with top countries
- Case-insensitive country name lookups

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (development) / MySQL (production)
- **ORM**: SQLModel
- **Image Processing**: Pillow
- **HTTP Client**: Requests

## Installation

### Prerequisites

- Python 3.13+
- pip or uv package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Temake/Countries-Analyser-API-HNGTASK2-.git
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install fastapi uvicorn sqlmodel mysqlclient pillow requests python-dotenv pydantic pydantic-settings
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration (see Environment Variables section)

6. **Run the application**
   ```bash
   uvicorn main:app --reload --port 9000
   ```

The API will be available at: `http://localhost:9000`

## Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite:///database.db

# For Production (MySQL)
# DATABASE_URL=mysql://username:password@host:port/database_name

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# External API URLs
COUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_RATE_API_URL=https://open.er-api.com/v6/latest/USD

# API Timeout (in seconds)
API_TIMEOUT=30
```

## API Endpoints

### 1. Refresh Country Data
```http
POST /countries/refresh
```
Fetches country data and exchange rates from external APIs, then caches in database.

**Response:**
```json
{
  "message": "Country data refreshed successfully."
}
```

**Error Response (503):**
```json
{
  "error": "External data source unavailable",
  "details": "Could not fetch data from REST Countries API"
}
```

---

### 2. Get All Countries
```http
GET /countries
```

**Query Parameters:**
- `region` (optional): Filter by region (e.g., `?region=Africa`)
- `currency` (optional): Filter by currency code (e.g., `?currency=NGN`)
- `sort` (optional): Sort results
  - `gdp_desc` / `gdp_asc`
  - `population_desc` / `population_asc`
  - `name_desc` / `name_asc`

**Example:**
```http
GET /countries?region=Africa&sort=gdp_desc
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1600.23,
    "estimated_gdp": 25767448125.2,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-22T18:00:00Z"
  }
]
```

---

### 3. Get Country by Name
```http
GET /countries/{name}
```

**Example:**
```http
GET /countries/Nigeria
```

**Response:**
```json
{
  "id": 1,
  "name": "Nigeria",
  "capital": "Abuja",
  "region": "Africa",
  "population": 206139589,
  "currency_code": "NGN",
  "exchange_rate": 1600.23,
  "estimated_gdp": 25767448125.2,
  "flag_url": "https://flagcdn.com/ng.svg",
  "last_refreshed_at": "2025-10-22T18:00:00Z"
}
```

**Error Response (404):**
```json
{
  "error": "Country not found",
  "details": "No data found for country 'InvalidName'"
}
```

---

### 4. Delete Country
```http
DELETE /countries/{name}
```

**Response:**
```json
{
  "message": "Country deleted successfully."
}
```

**Error Response (404):**
```json
{
  "error": "Country not found"
}
```

---

### 5. Get Status
```http
GET /status
```

**Response:**
```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-22T18:00:00Z"
}
```

---

### 6. Get Summary Image
```http
GET /countries/image
```

Returns a PNG image containing:
- Total number of countries
- Top 5 countries by estimated GDP
- Last refresh timestamp

**Error Response (404):**
```json
{
  "error": "Summary image not found"
}
```

## Project Structure

```
backend/
├── main.py              # FastAPI application and routes
├── database.py          # Database models and configuration
├── utils.py             # Utility functions (API calls, calculations)
├── schemas.py           # Pydantic models for validation
├── config.py            # Configuration management
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── README.md            # This file
└── cache/               # Generated images directory
    └── summary.png      # Auto-generated summary image
```

## Database Schema

### Country Table
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| name | String | Yes | Country name (indexed) |
| capital | String | No | Capital city |
| region | String | No | Geographic region (indexed) |
| population | Integer | Yes | Population count |
| currency_code | String | No | Currency code (indexed) |
| exchange_rate | Float | No | Exchange rate to USD |
| estimated_gdp | Float | No | Calculated GDP estimate |
| flag_url | String | No | URL to flag image |
| last_refreshed_at | DateTime | No | Last update timestamp |

## Error Handling

The API returns consistent JSON error responses:

- **400 Bad Request**: Validation failed
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: External API unavailable

## Development

### Run in development mode
```bash
uvicorn main:app --reload --port 9000
```

### Access API documentation
- Swagger UI: `http://localhost:9000/docs`
- ReDoc: `http://localhost:9000/redoc`

## Production Deployment

### Switch to MySQL

1. Update `.env`:
   ```env
   DATABASE_URL=mysql://username:password@host:port/database_name
   ```

2. Ensure MySQL client is installed:
   ```bash
   pip install mysqlclient
   ```

### Deployment Options

- **Railway**: [railway.app](https://railway.app)
- **Heroku**: [heroku.com](https://heroku.com)
- **AWS**: EC2, Elastic Beanstalk, or Lambda
- **DigitalOcean**: App Platform


## License

MIT License

## Author

[Your Name] - HNG13 Stage 2 Task

## Acknowledgments

- [REST Countries API](https://restcountries.com/)
- [Exchange Rate API](https://open.er-api.com/)
