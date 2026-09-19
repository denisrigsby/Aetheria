@echo off
setlocal
cd /d "%~dp0"
title Aetheria continuity proof
echo.
echo  Aetheria continuity proof - public reference
echo  Fact: plant clock keeps advancing after Talk-face closes
echo  Not the private plant.
echo.
python -u scripts/demo_continuity.py
echo.
pause
