from controllers.perkebunan import Perkebunancontroller
from helpers.playwright_manager import PlaywrightManager
from helpers.save_json import SaveJson
from helpers.upload_files3 import upload_to_s3


import asyncio

class Perkebunan(Perkebunancontroller):
    def __init__(self, *args, **kwargs):
        super(Perkebunan,  self).__init__(*args, **kwargs)


    async def handler(self):
        try:
            await PlaywrightManager().one_page(self._url, self.get_images, self.headless)
        except Exception as e:
            self.log.error(e)

    async def get_images(self, page, _):
        self.log.info("get_images")

        await self.clean_cheked(page)

        await page.locator("#frame").content_frame.locator(".loading-indicator").wait_for(state="hidden", timeout=60000)
        await page.locator("#frame").content_frame.get_by_role("button", name="Layers", exact=True).click()

        title = await page.locator("#frame").content_frame.locator("//html/body/div[1]/div[3]/div[1]/header/hgroup/h1").inner_text()
        
        for i in range(1, 3):

            await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[1]/div/input").check()
            layer_text = await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[1]/div/label").inner_text()
            await asyncio.sleep(2)

            if i == 1:
                await page.locator("#frame").content_frame.get_by_role("button", name="").click()
            await asyncio.sleep(1)

            sublayers_count = await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li").count()

            for j in range(1, sublayers_count+1):
                await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li[{j}]/div/div/input").check()

                sublayer_text = await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li[{j}]/div/div/label").inner_text()
                await asyncio.sleep(1)

                subsublayers_count = await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li[{j}]/ul/li").count()
                for k in range(1, subsublayers_count+1):
                    await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li[{j}]/ul/li[{k}]/div/div/input").check()
                    subsublayers_text = await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li[{j}]/ul/li[{k}]/div/div/label").inner_text()

                    await asyncio.sleep(5)

                    filename = f"{subsublayers_text.replace(" ", "_").replace(".","_").replace("/","_").replace("\\","_").lower()}"
                    await page.locator("#frame").content_frame.get_by_label("Close layers").click()
                    await page.screenshot(path=f"data/perkebunan/jpg/{filename}_map.jpg")
                    await self.legends(page, filename)

                    data = {
                        "layer" : layer_text, 
                        "sublayer" : sublayer_text,
                        "subsublayer" : subsublayers_text,
                        "filename_image" : [
                            f"{filename}_map.jpg",
                            f"{filename}_legend.jpg"
                        ]
                    }

                    path_data_raw = [
                        f"s3://ai-pipeline-raw-data/data/data_statistics/kementan/siperditan/perkebunan/{layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/json/{filename}.json",
                        f"s3://ai-pipeline-raw-data/data/data_gambar_1/kementan/siperditan/perkebunan/{layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/jpg/{filename}_map.jpg",
                        f"s3://ai-pipeline-raw-data/data/data_gambar_1/kementan/siperditan/perkebunan/{layer_text.replace(" ","_").lower()}/{sublayer_text.replace(" ","_").lower()}/jpg/{filename}_legend.jpg",
                    ]
                    await self.metadata_handler(data, filename, title, layer_text, sublayer_text, path_data_raw)

                    local_path = [
                        f"data/perkebunan/json/{filename}.json",
                        f"data/perkebunan/jpg/{filename}_map.jpg",
                        f"data/perkebunan/jpg/{filename}_legend.jpg"
                    ]

                    if self.destination_name == "s3":
                        await upload_to_s3(local_path, path_data_raw)
                    

                    await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li[{j}]/ul/li[{k}]/div/div/input").uncheck()
                await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[2]/div/div[1]/ul/li[{j}]/div/div/input").uncheck()
            await page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[2]/div/div/div/div/ul/li[{i}]/div[1]/div/input").uncheck()

        await asyncio.sleep(5)
            


    async def metadata_handler(self, data, filename, title, category, sub_category, path_data_raw):
        datas = SaveJson(self._url, self.tags, self.source, title, None, None, None, None, None, category, sub_category, path_data_raw, None, "Indonesia", "nasioanl", data)
        await datas.save_json_local(f"{filename}.json", "data/perkebunan/json/")
        self.log.info("Successfully save metadata")


    async def legends(self, page, filename):
        await page.locator("#frame").content_frame.get_by_role("button", name="Legend").click()
        element = page.locator("#frame").content_frame.locator(f"//html/body/div[1]/div[4]/div[1]/div[1]/div/div")
        await element.screenshot(path=f"data/perkebunan/jpg/{filename}_legend.jpg")
        await page.locator("#frame").content_frame.get_by_role("button", name="Layers").click()


    async def clean_cheked(self, page):
        await page.locator("#frame").content_frame.get_by_role("button", name="Layers", exact=True).click()
        await page.locator("#frame").content_frame.get_by_role("menuitem", name="Prakiraan OPT Perkebunan ").get_by_role("button").click()
        await page.locator("#frame").content_frame.get_by_role("checkbox", name="Tembakau").uncheck()
        await page.locator("#frame").content_frame.get_by_role("checkbox", name="Kelapa Sawit").uncheck()
        await page.locator("#frame").content_frame.get_by_role("button", name="").click()
        await page.locator("#frame").content_frame.get_by_label("Prakiraan OPT Perkebunan").uncheck()
        await page.locator("#frame").content_frame.get_by_role("button", name="").click()
        await page.locator("#frame").content_frame.get_by_role("checkbox", name="Cengkeh", exact=True).uncheck()
        await page.locator("#frame").content_frame.get_by_role("checkbox", name="Tebu").uncheck()
        await page.locator("#frame").content_frame.get_by_role("checkbox", name="Cengkeh", exact=True).uncheck()
        await page.locator("#frame").content_frame.get_by_label("Kategori Endemis OPT").uncheck()
        await page.locator("#frame").content_frame.get_by_label("Close layers").click()
