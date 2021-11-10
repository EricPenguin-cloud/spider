import json
import time

from dispatcher import Dispatcher
from writer import Writer
from utils import conf
from logger import log

batch = ''
writer = Writer()
dispatcher = Dispatcher()

html_header = {
    "authority": "cn.ebay.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "zh-CN,zh;q=0.9"
}


def request_category(url):
    category_url_list = []
    for category_tag in dispatcher.html(url, head=html_header).find_all(class_='dialog__cell')[0].find_all("a"):
        if category_tag.has_attr("href"):
            category_url_list.append(category_tag["href"])
    return category_url_list


def get_product_url_list(url):
    product_list = []
    product_grids = dispatcher.html(url, head=html_header).find("ul", class_="srp-grid")
    if product_grids is None:
        log.error(url + "不存在商品")
        return None
    for product_tag in product_grids.find_all("a", class_="s-item__link"):
        if product_tag.has_attr("href"):
            product_list.append(product_tag["href"])
    return product_list


def process_product_detail_info(url):
    log.info("开始解析商品数据")
    try:
        soup = dispatcher.html(url, head=html_header, retry=2)
        if soup is None:
            return None
        sku_id = url.split("https://www.ebay.com/itm/")[1].split("?")[0]
        sku_name = soup.find("h1", id="itemTitle").contents[1]
        processs_product_table_info_1(url, sku_id, sku_name, soup)
        price = soup.find("span", itemprop="price").text
        properties = "{"
        rows = soup.find("div", class_="ux-layout-section").find_all("div", class_="ux-layout-section__row")
        for row in rows:
            layout_list = row.find_all("div", class_="ux-labels-values__labels")
            value_list = row.find_all("div", class_="ux-labels-values__values")
            for index in range(len(layout_list)):
                properties = properties + "\"" + layout_list[index].text.split("：")[0] + "\":\"" + value_list[
                    index].text + "\","
        return {"batch": batch, "sku_id": sku_id, "sku_name": sku_name, "price": price,
                "properties": "{}" if properties == "{" else properties[0:-1] + "}"}
    except AttributeError:
        log.error(url + "解析失败")
        return {}


def processs_product_table_info_1(url, sku_id, sku_name, soup):
    script_list = ""
    for script_contents in soup.findAll("script"):
        for script_content in script_contents:
            script_list = script_content + script_list
    try:
        product_info_list_1 = []
        product_info_list_2 = []
        header = json.loads(script_list.split(",\"fitHeaders\":")[1].split("\"},\"")[0] + "\"}")
        header["Authorization"] = script_list.split("'urwwidget', {\"value\":\"")[1].split("\",")[0]
        jsonInfo = dispatcher.json("GET",
                                   "https://api.ebay.com/parts_compatibility/v1/compatible_products/listing/" + sku_id + "?fieldgroups=full"
                                                                                                                         "&limit=10000",
                                   head=header)
        table_info_list = []
        if 'compatibleProductMetadata' in jsonInfo.keys():
            table_info_list = jsonInfo['compatibleProductMetadata']['compatibilityProperties']
        elif 'compatibleProducts' in jsonInfo.keys():
            table_info_list = jsonInfo["compatibleProducts"]["members"]
        for table_info in table_info_list:
            if 'Engine' in table_info['productProperties'].keys():
                product_info_list_2.append({"sku_id": sku_id, "batch": batch, "sku_name": sku_name,
                                            "release_year": table_info['productProperties']["Year"],
                                            "make": table_info['productProperties']["Make"],
                                            "model": table_info['productProperties']["Model"],
                                            "sku_trim": table_info['productProperties']["Trim"],
                                            "engine": table_info['productProperties']["Engine"]})
            else:
                product_info_list_1.append({"sku_id": sku_id, "batch": batch, "sku_name": sku_name,
                                            "release_year": table_info['productProperties']["Year"],
                                            "make": table_info['productProperties']["Make"],
                                            "model": table_info['productProperties']["Model"],
                                            "sub_model": table_info['productProperties']["Submodel"],
                                            "fitment_comments": table_info['productProperties']["FitmentComments"]})
        writer.write_table_info_1(product_info_list_1)
        writer.write_table_info_2(product_info_list_2)
    except IndexError:
        log.error(url + "不存在表格")
    except KeyError:
        log.error(url + "字段不匹配")
    except AttributeError:
        log.error(url + "解析失败")


def process_product_list(category_url):
    url_list = get_product_url_list(category_url)
    if url_list is None:
        return False
    product_detail_info_list = []
    for product_url in url_list:
        data = process_product_detail_info(product_url)
        if data is None:
            continue
        product_detail_info_list.append(data)
    writer.write_product_info_list(product_detail_info_list)
    return True


def execute(category_url_list):
    log.info("spider start,batch " + str(batch) + "...")
    current_time = time.time()
    for category_url in category_url_list:
        page = 1
        while process_product_list(
                category_url + '?rt=nc&_pgn=' + str(page)):
            page = page + 1
        writer.close()
    log.info("spider off ,cost" + str(time.time() - current_time))


def execute_category_pages(category_url_list):
    if category_url_list is None:
        log.error("parameter category-pages is None !")
        return
    log.info("spider start,batch " + str(batch) + "...")
    time.perf_counter()
    for category_url in category_url_list:
        page = 1
        while process_product_list(
                category_url + '?rt=nc&_pgn=' + str(page)):
            page = page + 1
        writer.close()
    log.info("spider off ,cost" + str(time.perf_counter()))


entry = {
    "category-pages": execute_category_pages
}

if __name__ == '__main__':
    batch = str(time.strftime("%Y-%m-%d %H:%M:%S"))
    entry[conf('spider', 'entry')](conf('spider', conf('spider', 'entry')))

    # execute(category_url_List)
    # 1636193164.9191375
    # 1636201809.566613
