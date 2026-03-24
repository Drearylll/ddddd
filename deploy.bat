@echo off
chcp 65001 >nul
echo ========================================
echo   Go In - 公网部署快速脚本
echo ========================================
echo.

:menu
echo 请选择部署方式：
echo.
echo 1. 上传到 GitHub（所有部署方式的前提）
echo 2. Vercel 部署（推荐，最简单）
echo 3. Railway 部署
echo 4. 本地测试运行
echo 5. 查看部署指南
echo 0. 退出
echo.
set /p choice=请输入选项 (0-5): 

if "%choice%"=="1" goto github
if "%choice%"=="2" goto vercel
if "%choice%"=="3" goto railway
if "%choice%"=="4" goto local
if "%choice%"=="5" goto guide
if "%choice%"=="0" goto end
goto menu

:github
echo.
echo ========================================
echo   步骤 1: 上传到 GitHub
echo ========================================
echo.
echo 请依次执行以下命令：
echo.
echo git init
echo git add .
echo git commit -m "Initial commit"
echo.
echo 然后创建 GitHub 仓库并执行：
echo git remote add origin https://github.com/你的用户名/goin.git
echo git push -u origin main
echo.
pause
goto menu

:vercel
echo.
echo ========================================
echo   步骤 2: Vercel 部署
echo ========================================
echo.
echo 1. 访问 https://vercel.com
echo 2. 点击 "New Project"
echo 3. 选择 "Import Git Repository"
echo 4. 选择你的 goin 仓库
echo 5. 点击 "Deploy"
echo.
echo 部署完成后获得链接：https://goin-xxx.vercel.app
echo.
pause
goto menu

:railway
echo.
echo ========================================
echo   步骤 2: Railway 部署
echo ========================================
echo.
echo 需要先安装 Railway CLI:
echo npm install -g @railway/cli
echo.
echo 然后执行：
echo railway login
echo railway init
echo railway up
echo.
pause
goto menu

:local
echo.
echo ========================================
echo   本地测试运行
echo ========================================
echo.
echo 正在启动 Flask 开发服务器...
echo.
python app.py
goto menu

:guide
echo.
echo ========================================
echo   查看部署指南
echo ========================================
echo.
echo 打开文件：部署指南.md
echo.
start 部署指南.md
pause
goto menu

:end
echo.
echo 再见！
echo.
timeout /t 2 >nul
