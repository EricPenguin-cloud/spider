# 提取文件夹下的地址+文件名，源文件设定排序规则
import os
import xml.etree.ElementTree as ET


def file_names(file_dir, suffix):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.' + suffix:
                L.append(os.path.join(root, file))
    return sorted(L)


ifnull = "ifnull("


def deal_ifnull(file_name):
    with open(file_name, 'r+') as file:
        lines = file.readlines()
        override = False
        for index in range(len(lines)):
            lines[index], replaced = replace_contract(lines[index])
            if replaced:
                override = True
        if override:
            file.seek(0, 0)
            file.writelines(lines)
            file.truncate()


def deal_duplicate(file_name):
    with open(file_name, 'r+') as file:
        lines = file.readlines()
        override = False
        dealing = False
        for index in range(len(lines)):
            line = lines[index]
            if "<insert " in line or "<select" in line or \
                    "<delete" in line or "<update" in line or \
                    "<resultMap" in line or "<sql" in line or "<mapper" in line:
                dealing = False
            if "on duplicate key update" in line or "ON DUPLICATE KEY UPDATE" in line:
                dealing = True
            if dealing:
                lines[index], replaced = replace_duplicate(lines[index])
                if replaced:
                    override = True
        if override:
            file.seek(0, 0)
            file.writelines(lines)
            file.truncate()


def replace_contract(line):
    if ifnull in line and "#" in line:
        return replace_ifnull(line), True
    return line, False


def replace_duplicate(line):
    override = False
    while "#{" in line:
        override = True
        source = line[line.find("#{"):line.find("}") + 1]
        line = line.replace(source, convert_duplicate(source), 1)
    return line, override


def replace_ifnull(line):
    while ifnull in line:
        start = line.find(ifnull)
        if -1 == line.find("now())"):
            source = line[start:line.find(")", start) + 1]
        else:
            source = line[start:line.find("now())", start) + 6]
        line = line.replace(source, convert_ifnull(source), 1)
    return line


def convert_ifnull(line):
    print("old: " + line)
    field = line[7:line.index("}") + 1]
    field_name = field[2:-1]
    if "," in field:
        field_name = field[2: field.index(",")]
    field_value = line[line.find(",", line.find("}")) + 1:-1]
    result = " <choose> " \
             + '<when test="' + field_name + '!=null"> ' + field + " </when> " \
             + " <otherwise> " + field_value + " </otherwise> " \
             + " </choose> "
    print("new: " + result)
    return result


def convert_duplicate(source):
    print("old: " + source)
    start = source.find("#{") + 2
    end = source.find(",")
    if end <= 0:
        end = source.find("}")
    value = "values(" + source[start:end] + ")"
    print("new: " + value)
    return value


if __name__ == "__main__":
    dir = "/mnt/c/Users/Eric/IdeaProjects/yh-rme-srm-order-plan/yh-rme-srm-order-plan-dao/src/main/resources/mapper"
    files = file_names(dir, "xml")
    for file in files:
        # 替换 ifnull
        deal_ifnull(file)
        # 替换 不合法的 on duplicate key update
        deal_duplicate(file)