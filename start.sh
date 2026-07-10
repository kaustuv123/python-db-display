#!/bin/bash
# Start FastAPI backend on port 8000
uvicorn backend:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend on port 8501
streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
