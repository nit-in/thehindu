#!/usr/bin/python3
import requests
import json
import re
import pdfkit
from pathlib import Path
import time
from datetime import datetime
import csv
import errno, os
import subprocess
import asyncio
import argparse


parser = argparse.ArgumentParser(description="The Hindu ops.")
parser.add_argument("-l", type=str, help="epaper")
parser.add_argument("-s", type=int, help="sp")

args = parser.parse_args()

story_id_url = args.l
sp = args.s

root_dir = "~/the_hindu/stories"

csv_dir_th = "~/the_hindu/csvs"

download_dir = Path(root_dir)
download_dir = download_dir.expanduser()


csv_download_dir = Path(csv_dir_th)
csv_download_dir = csv_download_dir.expanduser()
cwd = Path.cwd()

if download_dir.exists():

    print(f"{str(download_dir)} exists")
else:

    print(f"making {download_dir}")
    download_dir.mkdir(parents="True")


if csv_download_dir.exists():

    print(f"{str(csv_download_dir)} exists")
else:

    print(f"making {csv_download_dir}")
    csv_download_dir.mkdir(parents="True")


def txt_file(story_id):
    txtfile = Path(cwd, "record.txt")
    with open(str(txtfile), "a") as f:
        f.writelines(str(story_id) + "\n")


def csv_writer(csv_path, date, title, body, story_id_url):
    csv_file_path = Path(csv_path)
    csv_file_name = str(date) + ".csv"
    csv_file = Path(csv_file_path, csv_file_name)
    data = [str(date), str(title), str(body), str(story_id_url)]
    with open(csv_file, "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)


def check_pdf(pdf_name):
    try:
        pdf = Path(pdf_name)
        if pdf.exists():
            return True
        else:
            return False
    except OSError as e:
        if e.errno == errno.ENAMETOOLONG:
            print(f"{str(pdf_name)}\tfile name too long")
        else:
            pass


def check_edition(edition):
    ed = str(edition)
    ed = ed.lower()
    if "delhi" in ed:
        return True
    else:
        return False


def make_pdf(pdf_text, pdf_name):
    try:
        ops = {
            "quiet": "",
            "no-pdf-compression": "",
            "background": "",
            "page-size": "A4",
            "margin-top": "0.5in",
            "margin-right": "0.5in",
            "margin-bottom": "0.5in",
            "margin-left": "0.5in",
            "encoding": "UTF-8",
            "no-outline": None,
        }
        pdfkit.from_string(str(pdf_text), str(pdf_name), options=ops)
    except OSError as e:
        if e.errno == errno.ENAMETOOLONG:
            print(f"{str(pdf_name)}\tfile name too long")
        else:
            pass
    except TypeError:
        pass


async def id_links(start, finish):
    for i in range(start, finish):
        story_id = str(i)
        print(story_id)
        story_link = str(story_id_url) + story_id

        result = requests.get(story_link)
        await asyncio.sleep(5)
        data = json.loads(result.content)
        try:
            headline = str(data["StoryContent"][0]["Headlines"])
            body = str(data["StoryContent"][0]["Body"])
            article_date = str(data["Eddate"])
            csv_date = datetime.strptime(article_date, "%d/%m/%Y").strftime("%d-%b-%Y")
            ed_date = datetime.strptime(article_date, "%d/%m/%Y").strftime("%Y/%b/%d")
            edition = str(data["EditionName"])
            dateline = str(data["dateLine"])
            if dateline == "":
                dateline = "THE_HINDU_ED"
            else:
                dateline = dateline.lower().title()
                dateline = re.sub("\W+", "_", dateline)

            csvdata = [story_id, edition, dateline]
            csvf = str(csv_date) + ".csv"
            csvf_path = Path(cwd, csvf)
            with open(csvf_path, "a") as csvs_file:
                csvw = csv.writer(csvs_file)
                csvw.writerow(csvdata)

            if check_edition(str(edition)):
                dateline_ed_date = Path(ed_date, dateline)
                story_dir = Path(str(download_dir), str(dateline_ed_date))
                csv_dir = Path(str(csv_download_dir), str(dateline_ed_date))

                if story_dir.exists():
                    pass
                else:
                    story_dir.mkdir(parents="True")

                if csv_dir.exists():
                    pass
                else:
                    csv_dir.mkdir(parents="True")

                name = re.sub("\W+", "-", article_date) + re.sub("\W+", "_", headline)

                if len(name) > 200:
                    name = name[0:200]
                name_with_ext = name + str(story_id) + ".pdf"

                story_name = Path(story_dir, name_with_ext)

                pdf_text = str(
                    f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><p style='text-align:center'>DateLine : {dateline}</p><br><div style='text-align:center'{body}</div><body></html>"""
                )

                if check_pdf(str(story_name)):
                    print(f"\nAlready Downloaded:\t{story_name}\n")
                else:
                    csv_writer(csv_dir, csv_date, name, body, story_id)
                    txt_file(story_id)
                    make_pdf(str(pdf_text), str(story_name))

        except (TypeError, IndexError, ValueError, UnboundLocalError) as e:
            pass


async def main():
    await asyncio.gather(
        id_links(sp, sp + 1 * 1000),
        id_links(sp + 1 * 1000, sp + 2 * 1000),
        id_links(sp + 2 * 1000, sp + 3 * 1000),
        id_links(sp + 3 * 1000, sp + 4 * 1000),
        id_links(sp + 4 * 1000, sp + 5 * 1000),
        id_links(sp + 5 * 1000, sp + 6 * 1000),
        id_links(sp + 6 * 1000, sp + 7 * 1000),
        id_links(sp + 7 * 1000, sp + 8 * 1000),
        id_links(sp + 8 * 1000, sp + 9 * 1000),
        id_links(sp + 9 * 1000, sp + 10 * 1000),
        id_links(sp + 10 * 1000, sp + 11 * 1000),
        id_links(sp + 11 * 1000, sp + 12 * 1000),
        id_links(sp + 12 * 1000, sp + 13 * 1000),
        id_links(sp + 13 * 1000, sp + 14 * 1000),
        id_links(sp + 14 * 1000, sp + 15 * 1000),
        id_links(sp + 15 * 1000, sp + 16 * 1000),
        id_links(sp + 16 * 1000, sp + 17 * 1000),
        id_links(sp + 17 * 1000, sp + 18 * 1000),
        id_links(sp + 18 * 1000, sp + 19 * 1000),
        id_links(sp + 19 * 1000, sp + 20 * 1000),
        # id_links(sp + 20 * 1000, sp + 21 * 1000),
        # id_links(sp + 21 * 1000, sp + 22 * 1000),
        # id_links(sp + 22 * 1000, sp + 23 * 1000),
        # id_links(sp + 23 * 1000, sp + 24 * 1000),
        # id_links(sp + 24 * 1000, sp + 25 * 1000),
        # id_links(sp + 25 * 1000, sp + 26 * 1000),
        # id_links(sp + 26 * 1000, sp + 27 * 1000),
        # id_links(sp + 27 * 1000, sp + 28 * 1000),
        # id_links(sp + 28 * 1000, sp + 29 * 1000),
        # id_links(sp + 29 * 1000, sp + 30 * 1000),
        # id_links(sp + 30 * 1000, sp + 31 * 1000),
        # id_links(sp + 31 * 1000, sp + 32 * 1000),
        # id_links(sp + 32 * 1000, sp + 33 * 1000),
        # id_links(sp + 33 * 1000, sp + 34 * 1000),
        # id_links(sp + 34 * 1000, sp + 35 * 1000),
        # id_links(sp + 35 * 1000, sp + 36 * 1000),
        # id_links(sp + 36 * 1000, sp + 37 * 1000),
        # id_links(sp + 37 * 1000, sp + 38 * 1000),
        # id_links(sp + 38 * 1000, sp + 39 * 1000),
        # id_links(sp + 39 * 1000, sp + 40 * 1000),
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
