@echo off
chcp 65001 >nul
cls

echo.
echo     ⭐ xAdmin FastAPI 快速启动工具 ⭐
echo     =====================================
echo.
echo     选择启动方式:
echo.
echo     1) 🚀 开发模式启动 (推荐)
echo     2) 🏭 生产模式启动  
echo     3) 🧪 运行测试
echo     4) 🔧 初始化项目
echo     5) 📊 项目状态检查
echo     6) 📖 打开API文档
echo     7) ❓ 查看帮助
echo     0) 🚪 退出
echo.

set /p choice="请输入选项 (0-7): "

if "%choice%"=="1" goto dev
if "%choice%"=="2" goto prod  
if "%choice%"=="3" goto test
if "%choice%"=="4" goto init
if "%choice%"=="5" goto check
if "%choice%"=="6" goto docs
if "%choice%"=="7" goto help
if "%choice%"=="0" goto exit
goto invalid

:dev
echo.
echo 🚀 启动开发服务器...
python manage.py dev
goto end

:prod
echo.
echo 🏭 启动生产服务器...
python manage.py prod
goto end

:test
echo.
echo 🧪 运行测试套件...
python manage.py test
goto end

:init
echo.
echo 🔧 初始化项目...
python manage.py init
goto end

:check
echo.
echo 📊 检查项目状态...
python manage.py check
goto end

:docs
echo.
echo 📖 启动服务器并打开API文档...
python manage.py docs
goto end

:help
echo.
echo 📋 可用命令列表:
python manage.py help
goto end

:invalid
echo.
echo ❌ 无效选项，请重新选择
goto start

:exit
echo.
echo 👋 再见！
exit /b 0

:end
echo.
echo 按任意键返回主菜单...
pause >nul
goto start

:start
goto :eof