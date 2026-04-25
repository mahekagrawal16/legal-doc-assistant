# app.py

import multiprocessing
import subprocess
import uvicorn
import time

def run_fastapi():
    """Starts the FastAPI backend."""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

def run_streamlit():
    """Starts the Streamlit frontend."""
    subprocess.run(["streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    # Start both FastAPI and Streamlit in separate processes
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    streamlit_process = multiprocessing.Process(target=run_streamlit)

    fastapi_process.start()
    time.sleep(2)  # Let FastAPI boot first (optional)
    streamlit_process.start()

    # Wait for both to finish (Ctrl+C will terminate both)
    fastapi_process.join()
    streamlit_process.join()
