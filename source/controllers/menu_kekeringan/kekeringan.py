from controllers.menu_kekeringan import KekeringanController
from helpers.playwright_manager import PlaywrightManager
from helpers.save_json import SaveJson
from helpers.upload_files3 import upload_to_s3

from bs4 import BeautifulSoup

import asyncio

class Kekeringan(KekeringanController):
    def __init__(self, *args, **kwargs):
        super(Kekeringan, self).__init__(*args, **kwargs)


    async def handler(self):
        try:
            await PlaywrightManager().one_page(self._url, self.script_playwright, self.headless)
        except Exception as e:
            self.log.error(e)

    async def script_playwright(self, page, _):
        self.log.info("Script Playwright started")

        i = 2
        for _ in range(2):
            await page.locator("#frame").content_frame.locator(".loading-indicator").wait_for(state="hidden", timeout=60000)
            await page.locator("#frame").content_frame.get_by_role("button", name="Layers", exact=True).click()
            await asyncio.sleep(2)
            await page.frame_locator("#frame").get_by_role("button", name="").click()
            await asyncio.sleep(2)
            chekcbox_locator = page.frame_locator("#frame").locator(".esriCheckbox")

            await asyncio.sleep(2)

            if i > 2:
                if await chekcbox_locator.nth(i-1).is_checked():
                    await chekcbox_locator.nth(i-1).uncheck()
                    if await chekcbox_locator.nth(i-2).is_checked():
                        await chekcbox_locator.nth(i-2).uncheck()

            sub_title = page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li/div[2]/div/div[1]/ul/li[{i-1}]/div/div/label")
            sub_title_text = await sub_title.inner_text()
            if not await chekcbox_locator.nth(i).is_checked():
                await chekcbox_locator.nth(i).check()

                if not await chekcbox_locator.nth(i+1).is_checked():
                    await chekcbox_locator.nth(i+1).check()

            await page.locator("#frame").content_frame.get_by_role("button", name="").click()
            i += 1

            title = await page.locator("#frame").content_frame.locator("#title").inner_text()

            filename = sub_title_text.replace(" ", "_").lower()
            await self.legend_ss(page, filename)
            await page.screenshot(path=f"data/menu_kekeringan/jpg/{filename}_map.jpg")

            await self.mapping_data(filename, title, sub_title_text)


    async def legend_ss(self, page, filename):
        await page.locator("#frame").content_frame.get_by_role("button", name="Legend").click()
        legend = page.locator("#frame").content_frame.locator("#pageBody_legend")
        await legend.screenshot(path=f"data/menu_kekeringan/jpg/{filename}_legend.jpg")
        await page.locator("#frame").content_frame.get_by_label("Close legend").click()
        
        await asyncio.sleep(10)


    async def mapping_data(self, filename, title, sub_title):
        path_data_raw = [
            f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/banjir_dan_kekeringan/json/{filename}.json",
            f"s3://ai-pipeline-raw-data/data/data_gambar_1/kementan/siperditan/banjir_dan_kekeringan/jpg/{filename}_legend.jpg",
            f"s3://ai-pipeline-raw-data/data/data_gambar_1/kementan/siperditan/banjir_dan_kekeringan/jpg/{filename}_map.jpg",
        ]

        local_path = [
            f"data/menu_kekeringan/json/{filename}.json",
            f"data/menu_kekeringan/jpg/{filename}_legend.jpg",
            f"data/menu_kekeringan/jpg/{filename}_map.jpg",
        ]

        data = {
            "filename_gambar": [
                f"{filename}_legend.jpg",
                f"{filename}_map.jpg",
            ]
        }

        json_metadata = SaveJson(
            self._url,
            ["bdsp2.pertanian.go.id", "siperditan", "menu kekeringan"],
            "siperditan", 
            title,
            sub_title,
            None, None, None, None, None, None,
            path_data_raw,
            None,
            "Indonesia",
            "provinsi, kabupaten/kota",
            data
            )
        
        datas = json_metadata.mapping()

        if self.destination_name == "file":
            await json_metadata.save_json_local(f"{filename}.json", "data/menu_kekeringan/json/")

        if self.destination_name == "s3":
            await upload_to_s3(local_path, path_data_raw)