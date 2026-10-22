"""Che input trong lỗi envelope của riêng API yêu cầu feature (4d)."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute


class TuyenEnvelopeKin(APIRoute):
    def get_route_handler(self):
        xu_ly = super().get_route_handler()

        async def goi(request: Request):
            try:
                return await xu_ly(request)
            except RequestValidationError:
                return JSONResponse(
                    {"trang_thai": "khong_hop_le", "loi": ["Thân yêu cầu không hợp lệ"]},
                    status_code=422,
                )

        return goi
