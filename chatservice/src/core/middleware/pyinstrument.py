from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from pyinstrument import Profiler
from starlette.middleware.base import BaseMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

PROFILING = True  # 프로파일링을 활성화하는 플래그


class ProfilerMiddleware:
    def __init__(self, app: ASGIApp, interval: float = 0.001):
        self.interval = interval

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 프로파일러 인스턴스 초기화 (HTTP 및 WebSocket에 대해 모두 적용)
        profiler = (
            Profiler(interval=self.interval, async_mode="enabled")
            if PROFILING
            else None
        )

        if scope["type"] == "http":
            # HTTP 요청 프로파일링 처리
            request = Request(scope, receive)
            profiling = request.query_params.get("profile", False)

            if profiling and profiler:
                profiler.start()
                response = await self.app(scope, receive, send)
                profiler.stop()

                # 프로파일링 결과 출력
                html_output = profiler.output_html()
                return await send(HTMLResponse(html_output)(scope, receive, send))

            # 프로파일링이 비활성화된 경우 일반 처리
            await self.app(scope, receive, send)

        elif scope["type"] == "websocket":
            # WebSocket 요청 프로파일링 처리
            if profiler:
                profiler.start()  # 웹소켓 연결 시작 시 프로파일링 시작

            async def receive_wrapper() -> Message:
                message = await receive()
                if message["type"] == "websocket.receive":
                    if profiler:
                        profiler.stop()
                        print(profiler.output_text(unicode=True, color=True))
                        profiler.start()  # 메시지 수신 후 프로파일링 재시작
                elif message["type"] == "websocket.disconnect":
                    if profiler:
                        profiler.stop()
                        print(profiler.output_text(unicode=True, color=True))
                return message

            await self.app(scope, receive_wrapper, send)
