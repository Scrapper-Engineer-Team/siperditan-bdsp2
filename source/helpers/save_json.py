import json
import os
import aiofiles
from datetime import datetime

class SaveJson:

    def __init__(self, url, tags, source, title, sub_title, range_data, create_date, update_date, desc, category, sub_category, path_data_raw, table_name, country_name, level, data):
        self.url = url
        self.tags = tags
        self.source = source
        self.title = title
        self.sub_title = sub_title
        self.range_data = range_data
        self.create_data = create_date
        self.update_data = update_date
        self.desc = desc
        self.category = category
        self.sub_category = sub_category
        self.path_data_raw = path_data_raw
        self.table_name = table_name
        self.country_name = country_name
        self.level = level
        self.data = data


    async def save_json_local(self, filename, *folders):
        directory = os.path.join(*folders)
        
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as json_file:
            data = self.mapping()
            await json_file.write(json.dumps(data, ensure_ascii=False))

    def mapping(self):
        now = datetime.now()
        crawling_time = now.strftime('%Y-%m-%d %H:%M:%S')
        crawling_time_epoch = int(now.timestamp())

        data_json = {
            "link": getattr(self, 'url', ""),
            "tags": getattr(self, 'tags', []),
            "source": getattr(self, 'source', ""),
            "title": getattr(self, 'title', ""),
            "sub_title": getattr(self, 'sub_title', ""),
            "range_data": getattr(self, 'range_data', ""),
            "create_date": getattr(self, 'create_data', ""),
            "update_date": getattr(self, 'update_data', ""),
            "desc": getattr(self, 'desc', ""),
            "category": getattr(self, 'category', ""),
            "sub_category": getattr(self, 'sub_category', ""),
            "path_data_raw": getattr(self, 'path_data_raw', ""),
            "crawling_time": crawling_time,
            "crawling_time_epoch": crawling_time_epoch,
            "table_name": getattr(self, 'table_name', ""),
            "country_name": getattr(self, 'country_name', "Indonesia"),
            "level": getattr(self, 'level', "Nasional"),
            "stage": "Crawling data",
            "data": getattr(self, 'data', "")
        }
        
        return data_json