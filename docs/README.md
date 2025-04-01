# Stablecoin Analytics Platform

## Project Overview
This platform provides comprehensive analytics and insights for stablecoin markets, helping users understand market dynamics, track performance metrics, and make informed decisions.

## Architecture
The project is structured into three main components:

### Frontend
- Modern web application for data visualization and user interaction
- Will be implemented using React/Next.js
- Will provide interactive charts, real-time data updates, and user-friendly interfaces

### Backend
- Python-based API server
- Handles data processing, analysis, and storage
- Provides RESTful endpoints for frontend consumption
- Integrates with various blockchain data sources

### Documentation
- Contains project documentation, API references, and setup guides
- Will be maintained as the project evolves

## Getting Started

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. Run tests:
   ```bash
   pytest
   ```

The API will be available at `http://localhost:8000`. You can access the automatic API documentation at `http://localhost:8000/docs`.

## Development Status
- Project is in initial setup phase
- Basic structure and environment configuration completed
- FastAPI backend initialized with health endpoint
- Further development in progress 