from helpers.playwright_manager import PlaywrightManager
from helpers.save_json import SaveJson
from helpers.file_downloader import download_file
from helpers.upload_files3 import upload_to_s3
from controllers.curah_hujan import CurahHujanController

import asyncio

class CurahHujan(CurahHujanController):
    def __init__(self, *args, **kwargs):
        super(CurahHujan, self).__init__(*args, **kwargs)
        self._url = "https://bdsp2.pertanian.go.id/siperditan/menu_perkcurahhujan.php"

    async def handler(self):
        await self.base_controller()

    async def base_controller(self):
        await PlaywrightManager().one_page(self._url, self.script_pw, self.headless)

    async def script_pw(self, page, _):
        print("Starting Script")


        # ? layers
        frame = page.frame_locator("#frame").frame_locator("internal:text=\"View Larger Map</a></small><\"i")
        
        await frame.locator(".loading-indicator").wait_for(state="hidden", timeout=60000)

        await frame.get_by_role("button", name="Layers").click()
        await asyncio.sleep(2)
        await frame.get_by_role("button", name="").click()
        await asyncio.sleep(2)

        checkboxes = await frame.locator("input.esriCheckbox").element_handles()

        i = 1
        for checkbox in checkboxes:
            if i != 1:
                if i == 2:
                    await checkbox.click()

                await checkbox.click()
                await asyncio.sleep(2)

                await frame.get_by_role("tab", name="Legend").click()

                title_locator = frame.locator("h1#title")
                sub_title_element = frame.locator("//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li/div[2]/div/div[2]/div/div[1]/div/table[1]/tbody/tr/td")


                title = await title_locator.inner_text()
                sub_title = await sub_title_element.inner_text()

                range_data = ''.join(filter(str.isdigit, sub_title))
                filename = sub_title.replace(" ","_").replace(".tif", "").lower().replace(")","")

                if i == 2:
                    await self.pdf_handle("https://bdsp2.pertanian.go.id/siperditan/rekomenpdf/iklim/Analisis%20dan%20Prediksi%20Curah%20Hujan%20Bln%20Agustus%202024%20-%20Februari%202025.pdf", title.replace(" ","_").lower(), title)

                legend_container = frame.get_by_role("tabpanel")
                await legend_container.screenshot(path=f"data/curah_hujan/png/{filename}_legend.png")

                await frame.get_by_label('Close layers').click()

                map = frame.locator("#mapDiv_container")
                await map.screenshot(path=f"data/curah_hujan/png/{filename}_map.png")
                await asyncio.sleep(1)


                await frame.get_by_role("button", name="Layers").click()
                await frame.get_by_role("tab", name="Sublayers").click()
                await checkbox.click()

                path_data_raw = [
                    f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/prakiraan_curah_hujan_bulanan/json/{filename}.json",
                    f"s3://ai-pipeline-raw-data/data/data_gambar_1/kementan/siperditan/prakiraan_curah_hujan_bulanan/png/{filename}_map.png",
                    f"s3://ai-pipeline-raw-data/data/data_gambar_1/kementan/siperditan/prakiraan_curah_hujan_bulanan/png/{filename}_legend.png"
                ]

                path_data_local = [
                    f"data/curah_hujan/json/{filename}.json",
                    f"data/curah_hujan/png/{filename}_map.png",
                    f"data/curah_hujan/png/{filename}_legend.png"
                ]

                data = {
                    "filename_gambar" : [
                        f"{filename}_map.png",
                        f"{filename}_legend.png"
                    ]
                }

                await SaveJson(self._url, ["bdsp2.pertanian.go.id", "Prakiraan Curah Hujan Bulanan"], "siperditan", title, sub_title, range_data, None, None, None, None, None, path_data_raw, "Indonesia", "Nasional", "Crawling data", data).save_json_local(f"{filename}.json", "data/curah_hujan/json")
                await upload_to_s3(path_data_local, path_data_raw)
            i+=1


    async def pdf_handle(self, url, filename, title):
        path_data_raw = [
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/prakiraan_curah_hujan_bulanan/json/{filename}.json",
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/prakiraan_curah_hujan_bulanan/pdf/{filename}.pdf"
        ]

        path_data_local = [
            f"data/curah_hujanjson/{filename}.json",
            f"data/curah_hujan/pdf/{filename}.pdf"
        ]
        
        data = {
            "filename_pdf": [
                f"{filename}.pdf"
            ]
        }
        await SaveJson(self._url, ["bdsp2.pertanian.go.id", "Prakiraan Curah Hujan Bulanan"], "siperditan", title, None, None, None, None, None, None, None, path_data_raw, "Indonesia", "Nasional", "Crawling data", data).save_json_local(f"{filename}.json", "data/curah_hujan/json")  
        await download_file(url, f"{filename}.pdf", "data/curah_hujan/pdf/")
        if self.destination_name == "s3":
            await upload_to_s3(path_data_local, path_data_raw)
            