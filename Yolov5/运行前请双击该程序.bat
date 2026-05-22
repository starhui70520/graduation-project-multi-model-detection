@echo off
REM 切换到脚本所在目录
cd /d %~dp0

REM 安装所需的库
pip install -r requirements.txt

REM 检查安装结果
IF %ERRORLEVEL% NEQ 0 (
    echo 安装过程中发生错误，请检查并手动安装所需库。
    pause
    exit /b %ERRORLEVEL%
)

echo 安装成功！
pause
exit /b 0
