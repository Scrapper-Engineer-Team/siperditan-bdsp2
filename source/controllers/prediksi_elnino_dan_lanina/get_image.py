import os
import json
import aiohttp
from bs4 import BeautifulSoup

from controllers.prediksi_elnino_dan_lanina import PrediksiEllaController
from helpers.file_downloader import download_file
from helpers.html_parser import HtmlParser
from helpers.save_json import SaveJson
from helpers.upload_files3 import upload_to_s3

class PrediksiElla(PrediksiEllaController):
    def __init__(self, *args, **kwargs):
        super(PrediksiElla, self).__init__(*args, **kwargs)


    async def handler(self):
        try:
            await self.get_image()
        except Exception as e:
            self.log.error(e)


    async def get_image(self):
        file_img = []
        path_data_raws = []

        await self.download_pdf()

        html = await self.fetch_page()
        if html:
            image_selector = [
                "div.px-1:nth-child(2) > div:nth-child(1) > img:nth-child(1)",
                "div.px-1:nth-child(3) > div:nth-child(1) > img:nth-child(1)"
            ]
            i = 1

            for selector in image_selector:
                image = (HtmlParser().bs4_parser(html, selector))[0]
                src = image.get("src")
                if "http" not in src:
                    src = "https://bdsp2.pertanian.go.id/siperditan/" + src
                filename = f"menu_enso_{i}.png"
                file_img.append(filename)
                await download_file(src, filename, f"data/prediksi_elnino_dan_lanina/png/")
                i += 1

                path_data_raws.append(f"s3://ai-pipeline-raw-data/data/data_gambar_1/kementan/siperditan/prediksi_elnino_dan_lanina/png/{filename}")

            filename_json = f"menu_enso.json"
            path_data_raws.append(f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/prediksi_elnino_dan_lanina/json/{filename_json}")
            data = {
                "filename" : file_img
            }
            local_path = [
                f"data/prediksi_elnino_dan_lanina/png/menu_enso_1.png",
                f"data/prediksi_elnino_dan_lanina/png/menu_enso_2.png",
                f"data/prediksi_elnino_dan_lanina/json/{filename_json}",
            ]
            await SaveJson(self._url, ["https://bdsp2.pertanian.go.id/siperditan/", "siperditan", "bdsp2.pertanian.go.id"], self.source, None, None, None, None, None, None, None, None, path_data_raws, None, "Indonesia", "Nasional", data).save_json_local(filename_json, "data/prediksi_elnino_dan_lanina/json/")
            await upload_to_s3(local_path, path_data_raws)
            


    async def fetch_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url) as response:
                if response.status != 200:
                    self.log.error(f"Failed to fetch the page. Status code: {response.status}")
                    return None
                else:
                    html = await response.text()
                    return html
                
    
    async def download_pdf(self):
        filename = "menu_enso.pdf"
        filename_json = "menu_enso_pdf.json"
        await download_file("https://bdsp2.pertanian.go.id/siperditan/rekomenpdf/enso/25062020_Analisis%20dan%20Prediksi%20Iklim%20Indonesia.pdf", filename, "data/prediksi_elnino_dan_lanina/pdf/")
        data = {
            "filename" : [filename]
        }

        path_data_raws = [
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/prediksi_elnino_dan_lanina/json/{filename_json}",
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/prediksi_elnino_dan_lanina/pdf/{filename}"
        ]

        local_path = [
            f"data/prediksi_elnino_dan_lanina/json/{filename_json}",
            f"data/prediksi_elnino_dan_lanina/pdf/{filename}"
        ]
        await SaveJson(self._url, ["https://bdsp2.pertanian.go.id/siperditan/", "siperditan", "bdsp2.pertanian.go.id"], self.source, None, None, None, None, None, None, None, None, path_data_raws, None, "Indonesia", "Nasional", data).save_json_local(filename_json, "data/prediksi_elnino_dan_lanina/json/")
        if self.destination_name == "s3":
            await upload_to_s3(local_path, path_data_raws)