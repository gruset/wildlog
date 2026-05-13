#!/usr/bin/env python3
"""
Entrypoint used by gunicorn / Docker.
Ensures the DB is initialised before the first request is handled.
"""
from app import app, init_db

init_db()

if __name__ == '__main__':
    app.run()
