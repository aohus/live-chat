import uvicorn
from core.config import config
from dotenv import find_dotenv, load_dotenv

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    uvicorn.run(
        app="app:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True if config.ENV != "production" else False,
        log_config="log_conf_dev.yaml",
        workers=1,
    )
