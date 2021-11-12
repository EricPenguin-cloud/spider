import pymysql
from logger import log
from utils import conf


class Writer:

    def __init__(self):
        mysql_config = conf('mysql')
        self.conn = pymysql.connect(
            host=mysql_config['host'],
            port=mysql_config['port'],
            db=mysql_config['db'],
            user=mysql_config['user'],
            password=mysql_config['password']
        )

    def write_product_info_list(self, product_info_list):
        log.info("写入数据库")
        cursor = self.conn.cursor()
        tuple_list = []
        for i in product_info_list:
            tuple_list.append(tuple(i.values()))
        sql = 'INSERT INTO spider.ebay_product_info (batch, sku_id, sku_name, price, properties, is_delete, created_by, created_time, updated_by, updated_time)' \
              ' VALUES (%s, %s, %s, %s, %s, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)'
        log.info("数据库落表" + str(cursor.executemany(sql, tuple_list)) + "条")
        self.conn.commit()
        cursor.close()

    def write_table_info(self, table_info_list):
        if table_info_list is None:
            return
        if len(table_info_list) == 0:
            return
        log.info("表1写入数据库")
        cursor = self.conn.cursor()
        tuple_list = []
        for i in table_info_list:
            tuple_list.append(tuple(i.values()))
        sql = "INSERT INTO spider.ebay_table_info (" \
              "batch, sku_id, sku_name, json_text, is_delete, created_by, created_time, updated_by,updated_time)VALUES " \
              "(%s, %s, %s, %s, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT);"
        log.info("数据库落表" + str(cursor.executemany(sql, tuple_list)) + "条")
        self.conn.commit()
        cursor.close()

    def close(self):
        self.conn.close()
