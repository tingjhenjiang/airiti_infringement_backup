# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import argparse
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
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#使用Edge時driver檔名請儲存為'MicrosoftWebDriver.exe'
#使用Firefox時driver檔名請儲存為'geckodriver.exe'
#使用Chrome時driver檔名請儲存為'chromedriver.exe'


# %%
def generate_selenium_dclass_options(browser = "firefox"):
    browser = browser.lower()
    options = {"firefox": FirefoxOptions(), "edge": EdgeOptions(), "chrome": ChromeOptions()}[browser]
    options.add_argument("--headless")
    options.add_argument('--start-maximized')
    if browser=="chrome":
        options.binary_location = "D:\\PortableApps\\PortableApps\\GoogleChromePortable\\App\\Chrome-bin\\chrome.exe" #可指定Chrome binary path 例如："C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    browser_argument = {
        "firefox": {
            "firefox_binary": "D:\\PortableApps\\PortableApps\\FirefoxPortable\\App\\Firefox64\\firefox.exe" #可指定Firefox binary path 如
        },
        "edge": {},
        "chrome": {}
    }[browser]
    needdriver = {"firefox": FirefoxDriver, "edge": EdgeDriver, "chrome": ChromeDriver}[browser]
    return {'needdriver': needdriver, 'options': options, 'browser_argument': browser_argument}


# %%
def initDriver(needdriver=generate_selenium_dclass_options("firefox")['needdriver'],
               options=generate_selenium_dclass_options("firefox")['options'],
               **browser_argument):
    driver = needdriver(options=options, **browser_argument)
    return driver

def save_screenshot(driver, path="1.png"):
    # Ref: https://stackoverflow.com/a/52572919/
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    driver.find_element_by_tag_name('body').screenshot(path)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])


# %%
def driver_nav_airiti_pages_and_save_screenshots(driver, docid="a0000446-199106-20-2-63-85-a"):
    htmls = []
    html_file_names = []
    urls = []
    screenshot_file_names = []
    for i, url in enumerate(["https://www.airitilibrary.com/Publication/alDetailedMesh?DocID={}","http://www.airitilibrary.cn/Publication/alDetailedMesh?DocID={}"]):
        targetUrl = url.format(docid)
        urls.append(targetUrl)
        driver.get(targetUrl)
        screenshot_file_name = "{}.png".format(i)
        screenshot_file_names.append(screenshot_file_name)
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
    return {
        'htmls': htmls,
        'html_file_names': html_file_names,
        'urls': urls,
        'screenshot_file_names': screenshot_file_names,
        'article_inf': article_inf
    }


# %%
def generate_diff_report_and_capture_screenshot(driver, html_file_names, fnameO="diff.html"):
    diff2HtmlCompare.main(html_file_names[0], html_file_names[1], fnameO, {"verbose":False, "syntax_css": "vs", "print_width": False})
    driver.get(os.path.join(os.getcwd(),fnameO) )
    diff_png_file_name = fnameO.replace("html","png")
    save_screenshot(execdriver, diff_png_file_name)
    return diff_png_file_name


# %%
def closeDriver(driver):
    driver.close()


# %%
def merge_screenshots(images_list, urls, article_desc, fontFname="./NotoSansTC-Medium.otf", fontsize=16):
    imgs = [Image.open(i) for i in images_list] #只接受上面兩個下面一個
    # merge horizontally first
    width_sorted = sorted([i.width for i in imgs])
    height_sorted = sorted([i.height for i in imgs])
    total_width = sum(width_sorted[:-1])
    max_height = height_sorted[-1]
    second_max_height = max(height_sorted[:-1])
    total_height = second_max_height+max_height
    img_merge = Image.new(imgs[0].mode, (total_width, total_height))
    font = ImageFont.truetype(fontFname, fontsize)
    x = 0
    y = 0
    for i, img in enumerate(imgs):
        if i<2:
            img_merge.paste(img, (x, 0))
            draw = ImageDraw.Draw(img_merge)
            draw.text((x+10, 0), urls[i], (196, 8, 42), font=font)
            x += img.width
        else:
            #計算置中的x位置
            this_width = img.width
            to_paste_x = int((x-this_width)/2)
            img_merge.paste(img, (to_paste_x, second_max_height))
            y += img.height
    img_merge.save(os.path.join("fetch_results", '{}.png'.format(article_desc)))
    [i.close() for i in imgs]


# %%
docid = "a0000446-199106-20-2-63-85-a"
#driver_obj = generate_selenium_dclass_options()
#execdriver = initDriver(driver_obj['needdriver'], browser_argument=driver_obj['options'])
execdriver = initDriver(**generate_selenium_dclass_options("firefox")['browser_argument'])
airiti_inf = driver_nav_airiti_pages_and_save_screenshots(execdriver, docid=docid)
diff_png_file_name = generate_diff_report_and_capture_screenshot(execdriver, airiti_inf['html_file_names'], fnameO="diff.html")
airiti_inf['screenshot_file_names'].append(diff_png_file_name)
closeDriver(execdriver)
merge_screenshots(images_list=airiti_inf['screenshot_file_names'], urls=airiti_inf['urls'], article_desc=airiti_inf['article_inf'])


# %%



# %%
if __name__ == "__main__":
    


