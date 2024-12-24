# errands/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status


class RedirectUnauthenticatedMiddleware:
    """
    中间件：拦截未认证的 API 请求并重定向到登录页面。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 检查响应状态码是否为 401 或 403
        if response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]:
            # 检查请求是否为 API 请求
            if request.path.startswith('/api/'):
                # 检查请求是否为 AJAX 请求（通过头部 'X-Requested-With'）
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                if not is_ajax:
                    # 获取登录页面的 URL 名称（根据您的 URL 配置可能需要调整）
                    login_url = reverse('login_page')
                    return redirect(login_url)

        return response
