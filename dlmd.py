#coding=utf-8

from ckiptagger import data_utils
data_utils.download_data_gdown("./")

# import datetime
# from ckiptagger import WS
# from fuzzywuzzy import fuzz, process

# ws = WS("./data")
# loc_table = ["基隆端", "基隆", "八堵", "大華系統", "五堵", "汐止", "汐止系統", "高架汐止端", "東湖", "內湖", "圓山", "台北", "三重", "五股轉接道", "五股", "高公局", "泰山轉接道", "林口", "桃園", "機場系統", "中壢服務區", "內壢", "中壢轉接一", "中壢轉接二", "中壢", "平鎮系統", "幼獅", "楊梅", "高架楊梅端", "湖口", "湖口服務區", "竹北", "新竹", "新竹系統", "頭份", "頭屋", "苗栗", "銅鑼", "三義", "泰安服務區", "后里", "台中系統", "豐原", "大雅", "台中", "南屯", "王田", "彰化系統", "彰化", "埔鹽系統", "員林", "北斗", "西螺服務區", "西螺", "虎尾", "斗南", "雲林系統", "大林", "民雄", "嘉義", "水上", "嘉義系統", "新營服務區", "新營", "下營系統", "麻豆", "安定", "台南系統", "永康", "大灣", "仁德", "仁德系統", "仁德服務區", "路竹", "高科", "岡山", "楠梓", "鼎金系統", "高雄", "瑞隆路", "五甲系統", "五甲", "中山四路", "漁港路", "高雄端"]

# def parse_str(text):
#     data = ws([text])[0]

#     label = {"type":"","date":"","time":"","loc":"","loc_from":"","loc_to":"","Error":[]}
#     if any([("申報" in d or "report" in d) for d in data]):
#         label["type"] = "report"
#         loc_list = []
#         for i in range(len(data)):
#             if ":" in data[i]: # time
#                 label = parse_time(data,i,label)
#             elif "/" in data[i]: # date
#                 label = parse_date(data,i,label)
#             elif len(data[i]) >= 2: # loc
#                 try:
#                     blur_pro = process.extractOne(data[i], loc_table)
#                     if blur_pro[1] > 40:
#                         loc_list.append(blur_pro[0])
#                 except:
#                     print(data[i])
#         if len(loc_list) == 2:
#             label["loc_from"] = loc_list[0]
#             label["loc_to"] = loc_list[1]
#         else:
#             label["Error"].append("loc_from") 
#             label["Error"].append("loc_to") 
#     elif any([("看" in d,"搜尋" in d ,"查詢" in d or "query" in d or "查" in d) for d in data]):
#         label["type"]="query"
#         for i in range(len(data)):
#             if ":" in data[i]: # time
#                 label = parse_time(data,i,label)
#             elif "/" in data[i]: # date
#                 label = parse_date(data,i,label)
#             elif len(data[i]) >= 2: # loc
#                 try:
#                     blur_pro = process.extractOne(data[i], loc_table)
#                     if blur_pro[1] > 40:
#                         label["loc"] = blur_pro[0]
#                 except:
#                     label["Error"].append("loc") 
#                     print(data[i])
                
                
#     return label

# def parse_date(data,i,label):
#     if len(data[i])==1:
#         if (i != 0 or i != len(data)-1) and data[i-1].isnumeric() and data[i+1].isnumeric():
#             try:
#                 year = datetime.date.today().year
#                 datetime.date(year,int(data[i-1]),int(data[i+1]))
#                 label["time"] = data[i-1] + "/" + data[i+1]
#             except:
#                 label["Error"].append("date") 
#         else:
#             label["Error"].append("date") 
#     else:
#         data[i] = data[i].replace('月','')
#         data[i] = data[i].replace('日','')
#         data[i] = data[i].replace('號','')
#         date_data = data[i].split("/")
#         if len(date_data) == 2 and date_data[0].isnumeric() and date_data[1].isnumeric():
#             try:
#                 year = datetime.date.today().year
#                 datetime.date(year,int(date_data[0]),int(date_data[1]))
#                 label["date"] = date_data[0] + "/" + date_data[1]
#             except:
#                 label["Error"].append("date") 
#         else:
#             label["Error"].append("date") 
#     return label

# def parse_time(data,i,label):
#     if len(data[i])==1:
#         if (i != 0 or i != len(data)-1) and data[i-1].isnumeric() and data[i+1].isnumeric():
#             if 0 <= int(data[i-1]) <= 24 and 0 <= int(data[i+1]) < 60:
#                 label["time"] = data[i-1] + ":" + data[i+1]
#             else:
#                 label["Error"].append("time") 
#         else:
#             label["Error"].append("time") 
#     else:
#         time_data = data[i].split(":")
#         if len(time_data) == 2 and time_data[0].isnumeric() and time_data[1].isnumeric():
#             if 0 <= int(time_data[0]) <= 24 and 0 <= int(time_data[1]) < 60:
#                 label["time"] = time_data[0] + ":" + time_data[1]
#             else:
#                 label["Error"].append("time") 
#         else:
#             label["Error"].append("time") 
#     return label


# print(parse_str("我要查詢台北交流道1/2號12:20的交通狀況"))
# print(parse_str("我要申報台北交流道到新竹1/2號12:20的交通狀況"))