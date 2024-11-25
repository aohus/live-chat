import multiprocessing

uvicorn_settings = {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": multiprocessing.cpu_count(),
    "backlog": 4096,
    "timeout_keep_alive": 120,
    "loop": "uvloop",
    "http": "httptools",
}

# SSL 설정 (옵션)
# ssl_certfile = None  # SSL 인증서 경로
# ssl_keyfile = None   # SSL 키 경로
# if ssl_certfile and ssl_keyfile:
#     uvicorn_settings["ssl_certfile"] = ssl_certfile
#     uvicorn_settings["ssl_keyfile"] = ssl_keyfile
