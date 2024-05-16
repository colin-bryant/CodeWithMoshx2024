import time
import requests
import re
import os
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

#获取处于调试模式的Chrome浏览器对象
if __name__ == '__main__':
    option1 = Options()
    option1.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    webobj = webdriver.Chrome(options=option1)

#获取用户名
savepath = '/Users/gustavofring/Downloads/小红书'
headers={
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
}
username = webobj.find_element(By.CLASS_NAME, 'user-name').text

#设定本地存储地址
if not os.path.exists(savepath):
    os.mkdir(savepath)
savepath = savepath + '/' + username
if not os.path.exists(savepath):
    os.mkdir(savepath)

#获取首次刷新数据
#注意，代码中的“data-v-d0dd9c82”部分需要根据实际数据进行替换
initdata = webobj.find_elements(by=By.XPATH, value='//div[@data-v-d0dd9c82]/a[@style="display: none;"]')
initdata = [initdata.get_property('href') for initdata in initdata]

#滚动页面加载更多笔记
last_height = webobj.execute_script("return document.body.scrollHeight")
while True:
    webobj.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    time.sleep(4)
    newdata = webobj.find_elements(by=By.XPATH, value='//div[@data-v-d0dd9c82]/a[@style="display: none;"]')
    newdata = [newdata.get_property('href') for newdata in newdata]
    new_height = webobj.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    initdata.extend(newdata)
    last_height = new_height

#剔除笔记网址中的重复项
data = []
for initdata in initdata:
    if data.count(initdata) < 1:
        data.append(initdata)

for num in range(0,len(data)):
    print(str(num+1) + ' ' + data[num])

#新建无头浏览器对象下载图片和视频
webobj.quit()
option2 = Options()
option2.add_argument('--headless')
option2.add_argument('--disable-gpu')
webobj = webdriver.Chrome(options=option2)

#按笔记顺序下载：图片笔记和视频笔记分别处理
for page in range(0,len(data)):
    webobj.get(data[page])
    response = requests.get(url=data[page],headers=headers).text
    parser = etree.HTML(response)
    title = parser.xpath('//div[@id="detail-title"]/text()')
    #笔记无标题的情况
    if len(title) == 0:
        title = '无标题'
    else:
        title = title[0]
    title = title.replace('/','.') #笔记标题中有斜杠的情况
    pic = webobj.find_elements(by=By.XPATH, value='//div[@class="swiper-wrapper"]/div')
    if len(pic) != 0:
        for num in range(1,len(pic)-1):
            link = re.search('url\("(.*)"\)', pic[num].get_attribute('style'))
            img = requests.get(url=link.group(1),headers=headers).content
            with open(savepath + '/' + str(page + 1) + '_' + title + '_' + str(num) + '.webp', 'wb') as t:
                t.write(img)
    else:
        link = webobj.find_element(by=By.TAG_NAME, value='video').get_property('src')
        vid = requests.get(url=link, headers=headers).content
        with open(savepath + '/' + str(page + 1) + '_' + title + '.mp4', 'wb') as t:
            t.write(vid)