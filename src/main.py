from time import sleep

from captchaVerification import *


def reserve(config, start_time, end_time, ground_index):
    url = "https://reservation.sustech.edu.cn/api/blade-app/qywx/saveOrder?userid=" + config["student_id"] \
          + "&token=" + config["token"]
    captchaVerification = str(Verification())[2:-1]  # The original value seems like b'xxxxxxxx', so I use [2:-1]
    data = {
        "captchaVerification": captchaVerification,
        "customerEmail": "",
        "customerId": "1596483041392003586",
        "customerName": config["student_name"],
        "customerTel": config["student_tel"],
        "endTime": end_time,
        "groundId": config["ground_url"][str(ground_index)],
        "groundName": config["ground_name"][str(ground_index)],
        "groundType": "0",
        "gymId": "1297442093383360513",
        "gymName": "欣园网球场",
        "isIllegal": "0",
        "messagePushType": "0",
        "orderDate": config["order_time"],
        "startTime": start_time,
        "tmpEndTime": end_time,
        "tmpOrderDate": config["order_time"],
        "tmpStartTime": start_time,
        "userNum": 1
    }
    headers = config["headers"]
    try:
        re = requests.post(url, json=data, headers=headers)
        re_data = json.loads(re.text)
        if re_data["success"]:
            print("You have reserved Ground " + str(ground_index) + " from " + start_time + " to " + end_time)
            return True
        else:
            print(f"Failed to reserve Ground {str(ground_index)} from {start_time} to {end_time}--> {re.text}")
            return False
    except requests.RequestException as e:
        print(f"{e}")
        return False


if __name__ == "__main__":
    config = get_config()
    flag=0
    while flag!=1:
        for start_time, end_time in zip(config["start_time"], config["end_time"]):
            for ground_id in list(config["ground_url"].keys()):
                if ground_id == "2" or ground_id == "7":
                    continue
                # print(f"Reserve Ground {ground_id} from {start_time} to {end_time}")
                result = False
                try:
                    result = reserve(config, start_time, end_time, ground_id)
                except Exception as e:
                    pass
                if result:
                    flag=1
                    break
