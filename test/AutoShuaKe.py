from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

base_url = "https://gsscut.xuetangx.com/lms#/video/4995/5873/{}/{}/0/videoDiscussion"
"""
{"fb42355c-4cb6-4970-af96-ca8cfcd2f783:39589c29-0e25-46fc-b343-7ede3aee2057:7130": 1,
      "fb42355c-4cb6-4970-af96-ca8cfcd2f783:39589c29-0e25-46fc-b343-7ede3aee2057:7131": 2,
      "fb42355c-4cb6-4970-af96-ca8cfcd2f783:39589c29-0e25-46fc-b343-7ede3aee2057:7132": 3,
      "fb42355c-4cb6-4970-af96-ca8cfcd2f783:39589c29-0e25-46fc-b343-7ede3aee2057:7133": 4,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:17c08704-5122-4d1b-80a2-86f8370db7d5:7134": 5,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:17c08704-5122-4d1b-80a2-86f8370db7d5:7135": 6,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:17c08704-5122-4d1b-80a2-86f8370db7d5:7136": 7,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:17c08704-5122-4d1b-80a2-86f8370db7d5:7137": 8,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:17c08704-5122-4d1b-80a2-86f8370db7d5:7138": 9,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:f27e84ae-c8d3-4494-afbf-da58e3ade209:7139": 10,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:fc33ffc6-190d-4463-a382-22a9ff697a30:7140": 11,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:6b491156-c8ce-4763-975e-57dd677c7850:7141": 12,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:da9f3d4e-62a0-446c-a3b4-55573c091268:7142": 13,
      "722ba994-5a46-4c6a-91fb-a28d7620dab5:da9f3d4e-62a0-446c-a3b4-55573c091268:7143": 14,
      "52822144-6b87-47d7-85a1-5fb7371dc1d2:329ea8e6-9b5c-42c3-be8f-5b101c41298c:7144": 16,
      "52822144-6b87-47d7-85a1-5fb7371dc1d2:329ea8e6-9b5c-42c3-be8f-5b101c41298c:7145": 17,
      "52822144-6b87-47d7-85a1-5fb7371dc1d2:329ea8e6-9b5c-42c3-be8f-5b101c41298c:7146": 18,
      "52822144-6b87-47d7-85a1-5fb7371dc1d2:329ea8e6-9b5c-42c3-be8f-5b101c41298c:7147": 19,
      "52822144-6b87-47d7-85a1-5fb7371dc1d2:329ea8e6-9b5c-42c3-be8f-5b101c41298c:7148": 20,
      "52822144-6b87-47d7-85a1-5fb7371dc1d2:329ea8e6-9b5c-42c3-be8f-5b101c41298c:7149": 21,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7150": 23,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7151": 24,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7152": 25,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7153": 26,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7154": 27,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7155": 28,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7156": 29,
      "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:0c4352b3-cd9d-4995-a97d-e82b5d74809a:7157": 30,
      "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7158": 32,
      "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7159": 33,
      "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7160": 34,
      "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7161": 35,
      }"""
jj = {
    "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7152": 25,
    "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7153": 26,
    "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7154": 27,
    "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7155": 28,
    "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:5fde9562-92f2-45b3-b1f9-9a460507c34a:7156": 29,
    "b4ba731c-b6a8-4263-b9ca-40a11ab580a6:0c4352b3-cd9d-4995-a97d-e82b5d74809a:7157": 30,
    "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7158": 32,
    "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7159": 33,
    "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7160": 34,
    "8ef5f6a7-147c-4b6d-b5ec-72a38c8e3d4f:ce0d04aa-9bb2-4261-b6c9-898def7ea217:7161": 35,
}

brower = webdriver.Chrome()
brower.get(
    "https://gsscut.xuetangx.com/lms#/video/4995/5873/52822144-6b87-47d7-85a1-5fb7371dc1d2/7147/0/videoDiscussion")

time.sleep(1)

# 输入账号和密码
brower.find_element_by_xpath("//*[@id='stu-code']").send_keys("201821039149")
brower.find_element_by_xpath("/html/body/div[1]/div[4]/div[2]/div[2]/div[2]/input[2]").send_keys("5515225gg5")

# 输入完成后进行跳转
button = brower.find_element_by_xpath("/html/body/div[1]/div[4]/div[2]/div[2]/button")
while True:
    try:
        button.is_displayed()  # 当按钮被点击以后 ，就会消失，监控按钮的点击事件
        time.sleep(1)
    except Exception as e:
        break
for k, _ in jj.items():  # type:str
    kk = k.split(":")
    url = base_url.format(kk[0], kk[2])  # 填充url

    brower.get(url)

    time.sleep(1)
    try:
        # 点击播放和关闭声音
        brower.find_element_by_xpath("//*[@id='video-box']/div/div/div[1]/div[1]").click()  # 点击播放按钮
        brower.find_element_by_xpath("//*[@id='video-box']/div/div/div[1]/div[3]/div[1]").click()  # 点击关闭声音按钮
        beisu = brower.find_element_by_xpath(r'//*[@id="video-box"]/div/div/div[1]/div[5]/div')
        time.sleep(1)
        ActionChains(brower).move_to_element(beisu).perform()
        time.sleep(0.5)
        brower.find_element_by_xpath('//*[@id="video-box"]/div/div/div[1]/div[5]/ul/li[1]').click()

        #  取消事件的监听
        brower.execute_script('''
                            function ss(){
            console.log("111");
        }
        window.onblur = ss;''')

        # 获取进度
        jindu = brower.find_element_by_xpath("//*[@id='video-box']/div/div/div[1]/div[6]/div[3]/div")
        while True:
            if "left: 100%;" == jindu.get_attribute("style"):
                break
            time.sleep(3)
        print("{} is done!!".format(url))
    except Exception as e:
        continue
