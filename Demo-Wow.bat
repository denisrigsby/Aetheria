@echo off
setlocal
cd /d "%~dp0"
title Aetheria WOW Demo
echo.
echo  Aetheria WOW Demo - plant clock keeps ticking after chat closes
echo  Public reference only. Not the private plant.
echo.
python -u scripts/demo_wow.py
echo.
pause
