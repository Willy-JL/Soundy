@echo off
pyinstaller --clean -y --dist dist\windows --workpath tmp build.spec
cmd.exe /c rmdir /s /q dist\windows\Soundy\certifi
cmd.exe /c rmdir /s /q dist\windows\Soundy\Include
cmd.exe /c rmdir /s /q dist\windows\Soundy\win32com
cmd.exe /c del /f /q dist\windows\Soundy\_asyncio.pyd
cmd.exe /c del /f /q dist\windows\Soundy\_cffi_backend.cp38-win_amd64.pyd
cmd.exe /c del /f /q dist\windows\Soundy\_elementtree.pyd
cmd.exe /c del /f /q dist\windows\Soundy\_hashlib.pyd
cmd.exe /c del /f /q dist\windows\Soundy\_queue.pyd
cmd.exe /c del /f /q dist\windows\Soundy\_win32sysloader.pyd
cmd.exe /c del /f /q dist\windows\Soundy\api-ms-win-*
cmd.exe /c del /f /q dist\windows\Soundy\d3dcompiler_47.dll
cmd.exe /c del /f /q dist\windows\Soundy\libEGL.dll
cmd.exe /c del /f /q dist\windows\Soundy\libGLESv2.dll
cmd.exe /c del /f /q dist\windows\Soundy\mfc140u.dll
cmd.exe /c del /f /q dist\windows\Soundy\MSVCP140.dll
cmd.exe /c del /f /q dist\windows\Soundy\MSVCP140_1.dll
cmd.exe /c del /f /q dist\windows\Soundy\opengl32sw.dll
cmd.exe /c del /f /q dist\windows\Soundy\Qt5DBus.dll
cmd.exe /c del /f /q dist\windows\Soundy\Qt5Network.dll
cmd.exe /c del /f /q dist\windows\Soundy\Qt5Qml.dll
cmd.exe /c del /f /q dist\windows\Soundy\Qt5QmlModels.dll
cmd.exe /c del /f /q dist\windows\Soundy\Qt5Quick.dll
cmd.exe /c del /f /q dist\windows\Soundy\Qt5Svg.dll
cmd.exe /c del /f /q dist\windows\Soundy\Qt5WebSockets.dll
cmd.exe /c del /f /q dist\windows\Soundy\ucrtbase.dll
cmd.exe /c del /f /q dist\windows\Soundy\VCRUNTIME140.dll
cmd.exe /c del /f /q dist\windows\Soundy\VCRUNTIME140_1.dll
cmd.exe /c del /f /q dist\windows\Soundy\win32trace.pyd
cmd.exe /c del /f /q dist\windows\Soundy\win32ui.pyd
cmd.exe /c del /f /q dist\windows\Soundy\win32wnet.pyd
cmd.exe /c mkdir dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\_ctypes.pyd dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\_overlapped.pyd dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\_socket.pyd dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\_ssl.pyd dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\libcrypto-1_1.dll dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\libffi-7.dll dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\libssl-1_1.dll dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\pyexpat.pyd dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\python3.dll dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\pythoncom38.dll dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\pywintypes38.dll dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\select.pyd dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\win32api.pyd dist\windows\Soundy\lib
cmd.exe /c move /y dist\windows\Soundy\win32event.pyd dist\windows\Soundy\lib
cd dist\windows\Soundy
start Soundy.exe
