from helpers.playwright_manager import PlaywrightManager
from helpers.html_parser import HtmlParser
from helpers.kafka import Producer
from helpers.upload_files3 import upload_to_s3
from controllers.data_tabular import DataTabularController

from random import randint
from datetime import datetime
from loguru import logger

import pprint as pp
import asyncio

import os
import json

class DataTabular(DataTabularController):
    def __init__(self, *args, **kwargs):
        super(DataTabular, self).__init__(*args, **kwargs)
        self._url = "https://bdsp2.pertanian.go.id/siperditan/nav_datatabular_json.php"
        self.tabs = kwargs.get('tabs', 1)

        # ? kafka 
        self.topic = "data-knowledge-repo-general_10"
        self.bootstrap_servers = ['kafka01.research.ai', 'kafka02.research.ai', 'kafka03.research.ai']
        self.producer = Producer(self.bootstrap_servers)


    async def handler(self):
            await self.base_controller()


    async def base_controller(self):
        current_year = datetime.now().year
        years = list(range(2019, current_year + 1))
        await PlaywrightManager().multiple_pages(self._url, self.script_pw, years, self.headless, self.tabs)


    async def script_pw(self, page, task):
        r_month = 1
        r_tanggal = 1
        year = task

        loop_count = 0


        while True:
            try:
                if loop_count != 0:
                    await page.reload(timeout=600000)
                    await page.wait_for_load_state('load', timeout=600000)

                await page.locator("#tahun").select_option(f"{year}")
                for month in range(r_month, 13):
                    formatted_month = str(month).zfill(2)
                    await page.locator("#bulan").select_option(f"{formatted_month}")
                    r_month = month
                    await asyncio.sleep(1)
                    for tanggal in range(r_tanggal, 32):
                        formatted_tanggal = str(tanggal).zfill(2)
                        await page.locator("#tanggal").select_option(f"{formatted_tanggal}")
                        r_tanggal = tanggal
                        await asyncio.sleep(1)

                        filter_button = page.get_by_role("button", name="Filter")
                        await filter_button.wait_for(state="visible")
                        await filter_button.click()

                        await asyncio.sleep(2)

                        html = await page.content()
                        title = (await HtmlParser.bs4_parser(html, "body > div.page-container > div > div > div > div > div.px-3.py-5.pt-md-5.pb-md-4.mx-auto.text-center > h1"))[0].text.strip()
                        datas = await self.table_click(page)
                        now = datetime.now()

                        if title:
                            filename = f"{title}".replace(" ","_").lower().replace("-","_").replace("\\", "_").replace("/","_")

                        if filename:
                            async with page.expect_download() as download_info:
                                await page.get_by_role("button", name="PDF").click()
                            download_pdf = await download_info.value
                            await self.download_files(f"{filename}.pdf", download_pdf, f"data/data_tabular/{year}/{month}/pdf")

                            async with page.expect_download() as download_info:
                                await page.get_by_role("button", name="Excel").click()
                            download_xlsx = await download_info.value
                            await self.download_files(f"{filename}.xlsx", download_xlsx, f"data/data_tabular/{year}/{month}/xlsx")

                        path_data_raw = [
                            "kafka: data-knowledge-repo-general_10",
                            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/data_tabular/{year}/pdf/{filename}.pdf",
                            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/data_tabular/{year}/xlsx/{filename}.xlsx"
                        ]

                        path_data_raw_files = [
                            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/data_tabular/{year}/pdf/{filename}.pdf",
                            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/data_tabular/{year}/xlsx/{filename}.xlsx"
                        ]
                        path_data_local_files = [
                            f"data/data_tabular/{year}/{month}/pdf/{filename}.pdf",
                            f"data/data_tabular/{year}/{month}/xlsx/{filename}.xlsx"
                        ]

                        metadata = {
                            "link": self._url,
                            "source":  'siperditan',
                            "title" : title,
                            "tags": ["bdsp2.pertanian.go.id", "Data Tabular"],
                            "sub_title":  None,
                            "range_data":  year,
                            "create_date":  f"{tanggal}-{month}-{year}",
                            "update_date":  None,
                            "desc":  None,
                            "category":  None,
                            "sub_category":  None,
                            "path_data_raw":  path_data_raw,
                            "crawling_time": now.strftime('%Y-%m-%d %H:%M:%S'),
                            "crawling_time_epoch": int(now.timestamp()),
                            "country_name": "Indonesia",
                            "level": "Nasional",
                            "stage": "Crawling data",
                            "data" : datas
                        }

                        logger.info(title)


                        os.makedirs(f"data/data_tabular/{year}/{month}/json/", exist_ok=True)
                        with open(f"data/data_tabular/{year}/{month}/json/{filename}.json", "w") as f:
                                json.dump(metadata, f, indent=4)

                        if self.destination_name == "kafka":
                            await upload_to_s3(path_data_local_files, path_data_raw_files)

                        if self.destination_name == "kafka":
                            await self.producer.send(self.topic, metadata)

                        r_tanggal = tanggal + 1

                    r_tanggal = 1
                    r_month = month + 1
                break
            except Exception as e:
                loop_count += 1
                logger.error(f"Error encountered tab year {year}: {e}. Reloading and retrying...")
                await asyncio.sleep(randint(2, 10))


    async def table_click(self, page):
        all_data_tables = []

        next_button = page.locator(".paginate_button.next")

        while True:
            html = await page.content()
            data_table = await self.parsing_table(html)
            if data_table:
                all_data_tables.extend(data_table)

            classes = await next_button.get_attribute('class')
            if 'disabled' in classes:
                break
            
            await next_button.click()
            await asyncio.sleep(1) 

        return all_data_tables


    async def parsing_table(self, html):
        datas = []
        try:
            thead = (await HtmlParser.bs4_parser(html, "#myTable > thead:nth-child(1) > tr:nth-child(1)"))
            th_elements = thead[0].find_all("th")
            [th.text.strip for th in th_elements]

            tbody = (await HtmlParser.bs4_parser(html, "#myTable > tbody:nth-child(2)"))
            tr_elements = tbody[0].find_all()
            for tr in tr_elements:
                td_elements = tr.find_all("td")
                data = {th.text.strip().replace(" ","_").lower(): td.text.strip() for th, td in zip(th_elements, td_elements)}
                if data:
                    datas.append(data)
            return datas

        except Exception as e:
            logger.error(e)


    async def download_files(self, filename, download_info, path):
        if filename != ".pdf" or filename != ".xlsx":
            save_folder = path
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            file_path = os.path.join(save_folder, filename)
            await download_info.save_as(file_path)