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

channels = []

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




sorted_results = sorted(results, key=lambda x: (int(re.search(r'\d+', x[0]).group()) if re.search(r'\d+', x[0]) else float('inf'), x[0] != 'CCTV5'))


cctv_channels = []
satellite_channels = []
other_channels = []

for channel_name, channel_url in sorted_results:
    if 'CCTV' in channel_name:
        cctv_channels.append((channel_name, channel_url))
    elif '卫视' in channel_name:
        satellite_channels.append((channel_name, channel_url))
    else:
        other_channels.append((channel_name, channel_url))





cctv_merged = []
channel_counters = {}
result_counter = 7 

for channel_name, channel_url in cctv_channels:
   if channel_name in channel_counters:
       if channel_counters[channel_name] >= result_counter:
           continue
       else:
           cctv_merged.append((channel_name, channel_url))
           channel_counters[channel_name] += 1
   else:
       cctv_merged.append((channel_name, channel_url))
       channel_counters[channel_name] = 1



satellite_merged = {}
channel_counters = {}
result_counter = 7  

for channel_name, channel_url in satellite_channels:
    prefix = channel_name.split(' ')[0]
    if prefix in satellite_merged:
        if channel_name not in channel_counters:
            channel_counters[channel_name] = 0

        if channel_counters[channel_name] < result_counter:
            satellite_merged[prefix].append((channel_name, channel_url))
            channel_counters[channel_name] += 1
    else:
        satellite_merged[prefix] = [(channel_name, channel_url)]
        channel_counters[channel_name] = 1

    

other_merged = {}
channel_counters = {}
result_counter = 5  

for channel_name, channel_url in other_channels:
    prefix = channel_name.split(' ')[0]
    if prefix in other_merged:
        if channel_name not in channel_counters:
            channel_counters[channel_name] = 0

        if channel_counters[channel_name] < result_counter:
            other_merged[prefix].append((channel_name, channel_url))
            channel_counters[channel_name] += 1
    else:
        other_merged[prefix] = [(channel_name, channel_url)]
        channel_counters[channel_name] = 1


other_channels_sorted = []
for prefix in sorted(other_merged.keys()):
    for channel_name, channel_url in other_merged[prefix]:
        other_channels_sorted.append((channel_name, channel_url))




with open("10001", 'w', encoding='utf-8') as file:

    file.write('央视频道,#genre#\n')
    for channel_name, channel_url in cctv_merged:
        file.write(f"{channel_name},{channel_url}\n")
    

    file.write('卫视频道,#genre#\n')
    for prefix in sorted(satellite_merged.keys()):
        for channel_name, channel_url in satellite_merged[prefix]:
            file.write(f"{channel_name},{channel_url}\n")
    

    file.write('其他频道,#genre#\n')
    for prefix in sorted(other_merged.keys()):
        for channel_name, channel_url in other_merged[prefix]:    
            file.write(f"{channel_name},{channel_url}\n")

    



with open("hyd", 'w', encoding='utf-8') as file:
    # 写入CCTV频道
    file.write('央视频道,#genre#\n')
    for channel_name, channel_url in cctv_merged:
        file.write(f"{channel_name},{channel_url}\n")


with open("hysd", 'w', encoding='utf-8') as file:
    # 写入CCTV频道
    file.write('央视频道,#genre#\n')
    for channel_name, channel_url in cctv_merged:
        file.write(f"{channel_name},{channel_url}\n")


with open("10001m3u", 'w', encoding='utf-8') as file:
    file.write('#EXTM3U\n')
    

    for channel_name, channel_url in cctv_merged:
        file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
        file.write(f"{channel_url}\n")


    for prefix in sorted(satellite_merged.keys()):
        for channel_name, channel_url in satellite_merged[prefix]:
            file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
            file.write(f"{channel_url}\n")


    for prefix in sorted(other_merged.keys()):
        for channel_name, channel_url in other_merged[prefix]:
            file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
            file.write(f"{channel_url}\n")




with open("hydm3u", 'w', encoding='utf-8') as file:
    file.write('#EXTM3U\n')
    

    for channel_name, channel_url in cctv_merged:
        file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
        file.write(f"{channel_url}\n")


