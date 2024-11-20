from loguru import logger
import argparse
import asyncio


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Argument parser")
    parser.add_argument("-c", "--config", dest="config", help="Config file", default="config.ini")
    parser.add_argument("-d", "--destination", dest="destination", type=str)
    parser.add_argument("-o", "--output", dest="output", type=str)


    sub_parser = parser.add_subparsers(title="action", help="-h / --help to see usage")
    parser_crawler = sub_parser.add_parser("crawler")
    parser_crawler.set_defaults(which="crawler")
    parser_crawler.add_argument("-m", "--mode", dest="mode", type=str)
    parser_crawler.add_argument("-t", "--type", dest="type", type=str)
    parser_crawler.add_argument("-l", "--headless", dest="headless",  action="store_true", help="Run in headless mode")

    args = parser.parse_args()

    if args.which == "crawler":
        if args.mode == "siperditan":
            if args.type == "kekeringan":
                logger.info("Crawler mode: Siperditan - peta sebaran banjir dan kekeringan")
                from controllers.menu_kekeringan.kekeringan import Kekeringan
                c = Kekeringan(**args.__dict__)
                asyncio.run(c.main())

            elif args.type == "hukum":
                logger.info("Crawler mode: Siperditan - dasar hukum")
                from controllers.nav_hukum.hukum import Hukum
                c = Hukum(**args.__dict__)
                asyncio.run(c.main())

            elif args.type == "perkebunan":
                logger.info("Crawler mode: Siperditan - Perkebunan")
                from controllers.perkebunan.get_images_map import Perkebunan
                c = Perkebunan(**args.__dict__)
                asyncio.run(c.main())

            elif args.type == "tanaman_pangan":
                logger.info("Crawler mode: Siperditan - Tanaman Pangan")
                from controllers.tanaman_pangan.get_images import TanamanPangan
                c = TanamanPangan(**args.__dict__)
                asyncio.run(c.main())

            elif args.type == "curah_hujan":
                logger.info("Crawler mode: Siperditan - Curah Hujan")
                from controllers.curah_hujan.get_image import CurahHujan
                c = CurahHujan(**args.__dict__)
                asyncio.run(c.main())

            elif args.type == "prediksi":
                logger.info("Crawler mode: Siperditan - prediksi El Nino dan La Nina")
                from controllers.prediksi_elnino_dan_lanina.get_image import PrediksiElla
                c = PrediksiElla(**args.__dict__)
                asyncio.run(c.main())

            elif args.type == "perubahan_suhu":
                logger.info("Crawler mode: Siperditan - Perubahan Suhu di Indonesia")
                from controllers.data_tabular.get_tabular import DataTabular
                c = DataTabular(**args.__dict__)
                asyncio.run(c.main())