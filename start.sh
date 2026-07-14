#!/bin/bash
# Start FastAPI backend (pie SVG API) on port 8000
exec uvicorn backend:app --host 0.0.0.0 --port 8000
