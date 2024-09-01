# Setup Instructions

## Prerequisites
- Docker
- Docker Compose

## Steps to Setup and Run

1. Clone the repository:
    ```bash
    git clone https://github.com/username/quantum-stabilizer-codes.git
    cd quantum-stabilizer-codes
    ```

2. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```

3. Access the application:
    - Go to `http://localhost` in your web browser to access the frontend.
    - The backend API is accessible at `http://localhost/api/quantum/simulate`.

4. To stop the application:
    ```bash
    docker-compose down
    ```

## Optional Setup (without Docker)
- To run the backend:
  1. Navigate to `backend/`
  2. Install dependencies: `npm install`
  3. Run the server: `npm start`

- To run the frontend:
  1. Navigate to `frontend/`
  2. Install dependencies: `npm install`
  3. Run the frontend: `npm start`

## Additional Notes
- The `simulation/` folder contains Python scripts for quantum error correction simulations. Ensure you have Python 3.8+ installed along with the required libraries (`pip install -r requirements.txt`).
