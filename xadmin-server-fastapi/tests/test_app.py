#!/usr/bin/env python
"""
Simple FastAPI test application
"""
from fastapi import FastAPI

app = FastAPI(title="xAdmin FastAPI Test")

@app.get("/")
async def root():
    return {"message": "xAdmin FastAPI is running!", "status": "success"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "xadmin-fastapi"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)