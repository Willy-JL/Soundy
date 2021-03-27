import sys
import subprocess

subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', 'requirements.txt'])
input('\n\n\nPress [Enter] to exit... ')
