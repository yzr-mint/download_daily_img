from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import time, re

# 定义爬取的目标网站的URL
url = "https://postimg.cc/gallery/4cbmpHW"
download_dir = r"C:\Users\14491\Desktop\get-picture\downloaded_images"
driver_path = "D:/工具/edge_driver/msedgedriver.exe"
pattern = r'https://postimg\s*\.\s*cc/gallery/([^\s\n]+)'
def handle_text(text : str):
    try:    
        match = re.findall(pattern, text)[0].replace(' ', '')
    except:
        print(f"刚刚下载的图床：{text}")        
        return text
    link = f'https://postimg.cc/gallery/{match}'
    print(f"刚刚下载的图床：{link}")
    return link         
    

def spider(text : str, driver_path : str, download_dir : str):
    url = handle_text(text)
    # 创建Edge Options对象
    options = Options()

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,  # 不提示下载对话框
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless") # 启用无头模式
    options.add_argument("--disable-gpu")
    # 设置用户代理字符串
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.112'
    options.add_argument(f'user-agent={user_agent}')

    # 创建一个Service对象并传入WebDriver的路径
    service = Service(executable_path=driver_path)

    # 使用配置好的Options对象创建Edge浏览器实例
    driver = webdriver.Edge(service=service, options=options)
    driver.get(url)

    start_time = time.time()
    # 等待#thumb-list元素加载完成
    try:
        thumb_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'thumb-list'))
        )
    
        # 获取所有的缩略图元素
        thumb_items = thumb_list.find_elements(By.CLASS_NAME, 'thumb')
        img_urls = []
        for thumb_item in thumb_items:
            # 获取图片链接
            img_urls.append(thumb_item.find_element(By.CLASS_NAME, 'img').get_attribute('href'))
        for img_url in img_urls:
            
            driver.get(img_url)
            
            # 等待下载链接加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'download'))
            ).click()
        
            # 稍微等待，以模拟用户浏览行为
            time.sleep(1)

    except Exception as e:
        print(f'发生错误：{e}')

    finally:
        # 等待下载完成    
        time.sleep((time.time() - start_time)/5)   
        # 关闭浏览器
        driver.quit()
