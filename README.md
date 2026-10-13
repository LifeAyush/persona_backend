# persona_backend

Live ride prices for one route across Ola, Rapido, and Namma Yatri.

You send a pickup and a drop. The API asks each app and returns the fares side by side.

Arun Singh built the Rapido scraper, the compiled fare response, CORS, and the duplicate-row fix.

## How to run

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/LifeAyush/persona_backend.git
   cd persona_backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Export the ride-app credentials the scrapers need:

   ```bash
   export RAPIDO_TOKENS=""
   export OLA_ACCESS_TOKEN=""
   export OLA_USER_TOKEN=""
   export OLA_REFRESH_TOKEN=""
   export NAMMA_YATRI_TOKEN=""
   ```

5. Start the API:

   ```bash
   uvicorn main:app --reload
   ```

`POST /api/v1/get_fares` takes the route and returns the fares.

## License

MIT
