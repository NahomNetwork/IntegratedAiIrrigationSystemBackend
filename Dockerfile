FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1 build-essential cargo


# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy application code
COPY . .

RUN alembic upgrade head

# Start the FastAPI app with Gunicorn using Uvicorn worker
CMD ["gunicorn", "main:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]