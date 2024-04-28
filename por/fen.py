cctv_channels = []
other_channels = []
satellite_channels = []
sport_channels = []
child_channels = []
guangdong_channels = []
hunan_channels = []
zhejiang_channels = []
other_channels2 = []



in1_file_path = f"jiee/hd"
with open(in1_file_path, 'r',  encoding='utf-8') as file:
    lines = file.readlines()
    lines = [line.strip() for line in lines if line.strip() and 'http' in line]
    
    for line in lines:
        if ',' not in line:
            print(f"Skipping invalid data: {line}")
            continue
            
        name, url = line.strip().split(',')
        channel_name = name.split(' ')[0]
        

        keywords = ["购", "推荐", "宣传", "酒店", "视频"]
        if any(keyword in name for keyword in keywords):
            continue
        
        
        if 'CCTV' not in channel_name and '卫视' not in channel_name:
            other_channels2.append((name, url))
            

        classified = False
        

        channel_keywords = {
            'cctv_channels': ['CCTV'],
            'sport_channels': ['CCTV5', '体育', '足球'],
            'child_channels': ['CCTV14', '卡', '少儿', '哈哈炫动'],
            'satellite_channels': ['卫视'],
            'guangdong_channels': ['广东', '广州', '惠州', '河源', '东莞', '梅州', '深圳', '潮州', '珠江', '揭西'],
            'hunan_channels': ['湖南', '金鹰', '茶'],
            'zhejiang_channels': ['浙江', '杭州', '西湖明珠', '宁波', '上虞', '丽水', '松阳', '永嘉', '温州', '绍兴', '苍南', '衢州', '诸暨', '遂昌', '青田', '龙泉']
        }



        for channel_list, keywords in channel_keywords.items():
            for keyword in keywords:
                if keyword in channel_name or keyword in name:
                    locals()[channel_list].append((name, url))
                    classified = True
                    #break  #

        if not classified:
            other_channels.append((name, url))
        
        
    #print(other_channels2)






def group_and_sort_channels(channel_list):

    channel_dict = {}
    for name, url in channel_list:
        prefix = name.split(' ')[0]
        if prefix in channel_dict:
            channel_dict[prefix].append((name, url))
        else:
            channel_dict[prefix] = [(name, url)]


    if channel_list and 'CCTV' in channel_list[0][0]:  #
        sorted_channels = []
        for prefix in sorted(channel_dict.keys(), key=lambda x: (int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf'), x != 'CCTV5', x)):
            sorted_channels.extend(channel_dict[prefix])
    else:  #
        sorted_channels = []
        for prefix in sorted(channel_dict.keys()):
            sorted_channels.extend(channel_dict[prefix])
    
    return sorted_channels

#
cctv_channels_sorted = group_and_sort_channels(cctv_channels)
satellite_channels_sorted = group_and_sort_channels(satellite_channels)
sport_channels_sorted = group_and_sort_channels(sport_channels)
child_channels_sorted = group_and_sort_channels(child_channels)
other_channels_sorted = group_and_sort_channels(other_channels)

guangdong_channels_sorted = group_and_sort_channels(guangdong_channels)
hunan_channels_sorted = group_and_sort_channels(hunan_channels)
zhejiang_channels_sorted = group_and_sort_channels(zhejiang_channels)
other_channels2_sorted = group_and_sort_channels(other_channels2)




#
def limit_channel_list(channel_list, limit=7):
    #print("Starting limit_channel_list function...")
    #print("channel_list:", channel_list)  # 输出 channel_list 的值
    name_counts = {}
    limited_list = []
    for name, url in channel_list:
        if name not in name_counts:
            name_counts[name] = 0
        if name_counts[name] < limit:
            limited_list.append((name, url))
            name_counts[name] += 1
    return limited_list
    
    
    
#
channel_lists = {
    "央视频道": cctv_channels_sorted,
    "卫视频道": satellite_channels_sorted,
    "体育频道": sport_channels_sorted,
    "少儿频道": child_channels_sorted,
    "其它": other_channels_sorted,
    "广东":guangdong_channels_sorted,
    "湖南":hunan_channels_sorted,
    "浙江":zhejiang_channels_sorted,
}




#
output5_file_path = f"C/hyd"

cctv_channels = channel_lists.get("央视频道", [])
with open(output5_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(f"央视频道,#genre#\n")  # 写入分类信息
    for name, url in limit_channel_list(cctv_channels):
        output_file.write(f"{name},{url}\n")


#
output6_file_path = f"C/hydm3u"

cctv_channels = channel_lists.get("央视频道", [])
with open(output6_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write('#EXTM3U\n')  # 写入第一行
    group_title = "央视频道"  # 默认分组标题为央视频道
    for name, url in limit_channel_list(cctv_channels):
        output_file.write(f"#EXTINF:-1 group-title=\"{group_title}\",{name}\n")
        output_file.write(f"{url}\n")
        



#
output7_file_path = f"C/10001"

# 写入所有频道列表并限制数量
limited_channels = limit_channel_list(channel_list)

with open(output7_file_path, 'w', encoding='utf-8') as output_file:
    for channel_name, channel_list in channel_lists.items():
        output_file.write(f"{channel_name},#genre#\n")  # 写入分类信息
        for name, url in limit_channel_list(channel_list):
            output_file.write(f"{name},{url}\n")
        output_file.write("\n")




#
output8_file_path = f"C/10001m3u"

#
limited_channels = limit_channel_list(channel_list)

with open(output8_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write('#EXTM3U\n')  # 写入第一行
    for channel_name, channel_list in channel_lists.items():
        for name, url in limit_channel_list(channel_list):
            output_file.write(f"#EXTINF:-1 group-title=\"{channel_name}\",{name}\n")
            output_file.write(f"{url}\n")




#
output11_file_path = f"C/dan"

limited_channels = limit_channel_list(channel_list)

with open(output11_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write('#EXTM3U\n')  # 写入第一行
    for channel_name, channel_list in channel_lists.items():
        written_channels = set()  # 用于记录已经写入的频道名称
        for name, url in limit_channel_list(channel_list):
            if name not in written_channels:
                output_file.write(f"#EXTINF:-1 group-title=\"{channel_name}\",{name}\n")
                output_file.write(f"{url}\n")
                written_channels.add(name)
        output_file.write("\n")



            
            

print("\n已完成")
