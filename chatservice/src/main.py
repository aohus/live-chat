import uvicorn
from core.config import config
from core.uvicorn_config import uvicorn_settings

if __name__ == "__main__":
    # 개발 환경과 프로덕션 환경에 따라 설정 변경
    environment_settings = {
        "reload": True if config.ENV != "production" else False,
        "log_config": "log_conf_dev.yaml",
    }

    # uvicorn 실행
    uvicorn.run(
        app="app:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        **uvicorn_settings,  # 기본 설정 로드
        **environment_settings,  # 환경별 설정 덮어쓰기
    )
