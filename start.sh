#!/usr/bin/env bash
python setup_data.py
python monitor.py
uvicorn app:app --host 0.0.0.0 --port $PORT