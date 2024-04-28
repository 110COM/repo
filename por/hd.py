import os
import re
import time
import asyncio
import aiohttp
import concurrent.futures
import subprocess
import json
import requests
import threading
from queue import Queue


task_queue = Queue()


results = []
channels = []
error_channels = []


speed_file_path = f"jiee/itv_speed.txt"
with open(speed_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if line and ',' in line:
            try:
                channel_name, channel_url = line.split(',')
                channels.append((channel_name.strip(), channel_url.strip()))
            except ValueError:
                continue



def get_resolution(name, url, timeout=10):
    process = None
    try:
        cmd = ['ffprobe', '-print_format', 'json', '-show_streams', '-select_streams', 'v', url]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=timeout)
        info = json.loads(stdout.decode())
        width = int(info['streams'][0]['width'])
        height = int(info['streams'][0]['height'])
        if width >= 1920 and height >= 1080:
            return name, url
    except subprocess.TimeoutExpired:
        process.kill()
    except Exception as e:
        pass
    finally:
        if process:
            process.wait()
    return None



def worker():
    while True:
        channel_name, channel_url = task_queue.get()
        try:
            resolution_info = get_resolution(channel_name, channel_url, timeout=15)
            if resolution_info:
                results.append(resolution_info)
        except Exception as e:
            error_channels.append((channel_name, channel_url))
        task_queue.task_done()





num_threads = 30
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    t.start()


for channel in channels:
    task_queue.put(channel)


task_queue.join()


out1_file_path = f"jiee/hd"
with open(out1_file_path, 'w', encoding='utf-8') as file:
    for name, url in results:
        file.write(f"{name},{url}\n")
        
        
        
        

            
            

print("\n已完成")
