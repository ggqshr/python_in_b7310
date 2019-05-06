from scrapy import cmdline
from time import sleep, strftime, localtime, time
import schedule
import atexit


@atexit.register
def close_file():
    print("trying to close file..")
    if not f.closed:
        f.close()


f = open("log.log", encoding="utf-8", mode="a")


def job():
    f.writelines(f"scrapy start to crawl at {strftime('%Y.%m.%d %H:%M:%S', localtime(time()))}\n")
    f.flush()
    cmdline.execute(['scrapy', 'crawl', 'bdbp'])


schedule.every().day.at("12:00").do(job)

while True:
    schedule.run_pending()
    sleep(60)
