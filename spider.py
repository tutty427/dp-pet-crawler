import xlwt
'''  
爬取网页时直接出现403，意思是没有访问权限  
'''
import requests
from bs4 import BeautifulSoup
import random
# 入口网页
start_url = 'http://www.dianping.com/shanghai/ch95'


def get_content(url, headers=None):
    response = requests.get(url, headers=headers)  # 发起了一次请求
    html = response.content
    return html


'''  
    获取所有行政区的url  
'''


def region_url(html):
    soup = BeautifulSoup(html, 'lxml')  # lxml解析器
    # <div id="region-nav" class="nc-items ">
    #   <a href="/search/category/344/10/r299"><span>芙蓉区</span></a>
    # 列表推导式
    region_url_list = [i['href'] for i in soup.find('div', id="region-nav").find_all('a')]
    print(region_url_list)
    return region_url_list


# 获取商户的详情页的url地址
# find:取第一个(返回一个具体的元素，没有为null)       find_all:匹配所有(返回列表，没有返回[])
def get_shop_url(html):
    soup = BeautifulSoup(html, 'lxml')  # lxml解析器
    shop_url_list = [i.find('a')['href'] for i in soup.find_all('div', class_='tit')]
    return shop_url_list


# 获取所得信息(店名，价格，评分)。。。解析页面
def get_detail(html):
    soup = BeautifulSoup(html, 'lxml')  # lxml解析器
    # <h1 class="shop-name">1911牛肉烤串</h1>
    title = soup.find('div', class_='breadcrumb').find('span').text
    # <span id="avgPriceTitle" class="item">人均：-</span>
    price = soup.find('span', id="avgPriceTitle").text
    # <span id="comment_score"><span class="item">口味：7.6</span><span class="item">环境：7.4</span><span class="item">服务：7.5</span></span>
    evaluation = soup.find('span', id="comment_score").find_all('span', class_="item")  # 评分的list
    # <span id="reviewCount" class="item">3条评论</span>
    comments = soup.find('span', id="reviewCount").text  # 评论的数量
    #     <div class="expand-info address" itemprop="street-address">
    #         <span class="item" itemprop="street-address" title="麓松路南丰港安置小区12栋">
    #                      麓松路南丰港安置小区12栋
    #         </span>
    #     </div>
    address = soup.find('span', class_="item", itemprop="street-address").text.strip()

    #     print u'店名'+title
    #     for ev in evaluation:
    #         print ev.text
    #     print u'价格'+price
    #     print u'评论数量'+comments
    #     print u'地址'+address
    return (title, evaluation[0].text, evaluation[1].text, evaluation[2].text, price, comments, address)



# 文件作为脚本直接执行，而import到其他脚本中是不会被执行的。
if __name__ == '__main__':
    items = []
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    ]

    ua = random.choice(user_agent_list);
    headers = {
        'User-Agent':ua,
    }
    html = get_content(start_url,headers)
    region_url_list = region_url(html)
    # 遍历所有行政区的所有商户
    for url in region_url_list:  # 遍历所有的行政区
        # 简单的出错处理，有错则略过
        try:
            for n in range(1, 51):  # 遍历所有的50页
                ua = random.choice(user_agent_list);
                html = get_content(url + 'p' + str(n),headers)
                # 所有商户的详情页
                shop_url_list = get_shop_url(html)
                for shop_url in shop_url_list:
                    #                 print shop_url
                    # 提取数据，获取
                    detail_html = get_content(shop_url, headers)
                    '''  
                    #403 Forbidden（没有访问权限）:  
                                            （1）直接出现：  
                                            （2）爬取一会儿出现403：可以通过代理ip解决  
                    referer   防盗链  
                    Host域名  
                    Cookie  
                    '''
                    items.append(get_detail(detail_html))
        except :
            continue
    new_table = r'D:\dzdp.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('test1')
    headData = ['商户名字', '口味评分', '环境评分', '服务评分', '人均价格', '评论数量', '地址']
    for colnum in range(0, 7):
        ws.write(0, colnum, headData[colnum], xlwt.easyxf('font:bold on'))
    index = 1
    lens = len(items)
    for j in range(0, lens):
        for i in range(0, 7):
            ws.write(index, i, items[j][i])
        index = index + 1

    wb.save(new_table)