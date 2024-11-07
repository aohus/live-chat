class TokenAdapter:
    async def parse_token(self, token: str) -> int:
        return token


# from typing import Optional

# import jwt


# class TmpTokenAdapter:
#     def __init__(self, secret_key: str, algorithm: str = "HS256"):
#         self.secret_key = secret_key
#         self.algorithm = algorithm

#     async def parse_token(self, token: str) -> Optional[int]:
#         """
#         토큰을 파싱하여 채널 ID를 반환하는 메서드.

#         :param token: 인증 토큰 (JWT 토큰 형식으로 가정)
#         :return: 유효한 경우 채널 ID, 그렇지 않은 경우 None
#         """
#         try:
#             decoded_data = jwt.decode(
#                 token, self.secret_key, algorithms=[self.algorithm]
#             )
#             channel_id = decoded_data.get("channel_id")

#             if channel_id is not None:
#                 return channel_id
#             return None

#         except jwt.ExpiredSignatureError:
#             print("토큰이 만료되었습니다.")
#             return None

#         except jwt.InvalidTokenError:
#             print("유효하지 않은 토큰입니다.")
#             return None
