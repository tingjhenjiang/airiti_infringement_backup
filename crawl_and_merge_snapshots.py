#!/usr/bin/env python
# coding: utf-8

# In[1]:


import selenium
import diff2HtmlCompare
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from time import sleep
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time, os
browser = "Firefox"
docid = "a0000446-199106-20-2-63-85-a"
#使用Edge時driver檔名請儲存為'MicrosoftWebDriver.exe'
#使用Firefox時driver檔名請儲存為'geckodriver.exe'
#使用Chrome時driver檔名請儲存為'chromedriver.exe'
def save_screenshot(driver, path) -> None:
    # Ref: https://stackoverflow.com/a/52572919/
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    driver.find_element_by_tag_name('body').screenshot(path)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])


# In[2]:


options = {"Firefox": FirefoxOptions(), "Edge": EdgeOptions(), "Chrome": ChromeOptions()}[browser]
options.add_argument("--headless")
options.add_argument('--start-maximized')
if browser=="Chrome":
    options.binary_location = "D:\\PortableApps\\PortableApps\\GoogleChromePortable\\App\\Chrome-bin\\chrome.exe" #可指定Chrome binary path 例如："C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
browser_argument = {
    "Firefox": {
        "firefox_binary": "D:\\PortableApps\\PortableApps\\FirefoxPortable\\App\\Firefox64\\firefox.exe" #可指定Firefox binary path 如
    },
    "Edge": {},
    "Chrome": {}
}[browser]
needdriver = {"Firefox": FirefoxDriver, "Edge": EdgeDriver, "Chrome": ChromeDriver}[browser]


# In[3]:


execdriver = needdriver(options=options, **browser_argument)


# In[4]:


htmls = []
html_file_names = []
urls = []
screenshot_file_names = []
for i, url in enumerate(["https://www.airitilibrary.com/Publication/alDetailedMesh?DocID={}","http://www.airitilibrary.cn/Publication/alDetailedMesh?DocID={}"]):
    targetUrl = url.format(docid)
    urls.append(targetUrl)
    execdriver.get(targetUrl)
    el = execdriver.find_element_by_tag_name('body')
    screenshot_file_name = "{}.png".format(i)
    screenshot_file_names.append(screenshot_file_name)
    #el.screenshot()
    save_screenshot(execdriver, screenshot_file_name)
    htmls.append(execdriver.execute_script("return document.getElementsByTagName('html')[0].innerHTML"))
    html_file_name = "{}.html".format(i)
    html_file_names.append(html_file_name)
    f = open(html_file_name, "w+", encoding="utf-8")
    f.write(htmls[i])
    f.close()
    if i==0:
        article_inf = execdriver.find_element_by_xpath("//div[@class='detail']").text
        article_inf = article_inf.replace("\n",",")
        article_inf = article_inf.replace(" ","")
        article_inf = article_inf.replace("/","-")


# In[5]:


diff2HtmlCompare.main(html_file_names[0], html_file_names[1], "diff.html", {"verbose":False, "syntax_css": "vs", "print_width": False})
execdriver.get(os.path.join(os.getcwd(),"diff.html") )
diff_png_file_name = "{}.png".format("diff")
el = execdriver.find_element_by_tag_name('body')
#el.screenshot("{}.png".format("diff"))
save_screenshot(execdriver, diff_png_file_name)
screenshot_file_names.append(diff_png_file_name)
execdriver.close()


# In[6]:


from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
images_list = screenshot_file_names
imgs = [Image.open(i) for i in images_list]


# In[7]:


# merge horizontally
width_sorted = sorted([i.width for i in imgs])
height_sorted = sorted([i.height for i in imgs])
total_width = width_sorted[-1]+width_sorted[-2]
max_height_sorted = height_sorted[-1]
second_max_height = max(height_sorted[:-1])
total_height = second_max_height+max_height_sorted


# In[8]:


img_merge = Image.new(imgs[0].mode, (total_width, total_height))
font = ImageFont.truetype("./NotoSansTC-Medium.otf", 12)
x = 0
y = 0
for i, img in enumerate(imgs):
    if i<2:
        img_merge.paste(img, (x, 0))
        draw = ImageDraw.Draw(img_merge)
        draw.text((x+10, 0), urls[i], (196, 8, 42), font=font)
        x += img.width
        y = img.height
    else:
        #計算置中的x位置
        this_width = img.width
        to_paste_x = int((x-this_width)/2)
        img_merge.paste(img, (to_paste_x, second_max_height))
        y += img.height
img_merge.save(os.path.join("fetch_results", '{}.png'.format(article_inf)))


# In[9]:


[i.close() for i in imgs]

