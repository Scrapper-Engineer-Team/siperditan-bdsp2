import aiohttp
import re

from controllers.nav_hukum import HukumController
from helpers.html_parser import HtmlParser
from helpers.file_downloader import download_file
from helpers.save_json import SaveJson
from helpers.upload_files3 import upload_to_s3


class Hukum(HukumController):
    def __init__(self, *args, **kwargs):
        super(Hukum, self).__init__(*args, **kwargs)

    async def handler(self):
        try:
            await self.fetch_page()
        except Exception as e:
            self.log.error(e)

    async def fetch_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url) as response:
                if response.status != 200:
                    self.log.error(response.status)
                else:
                    html_content = await response.text()
                    title = (HtmlParser().bs4_parser(html_content, "h1.display-2"))[0].text

                    ul = (HtmlParser().bs4_parser(html_content, ".list-group"))[0]
                    links = ul.find_all("a")
                    link_data = [(a["href"], a.get_text(strip=True)) for a in links]
                    for href, text in link_data:
                        title_file = text
                        link = href
                        if "http" not in link:
                            link = f"https://bdsp2.pertanian.go.id/siperditan/{link}"

                        range_data = int(re.findall(r"\b20\d+\b", title_file)[0])
                        filename = title_file.replace(" ", "_").lower().replace(".","_").replace(":","")

                        path_data_raw = [
                            f"s3://ai-pipeline-raw-data/data/data_descriptive/kementan/siperditan/dasar_hukum/json/{filename}.json",
                            f"s3://ai-pipeline-raw-data/data/data_descriptive/kementan/siperditan/dasar_hukum/pdf/{filename}.pdf"
                        ]
                        data = {
                            "title_file" : title_file,
                            "filename_pdf" : [
                                f"{filename}.pdf"
                            ]
                        }

                        local_path = [
                            f"data/dasar_hukum/json/{filename}.json",
                            f"data/dasar_hukum/pdf/{filename}.pdf"
                        ]

                        metadata = SaveJson(self._url, self.tags, self.source, title, None, range_data, None, None, None, None, None, path_data_raw, None, "Indonesia", "  Nasional", data)
                        await metadata.save_json_local(f"{filename}.json", "data/dasar_hukum/json/")
                        await download_file(link, f"{filename}.pdf", "data/dasar_hukum/pdf/")
                        if self.destination_name == "s3":
                            await upload_to_s3(local_path, path_data_raw)