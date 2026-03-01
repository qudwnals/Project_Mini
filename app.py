import os
import sys

# 프로젝트 루트 경로를 sys.path에 추가하여 src 모듈을 임포트할 수 있도록 함
root_path = os.path.abspath(os.path.dirname(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)

from src.dashboard.app_layout import DashboardApp

if __name__ == "__main__":
    # 대시보드 앱 인스턴스 생성 및 실행
    app = DashboardApp(root_path)
    app.run()
