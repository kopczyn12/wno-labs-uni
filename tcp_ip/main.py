import subprocess
import subprocess

path_to_server = "/home/mkopcz/Desktop/uni/wno2/server.py"
subprocess.run(['gnome-terminal', '--', 'bash', '-c', f'python3 {path_to_server}; exec bash'])

path_to_client = "/home/mkopcz/Desktop/uni/wno2/client.py"
subprocess.run(['gnome-terminal', '--', 'bash', '-c', f'python3 {path_to_client}; exec bash'])

path_to_client = "/home/mkopcz/Desktop/uni/wno2/client.py"
subprocess.run(['gnome-terminal', '--', 'bash', '-c', f'python3 {path_to_client}; exec bash'])
