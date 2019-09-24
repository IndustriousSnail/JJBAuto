import json
import random
import time

import requests
from pyquery import PyQuery as pq

import bet
import utils


class JJB(object):

    def __init__(self, url="https://www.jjblove.com/"):
        self.session = None
        self.url = url
        self.is_login = False
        self.session2 = requests.session()
        self.session2.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
        })

    def login(self, username, password):
        self.session = requests.session()
        data = {
            "username": username,
            "password": password,
            "auto_login": 1
        }
        time.sleep(0.2)
        resp = self.session.post(self.url + "Index/Index/Login.html?t=" + utils.get_random(), data=data)
        if resp.ok:
            print("登录成功")
            self.is_login = True

        # todo 保存session到文件

    def sign_in(self):
        if not self.is_login:
            raise Exception("请先登录")

        time.sleep(0.5)
        resp = self.session.post(self.url + "UserAjax/SignInDay?t=" + utils.get_random())
        if resp.ok:
            print(json.loads(resp.text)['message'])
        else:
            print("签到失败")


    def get_gameList(self):
        param = {
            "t": utils.get_random(),
            "nav_code": "live",
            "game_type_id": 0,
            "date": utils.get_today_timestamp(),
            "page": 1
        }
        result = []

        def req_and_parse():
            time.sleep(0.5)
            resp = self.session2.get(self.url + "gameAjax/gameList", params=param)
            if resp.text is None or len(resp.text) < 10:
                return
            print("获取所有列表成功")
            doc = pq(resp.text)
            count = 0
            for item in doc(".game_item").items():
                result.append({
                    "data-game-id": item.attr("data-game-id"),
                    "text": item.text()
                })
                count += 1
            if count > 2:
                param["page"] += 1
                req_and_parse()

        req_and_parse()
        return result

    def get_info_by_name(self, home_field, visiting_field):
        game_list = self.get_gameList()
        game = None
        for game_item in game_list:
            if home_field in game_item["text"] and visiting_field in game_item["text"]:
                game = game_item
                break
        if game is None:
            raise Exception("没找到竞猜项")

        form_data = {
            "game_id": game["data-game-id"],
            "is_sort": 0,
            "category_id": 3
        }
        time.sleep(0.5)
        resp = self.session2.post(self.url + "gameAjax/pointsList?t=" + utils.get_random(), data=form_data)
        print("获取详细列表成功")
        doc = pq(resp.text)

        data_key = None
        for tab_box_item in doc(".tab_list_box").items():
            if (tab_box_item(".box_title").text() != '总局' and '比赛中' in tab_box_item(".game_status").text())\
                    or ('竞猜中' in tab_box_item(".game_status").text()):
                data_key = tab_box_item.attr("data-key")
                break
        if data_key is None:
            raise Exception("当前没有进行中比赛")

        for detail_item in doc(".detail_content").items():
            if detail_item.attr("data-key") == data_key:
                doc = detail_item
                break
            else:
                doc = None

        if doc is None:
            raise Exception("data-key没有对应上")
        data_point_id_list = []
        for bet_item in doc(".jq-reload-points").items():
            data_point_id_list.append(bet_item.attr("data-point-id"))
        return data_point_id_list

    def refresh_bet_price(self, home_field, visiting_field):
        data_point_id_list = self.get_info_by_name(home_field, visiting_field)
        if len(data_point_id_list) <= 0:
            raise Exception("获取data-point-id失败")

        data_point_id = data_point_id_list[0]  # 滚电子竞技时只看第一个
        print("point_ids: " + str(data_point_id))

        count = 0
        while True:
            form_data = {
                "point_ids": data_point_id,
                "is_liveorfix": 1
            }
            time.sleep(3)
            resp = self.session2.post(self.url + "GameAjax/ReloadPoints.html?t=" + utils.get_random(), data=form_data)
            resp_data = json.loads(resp.text)
            is_pause = False
            if 'danger_status' in resp_data['data'][0] and resp_data['data'][0]['danger_status'] == 1:
                is_pause = True
            left_rate = float(resp_data['data'][0]["team_points"][0]["point"])
            right_rate = float(resp_data['data'][0]["team_points"][1]["point"])
            print("主场赔率：%s, 客场赔率：%s, 是否停盘：%s" % (left_rate, right_rate, is_pause))
            count += 1
            print(count)
            if not is_pause:
                rate = {
                    "left": left_rate,
                    "right": right_rate,
                }
                bet.Bet().bet(rate)


jjb = JJB()
# jjb.login("zhaohf358", "zhaohongfei")
# jjb.sign_in()

jjb.refresh_bet_price("Sparking", "Team")

