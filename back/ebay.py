import json
import time

import requests
import urllib3
from bs4 import BeautifulSoup
import pymysql

host = 'localhost'
port = 3306
db = 'spider'
user = 'root'
password = 'root'
conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
batch = time.time()


def write_table_info_1(table_info_list):
    if None == table_info_list:
        return
    if len(table_info_list) == 0:
        return
    print("写入数据库")
    cursor = conn.cursor()
    tuple_list = []
    for i in table_info_list:
        tuple_list.append(tuple(i.values()))
    sql = "INSERT INTO spider.ebay_table_info_type_1 (sku_id,batch,sku_name, release_year, make, model, sub_model, fitment_comments, is_delete, created_by, created_time, updated_by, updated_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)"
    print("数据库落表" + str(cursor.executemany(sql, tuple_list)) + "条")
    conn.commit()
    cursor.close()


def write_table_info_2(table_info_list):
    if None == table_info_list:
        return
    if len(table_info_list) == 0:
        return
    print("写入数据库")
    cursor = conn.cursor()
    tuple_list = []
    for i in table_info_list:
        tuple_list.append(tuple(i.values()))
    sql = "INSERT INTO spider.ebay_table_info_type_2 (sku_id,batch,sku_name, release_year, make, model,sku_trim, engine, is_delete, created_by, created_time, updated_by, updated_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)"
    print("数据库落表" + str(cursor.executemany(sql, tuple_list)) + "条")
    conn.commit()
    cursor.close()


def write_product_info_list(product_info_list):
    print("写入数据库")
    cursor = conn.cursor()
    tuple_list = []
    for i in product_info_list:
        tuple_list.append(tuple(i.values()))
    sql = 'INSERT INTO spider.ebay_product_info (batch, sku_id, sku_name, price, properties, is_delete, created_by, created_time, updated_by, updated_time) VALUES (%s, %s, %s, %s, %s, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)'
    print("数据库落表" + str(cursor.executemany(sql, tuple_list)) + "条")
    conn.commit()
    cursor.close()


def request_category(url):
    category_url_list = []
    for category_tag in get_soup(url).find_all(class_='dialog__cell')[0].find_all("a"):
        if category_tag.has_attr("href"):
            category_url_list.append(category_tag["href"])
    return category_url_list


def get_product_url_list(url):
    product_list = []
    product_grids = get_soup(url).find("ul", class_="srp-grid")
    if None == product_grids:
        print(url + "不存在商品")
        return None;
    for product_tag in product_grids.find_all("a", class_="s-item__link"):
        if product_tag.has_attr("href"):
            product_list.append(product_tag["href"])
    return product_list


def get_soup(url, retry=1):
    while retry > 0:
        try:
            current = time.time()
            print("requesting " + url)
            response = requests.request("GET", url, headers={
                "authority": "cn.ebay.com",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "zh-CN,zh;q=0.9"
            }, timeout=15)
            print("request down,cost " + str(time.time() - current))
            return BeautifulSoup(response.text, features="html")
        except urllib3.exceptions.MaxRetryError:
            print(url + "请求失败,retry " + str(retry))
            retry = retry - 1
            sleep()
        except urllib3.exceptions.ReadTimeoutError:
            print(url + "读取失败,retry " + str(retry))
            retry = retry - 1
            sleep()
        except requests.exceptions.ReadTimeout:
            print(url + "读取失败,retry " + str(retry))
            retry = retry - 1
            sleep()
        except requests.exceptions.Timeout:
            print(url + "请求超时,retry " + str(retry))
            retry = retry - 1
            sleep()
        except requests.exceptions.ConnectionError:
            print(url + "连接失败,retry " + str(retry))
            retry = retry - 1
            sleep()
    return None


def get_product_detail_info(url):
    print("开始解析商品数据")
    try:
        soup = get_soup(url, 2)
        if None == soup:
            return None
        sku_id = url.split("https://www.ebay.com/itm/")[1].split("?")[0]
        sku_name = soup.find("h1", id="itemTitle").contents[1]
        crawl_product_table_info_1(url, sku_id, sku_name, soup)
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
        print(url + "解析失败")
        return None


def crawl_product_table_info_1(url, sku_id, sku_name, soup):
    script_list = ""
    for script_contents in soup.findAll("script"):
        for script_content in script_contents:
            script_list = script_content + script_list
    try:
        product_info_list_1 = []
        product_info_list_2 = []
        header = json.loads(script_list.split(",\"fitHeaders\":")[1].split("\"},\"")[0] + "\"}")
        header["Authorization"] = script_list.split("'urwwidget', {\"value\":\"")[1].split("\",")[0]
        jsonInfo = json.loads(requests.get(
            "https://api.ebay.com/parts_compatibility/v1/compatible_products/listing/" + sku_id + "?fieldgroups=full"
                                                                                                  "&limit=10000",
            headers=header).text)
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
        write_table_info_1(product_info_list_1)
        write_table_info_2(product_info_list_2)
    except IndexError:
        print(url + "不存在表格")
    except KeyError:
        print(url + "字段不匹配")
    except AttributeError:
        print(url + "解析失败")


def process_product_list(category_url):
    url_list = get_product_url_list(category_url)
    if None == url_list:
        return False
    product_detail_info_list = []
    for product_url in url_list:
        print("=================================================")
        data = get_product_detail_info(product_url)
        if None == data:
            continue
        product_detail_info_list.append(data)
        print("=================================================")
    write_product_info_list(product_detail_info_list)
    return True


def sleep(sleep_time=3):
    print("开始睡眠" + str(time.time()))
    time.sleep(sleep_time)
    print("睡眠结束，开启下次请求。。。" + str(time.time()))
    print("=================================================")


def execute(category_url_list):
    print("spider start,batch " + str(batch) + "...")
    current_time = time.time()
    for category_url in category_url_list:
        page = 1
        while process_product_list(
                category_url + '?rt=nc&_pgn=' + str(page)):
            page = page + 1
        conn.close()
    print("spider off ,cost" + str(time.time() - current_time))


if __name__ == '__main__':
    category_url_List = [
        # 'https://cn.ebay.com/b/In-Car-Technology-GPS-Security-Devices/38635/bn_562662',
        # 'https://cn.ebay.com/b/ATV-Side-by-Side-UTV-Parts-Accessories/43962/bn_562707',
        'https://cn.ebay.com/b/Car-Truck-Accessory-Belts-Parts/262059/bn_583759',
        'https://cn.ebay.com/b/Car-Truck-Advanced-Driver-Assistance-Systems/262064/bn_7117881172',
        'https://cn.ebay.com/b/Car-Truck-Air-Fuel-Delivery/33549/bn_584325',
        'https://cn.ebay.com/b/Car-Truck-Air-Conditioning-Heating/33542/bn_584326',
        'https://cn.ebay.com/b/Car-Truck-Brakes-Brake-Parts/33559/bn_557694',
        'https://www.ebay.com/sch/Electric-Vehicle-Parts/177701/bn_576987/i.html',
        'https://cn.ebay.com/b/Car-Truck-Engine-Cooling-Components/33599/bn_561581',
        'https://cn.ebay.com/b/Car-Truck-Engines-Components/33612/bn_560118',
        'https://cn.ebay.com/b/Car-Truck-Exhaust-Emission-Systems/33605/bn_583501',
        'https://cn.ebay.com/b/Car-Truck-Exterior-Parts/33637/bn_584029',
        'https://cn.ebay.com/b/Car-Truck-Ignition-Systems/33687/bn_577605',
        'https://cn.ebay.com/b/Car-Truck-Interior-Parts/33694/bn_584056',
        'https://cn.ebay.com/b/Car-Truck-Lighting-Lamps/33707/bn_557923',
        'https://cn.ebay.com/b/Car-Truck-Racks-Cargo-Carriers/262215/bn_7117880183',
        'https://cn.ebay.com/b/Car-Truck-Starters-Alternators-ECUs-Wiring/33572/bn_583502',
        'https://cn.ebay.com/b/Car-Truck-Suspension-Steering-Parts/33579/bn_577405',
        'https://cn.ebay.com/b/Car-Truck-Towing-Parts-Accessories/180143/bn_7117890161',
        'https://cn.ebay.com/b/Car-Truck-Transmission-Drivetrain-Parts/33726/bn_557929',
        'https://cn.ebay.com/b/Car-Truck-Wheels-Tires-Parts/33743/bn_584076',
        'https://cn.ebay.com/b/Other-Car-Truck-Parts-Accessories/9886/bn_7117878185'
    ]
    get_product_detail_info("https://www.ebay.com/itm/114048694738?epid=249409809&hash=item1a8dd4f9d2:g:g5EAAOSwW4JeEFAH")
    # execute(category_url_List)
    # 1636193164.9191375
    # 1636201809.566613
