import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app="app:app",
        host="0.0.0.0",
        port=8000,
        log_config="log_conf_dev.yaml",
        workers=1,
        reload=True,
    )
