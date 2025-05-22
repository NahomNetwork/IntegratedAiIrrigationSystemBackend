# Backend System for Sensor Data Management

This project is a backend system for managing sensor data, built with FastAPI, SQLAlchemy, and Alembic. It supports real-time communication using Socket.IO and includes a machine learning model for predictions.

---

## Features

- **FastAPI**: RESTful API for managing sensor data.
- **Socket.IO**: Real-time communication with clients.
- **SQLAlchemy**: Database ORM for managing data models.
- **Alembic**: Database migrations.
- **Machine Learning**: Integration with a pre-trained LightGBM model for predictions.

---

## Prerequisites

- Python 3.12 or higher
- Docker (optional, for containerized deployment)
- PostgreSQL (or any compatible database)

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd backend
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with the following content:

```env
DATABASE_URL=postgresql+asyncpg://<username>:<password>@<host>:<port>/<database>
```

Replace `<username>`, `<password>`, `<host>`, `<port>`, and `<database>` with your database credentials.

---

## Running the Project

### Option 1: Using Docker

1. **Build the Docker Image**:

   ```bash
   docker build -t backend-system .
   ```

2. **Run the Docker Container**:

   ```bash
   docker run -p 8000:8000 --env-file .env backend-system
   ```

The application will be available at `http://localhost:8000`.

---

### Option 2: Manual Setup

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run Database Migrations**:

   ```bash
   alembic upgrade head
   ```

3. **Start the Application**:

   ```bash
   python main.py
   ```

The application will be available at `http://localhost:8080`.

---

## API Endpoints

### Sensor Data Management

- **POST** `/api/system/sensor_data`: Receive sensor data and store it in the database.
- **GET** `/api/system/get_sensordata`: Retrieve the latest 10 sensor data entries.
- **GET** `/api/system/get_sensordata/last`: Retrieve the most recent sensor data entry.
- **GET** `/api/system/get_sensordata/{id}`: Retrieve sensor data by ID.
- **DELETE** `/api/system/sensordata/purge`: Purge all sensor data.
- **GET** `/api/system/non_working_sensors`: Retrieve non-working sensors.

- You can get more infor by visiting [Docs](http://localhost:8080/docs) /docs of your deployment

---

## Real-Time Communication

The application uses Socket.IO for real-time communication. Events include:

- **`connect`**: Triggered when a client connects.
- **`disconnect`**: Triggered when a client disconnects.
- **`sensor_data`**: Broadcasts new sensor data to connected clients.

---

## Machine Learning Model

The application uses a pre-trained LightGBM model for predictions. The model file (`lgbm_model.pkl`) should be placed in the `model/` directory.

---

[Deploying to a VPS](/DEPLOY_TO_VPS.MD)

---

## License

This project is licensed under the MIT License.
