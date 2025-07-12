# Promesse Backend

This is the backend for the Promesse application, a smart wardrobe and fashion assistant. It's built using FastAPI and MySQL.

## Features

- User Authentication (Register, Login)
- Wardrobe Management (Items, Outfits)
- Weekly Outfit Planning
- Occasion Planning
- Style History Tracking
- Wardrobe Statistics
- AI-Powered Features:
    - Outfit Analysis (mocked, planned for ML model integration)
    - Fashion Trend Forecasting (mocked, planned for ML model integration)
- Outfit Recommendations for Occasions (basic heuristics)
- Personalized Wardrobe Suggestions (basic heuristics)

## Setup and Installation

### Prerequisites

- Python 3.9+
- MySQL Server (e.g., via XAMPP, Docker, or standalone installation)
- Pip (Python package installer)

### Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
DATABASE_URL="mysql+mysqlconnector://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE_NAME"
# Example: DATABASE_URL="mysql+mysqlconnector://root:password@localhost:3306/promesse_app_db"

SECRET_KEY="your_very_strong_random_secret_key_for_jwt"
# Generate a strong key, e.g., using: openssl rand -hex 32
```

**Important:**
1.  Replace `USERNAME`, `PASSWORD`, `HOSTNAME`, `PORT`, and `DATABASE_NAME` with your actual MySQL connection details.
2.  You must **manually create the database** (e.g., `promesse_app_db`) in your MySQL server before running the application for the first time. The application will create the tables but not the database itself.
3.  Replace `your_very_strong_random_secret_key_for_jwt` with a securely generated secret key.

### Installation Steps

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository_url>
    # cd <repository_name>/backend
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    Make sure you are in the `backend/` directory where `requirements.txt` is located.
    ```bash
    pip install -r requirements.txt
    ```
    This will install FastAPI, Uvicorn, SQLAlchemy, MySQL connector, Pillow, and the AI/ML libraries (TensorFlow, Transformers, PyTorch, scikit-learn, etc.).

### Running the Application

1.  **Ensure your MySQL server is running** and the database specified in `DATABASE_URL` exists.
2.  **Navigate to the `backend/` directory.**
3.  **Run the FastAPI application using Uvicorn:**
    ```bash
    python main.py
    ```
    Alternatively, you can run directly with Uvicorn for more options:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The `--reload` flag enables auto-reloading when code changes, useful for development.

4.  The API will be available at `http://localhost:8000`.
5.  Interactive API documentation (Swagger UI) will be at `http://localhost:8000/docs`.
6.  Alternative API documentation (ReDoc) will be at `http://localhost:8000/redoc`.

## AI/ML Model Integration (Future Work)

The AI features (Outfit Analysis, Trend Forecasting, advanced Recommendations) currently use mock logic or simple heuristics. The environment is prepared with necessary libraries (`tensorflow`, `transformers`, `torch`, `scikit-learn`) for future integration of actual machine learning models. This would involve:
- Selecting or training appropriate models.
- Downloading pre-trained model weights.
- Implementing inference logic within the `ai_services.py` and `recommendation_services.py`.
- Potentially setting up asynchronous task queues (e.g., Celery) for long-running AI processes to avoid blocking API responses.

## Testing

Basic unit tests are located in the `backend/app/tests/` directory. To run tests:

1.  Ensure development dependencies like `pytest` and `pytest-asyncio` are installed:
    ```bash
    pip install pytest pytest-asyncio
    ```
2.  Navigate to the `backend/` directory.
3.  Run pytest:
    ```bash
    pytest
    ```
    (You might need to set `PYTHONPATH=.` or run as `python -m pytest` if imports are not resolved.)
# wardrobe-system-backend
# wardrobe-system-backend
