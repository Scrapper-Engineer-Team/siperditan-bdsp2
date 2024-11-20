from controllers.tanaman_pangan import TanamanPanganController
from helpers.playwright_manager import PlaywrightManager
from helpers.save_json import SaveJson
from helpers.file_downloader import download_file
from helpers.upload_files3 import upload_to_s3
from helpers.html_parser import HtmlParser

import requests
import asyncio

class TanamanPangan(TanamanPanganController):
    def __init__(self, *args, **kwargs):
        super(TanamanPangan, self).__init__(*args, **kwargs)
        self.layer_text = ""
        self.title = ""


    async def handler(self):
        try:
            await PlaywrightManager().one_page(self._url, self.get_image, self.headless)
        except Exception as e:
            self.log.error(e)



    async def get_image(self, page, _):
        self.log.info("Getting image") 
        await self.pdf_download() 
        await asyncio.sleep(10)

        frame = page.frame_locator("#frame")

        await self.setup(frame)
        
        title = await frame.get_by_role("heading", name="Peta Sebaran OPT Tanaman").inner_text()
        self.title = title
        
        li_layers = frame.locator("ul.esriList > li.esriLayer")
        li_layers_counts = await li_layers.count()

        for i in range(0, li_layers_counts-3):
            li = li_layers.nth(i)
            layer_text = await li.locator("div.esriTitle:nth-child(1) > div.esriTitleContainer:nth-child(1) > label.esriLabel:nth-child(3)").inner_text()
            self.layer_text = layer_text
            if i != 0:
                await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[1]/div/input").uncheck()
            await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i+1}]/div[1]/div/input").check()
            await asyncio.sleep(3)

            if layer_text == "EWS Serangan BLB":
                await self.one_checkbox(page, frame, i)
            elif layer_text == "Kategori Wilayah Serangan OPT":
                await self.three_checkbox(page, frame, i)
            else:
                await self.two_checkbox(page, frame, i)
        await asyncio.sleep(5)




    async def one_checkbox(self, page, frame, index):
        await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[1]/div/div[1]").click()
        sublayer_text = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li[1]/div/div/label").inner_text()
        await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li[1]/div/div/input").check()

        await frame.get_by_label("Close layers").click()
        await asyncio.sleep(5)

        path_image =f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/png/"
        filename = sublayer_text.replace(" ","_").lower()
        try:
            await page.screenshot(path=f"{path_image}/{filename}_map.png")
            await self.get_legend(frame, filename, path_image)
            self.log.info("Image saved")
        except Exception as e:
            self.log.error("failed taking screenshot")


        local_path = [
            f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/json/{filename}.json",
            f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/png/{filename}_map.png",
            f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/png/{filename}_legend.png"
        ]


        path_data_raw = [
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/json/{filename}.json",
            f"s3://ai-pipeline-raw-data/data/data_gambar/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/png/{filename}_map.png",
            f"s3://ai-pipeline-raw-data/data/data_gambar/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/png/{filename}_legend.png"
        ]
        data = {
            "layer" : self.layer_text,
            "sublayer" : sublayer_text,
            "filename_image" : [
                f"{filename}_map.png",
                f"{filename}_legend.png"
            ]
        }
        metadata = SaveJson(self._url, self.tag, self.source, self.title, None, None, None, None, None, None, None, path_data_raw, None, "Indonesia", "Nasional", data)
        await metadata.save_json_local(f"{filename}.json", f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/json/")
        await upload_to_s3(local_path, path_data_raw)




    async def three_checkbox(self, page, frame, index):
        await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[1]/div/div[1]").click()
        await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/div/div/input").check()
        sublayer_text = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/div/div/label").inner_text()

        subsublayer_count = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li").count()
        for j in range(1, subsublayer_count+1):
            subsublayer_text = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/div/div/label").inner_text()
            if j != 1:
                await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j-1}]/div/div/input").uncheck()
            await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/div/div/input").check()

            subsubsublayer_count = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/ul/li").count()
        
            for k in range(1, subsubsublayer_count+1):
                subsubsublayer_text = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/ul/li[{k}]/div/div/label").inner_text()
                if k!= 1:
                    await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/ul/li[{k-1}]/div/div/input").uncheck()
                await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/ul/li[{k}]/div/div/input").check()

                await frame.get_by_label("Close layers").click()
                await asyncio.sleep(3)

                path_image =f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/png/"
                filename = subsubsublayer_text.replace(" ","_").lower()
                await asyncio.sleep(5)

                path_data_raw = [
                    f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/json/{filename}.json",
                    f"s3://ai-pipeline-raw-data/data/data_gambar/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/png/{filename}_map.png",
                    f"s3://ai-pipeline-raw-data/data/data_gambar/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/png/{filename}_legend.png"
                ]

                local_path = [
                    f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/json/{filename}.json",
                    f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/png/{filename}_map.png",
                    f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/png/{filename}_legend.png",
                ]

                data = {
                    "layer" : self.layer_text,
                    "sublayer" : sublayer_text,
                    "subsublayer" : subsublayer_text,
                    "subsubsublayer" : subsubsublayer_text,
                    "filename_image" : [
                        f"{filename}_map.png",
                        f"{filename}_legend.png"
                    ]
                }
                metadata = SaveJson(self._url, self.tag, self.source, self.title, None, None, None, None, None, None, None, path_data_raw, None, "Indonesia", "Nasional", data)
                await metadata.save_json_local(f"{filename}.json", f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/{subsublayer_text.replace(" ","_").lower()}/json/")

                try:
                    await page.screenshot(path=f"{path_image}/{filename}_map.png")
                    await self.get_legend(frame, filename, path_image)
                    self.log.info("Image saved")
                except Exception as e:
                    self.log.error("failed taking screenshot")

                await upload_to_s3(local_path, path_data_raw)


            await asyncio.sleep(5)




    async def two_checkbox(self, page, frame, index):
        await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[1]/div/div[1]").click()
        sublayer_text = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/div/div/label").inner_text()
        await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/div/div/input").check()
        subsublayer_count = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li").count()
        for j in range(1, subsublayer_count+1):
            subsublayer_text = await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/div/div/label").inner_text()
            if j != 1:
                await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j-1}]/div/div/input").uncheck()
                await asyncio.sleep(2)
            await frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{index+1}]/div[2]/div/div[1]/ul/li/ul/li[{j}]/div/div/input").check()
            await asyncio.sleep(2)



            await frame.get_by_label("Close layers").click()
            await asyncio.sleep(3)

            path_image = f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/png/"
            filename = subsublayer_text.replace(" ","_").lower()
            await asyncio.sleep(5)

            local_path = [
                f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/json/{filename}.json",
                f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/png/{filename}_legend.png",
                f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/png/{filename}_map.png",
            ]

            path_data_raw = [
                f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/json/{filename}.json",
                f"s3://ai-pipeline-raw-data/data/data_gambar/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/png/{filename}_map.png",
                f"s3://ai-pipeline-raw-data/data/data_gambar/kementan/siperditan/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/png/{filename}_legend.png"
            ]
            data = {
                "layer" : self.layer_text,
                "sublayer" : sublayer_text,
                "subsublayer" : subsublayer_text,
                "filename_image" : [
                    f"{filename}_map.png",
                    f"{filename}_legend.png"
                ]
            }
            metadata = SaveJson(self._url, self.tag, self.source, self.title, None, None, None, None, None, None, None, path_data_raw, None, "Indonesia", "Nasional", data)
            await metadata.save_json_local(f"{filename}.json", f"data/tanaman_pangan/{self.layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/json")
            await upload_to_s3(local_path, path_data_raw)

            try:
                await page.screenshot(path=f"{path_image}/{filename}_map.png")
                await self.get_legend(frame, filename, path_image)
                self.log.info("Image saved")
            except Exception as e:
                self.log.error("failed taking screenshot")





    async def get_legend(self, frame, filename, path_image):
        await frame.get_by_role("button", name="Legend").click()
        await asyncio.sleep(3)
        ss_locator = frame.locator("//html/body/div[1]/div[4]/div[1]/div[1]/div/div")
        await ss_locator.screenshot(path=f"{path_image}/{filename}_legend.png")
        await frame.get_by_role("button", name="Layers").click()



    async def setup(self, frame):
        await frame.get_by_label("Laporan Serangan OPT").uncheck()
        await asyncio.sleep(4)


    async def pdf_download(self):
        url = "https://bdsp2.pertanian.go.id/siperditan/index.php"
        response = requests.get(url)
        html = response.text
        title = (HtmlParser().bs4_parser(html, "#myCarousel > div:nth-child(2) > h1:nth-child(1)"))[0].text
        sub_title = (HtmlParser().bs4_parser(html, "#myCarousel > div:nth-child(2) > p:nth-child(2) > strong:nth-child(1)"))[0].text
        category = (HtmlParser().bs4_parser(html, "#opt-tab"))[0].text
        sub_category = (HtmlParser().bs4_parser(html, "#opt1-tab"))[0].text
        desc = (HtmlParser().bs4_parser(html, "#opt1 > div:nth-child(1) > div:nth-child(1) > p:nth-child(1)"))[0].text
        link_pdf = (HtmlParser().bs4_parser(html, "#opt1 > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > p:nth-child(1) > a:nth-child(1)"))[0]['href']
        if "http" not in link_pdf:
            link_pdf = f"https://bdsp2.pertanian.go.id/siperditan/{link_pdf}"

        filename = "siperditan_tanaman_pangan"

        data = {
            "filename_pdf" : [
                f"{filename}.pdf"
            ]
        }

        local_path = [
            f"data/tanaman_pangan/json/{filename}.json",
            f"data/tanaman_pangan/pdf/{filename}.pdf"
        ]

        path_data_raw = [
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/tanaman_pangan/json/{filename}.json",
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/tanaman_pangan/pdf/{filename}.pdf"
        ]
        metadata = SaveJson(url, self.tag, self.source, title, sub_title, None, None, None, desc, category, sub_category, path_data_raw, None, "Indonesia", "Nasional", data)
        await metadata.save_json_local(f"{filename}.json", "data/tanaman_pangan/json/")
        await download_file(link_pdf ,f"{filename}.pdf", "data/tanaman_pangan/pdf/")
        if self.destination_name == "s3":
            await upload_to_s3(local_path, path_data_raw)