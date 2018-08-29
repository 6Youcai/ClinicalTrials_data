import requests
from bs4 import BeautifulSoup
import json
import time
import copy
import re

def get_web(CTR, ckm_id):
    chrome = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7",
               "Cache-Control": "max-age=0",
               "Connection": "keep-alive",
               "Content-Length": "237",
               "Content-Type": "application/x-www-form-urlencoded",
               "Cookie": "UM_distinctid=1655537e61273b-0642033f77f632-34657908-13c680-1655537e613f31; JSESSIONID=0000HTmmWCawo4Kl5eDraZrDc9e:-1; CNZZDATA1256895572=1236113898-1534731672-null%7C1535448681",
               "DNT": "1",
               "Host": "www.chinadrugtrials.org.cn",
               "Origin": "http://www.chinadrugtrials.org.cn",
               "Referer": "http://www.chinadrugtrials.org.cn/eap/clinicaltrials.searchlist?a=a&keywords=%s" %CTR,
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
    info = {"ckm_id": ckm_id,
            "ckm_index": 1,
            "sort": "desc",
            "sort2": "desc",
            "rule": "CTR",
            "currentpage": 1,
            "pagesize": 20,
            "keywords": CTR,
            "reg_no": "CTR"}
    Request_URL =  "http://www.chinadrugtrials.org.cn/eap/clinicaltrials.searchlistdetail"
    web = requests.post(Request_URL, data = info, headers = chrome)
    return web

def get_text(tag):
    return tag.text.strip()

def trim_blank(text):
    return re.sub("\s", "", text)

def dict_table(table, start = 0, space = 2):
    data = table.find_all('td')
    cells = list(map(get_text, data))
    return dict(zip(cells[start::space], cells[start+1::space]))

def list_table(table):
    values = []
    lines = table.find_all('tr')
    headers = list(map(get_text, lines[0].find_all('td')))
    for l in lines[1:]:
        tmp = list(map(get_text, l.find_all('td')))
        values.append(dict(zip(headers, tmp)))
    return values

def analysis(html, CTR):
    soup = BeautifulSoup(html, features="lxml")
    result = {}

    # cxtj_tm
    cxtj_tm = soup.find('div', class_ = 'cxtj_tm')
    result["basic_info"] = dict_table(cxtj_tm)

    # 公示的试验信息
    pub_info = soup.find('div', id = 'div_open_close_01')
    part_names = list(map(get_text, pub_info.find_all('div', recursive = False)))
    part_tables = pub_info.find_all('table', recursive = False)
    # 一、题目和背景信息
    result[part_names[0]] = dict_table(part_tables[0])
    # 二、申办者信息
    result[part_names[1]] = dict_table(part_tables[1])
    #  三、临床试验信息
    clinicaltrials = part_tables[2]
    lines = clinicaltrials.find_all('tr', recursive = False)
    info = {}
        # 1、试验目的
    info[get_text(lines[0])] = get_text(lines[1])
        # 2、试验设计
    info[get_text(lines[2])] = dict_table(lines[3].table, 1, 3)
        # 3、受试者信息
    patient_line = copy.copy(lines[5])
    for i in [6, 7, 10, 11]:
        patient_line.append(lines[i])
    patient = dict_table(patient_line)
            # 入选标准
    standard_in = lines[8].find_all('td', recursive = False)
    patient[get_text(standard_in[0])] = list(map(get_text, standard_in[1].find_all('td')))[1::2]
            # 排除标准
    standard_out = lines[9].find_all('td', recursive = False)
    patient[get_text(standard_out[0])] = list(map(get_text, standard_out[1].find_all('td')))[1::2]
    info[get_text(lines[4])] = patient
        # 4、试验分组
    group = {}
    drug_test = lines[13].find_all('td', recursive = False) # 试验药
    group[get_text(drug_test[0])] = list_table(drug_test[1])
    drug_control = lines[14].find_all('td', recursive = False) # 对照药
    group[get_text(drug_control[0])] = list_table(drug_control[1])
    info[get_text(lines[12])] = group
        # 5、终点指标
    end = {}
    main = lines[16].find_all('td', recursive = False) # 主要终点指标及评价时间
    end[get_text(main[0])] = list_table(main[1])
    minor = lines[17].find_all('td', recursive = False) # 次要终点指标及评价时间
    end[get_text(minor[0])] = list_table(minor[1])
    info[get_text(lines[15])] = end
        # 6、数据安全监察委员会（DMC）
    DMC = get_text(lines[18]).split("：")
    info[DMC[0]] = DMC[1].strip()
        # 7、为受试者购买试验伤害保险
    Insurance = get_text(lines[19]).split("：")
    info[Insurance[0]] = Insurance[1].strip()
    result[part_names[2]] = info
    # 四、第一例受试者入组日期
    result[part_names[3]] = get_text(part_tables[3])
    # 五、试验终止日期
    result[part_names[4]] = get_text(part_tables[4])
    # 六、研究者信息
    researcher = {}
    lines_researcher = part_tables[5].find_all('tr', recursive = False)
    researcher[get_text(lines_researcher[0])] = dict_table(lines_researcher[1].table) # 1、主要研究者信息
    researcher[get_text(lines_researcher[2])] = list_table(lines_researcher[3].table) # 2、各参加机构信息
    result[part_names[5]] = researcher
    # 七、伦理委员会信息
    result[part_names[6]] = list_table(part_tables[6])
    # 八、试验状态
    result[part_names[7]] = trim_blank(get_text(part_tables[7]))

    j = json.dumps(result, ensure_ascii = False)
    f = open("%s.json" %CTR, "w")
    f.write(j)
    f.close()

if __name__ == "__main__":
    f = open("chinadrugtrials.txt", 'r')
    f2 = open("failed.txt", 'w')
    for line in f:
        arr = line[:-1].split()
        CTR = arr[1]
        ckm_id = arr[-1]
        status = arr[2]
        if status in ["已完成", "进行中 招募完", "主动暂停"]:
            continue
        print("treating %s" %CTR)
        web = get_web(CTR, ckm_id)
        if web.ok:
            try:
                analysis(web.text, CTR)
                print("%s is OK" %CTR)
                time.sleep(3)
            except:
                print("analysis %s failed" %CTR)
                f2.write(CTR + "\t" + ckm_id + '\n')
        else:
            print("get %s failed" %CTR)
            f2.write(CTR + "\t" + ckm_id + '\n')
    f.close()
    f2.close()
