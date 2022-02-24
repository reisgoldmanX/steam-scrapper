from bs4 import BeautifulSoup
import requests
import os
from datetime import date


class SteamUser:
    def __init__(self, profile_link: str) -> None:
        self.profile_link = profile_link
        self.__main_page = self._request_to_main()

    def _request_to_main(self):
        req = requests.get(self.profile_link)

        if req.status_code == 200:
            return BeautifulSoup(req.content, "lxml")
        elif req.status_code == 400:
            raise Exception("Bad request: {}".format(req.status_code))

    def last_activities(self) -> str:
        activities = {"game_name": "", "game_link": "", "game_play_time": ""}
        recent_games = self.__main_page.find_all("div", class_="recent_game")
        for game in recent_games:
            game_link = game.find("div", class_="game_info_cap").find("a").get("href")
            game_info_details = game.find("div", class_="game_info_details").text
            game_name = game.find("div", class_="game_name").get("a").text

    def current_status(self) -> str:
        status_ = self.__main_page.find("div", class_="profile_in_game_header").text
        print(status_)

    def recent_play_time(self) -> str:
        play_time_ = self.__main_page.find(
            "div", class_="recentgame_quicklinks recentgame_recentplaytime"
        )
        return play_time_.text.replace("\n", "")

    def current_level(self) -> str:
        level_ = self.__main_page.find("span", class_="friendPlayerLevelNum").text
        return level_

    def profile_summary(self) -> str:
        profile_summary_ = self.__main_page.find("div", class_="profile_summary").text
        return profile_summary_

    def country(self) -> str:
        country_ = self.__main_page.find("div", class_="header_real_name ellipsis").text
        return country_.strip()

    def username(self) -> str:
        username_ = self.__main_page.find("span", class_="actual_persona_name").text
        return username_

    def profile_pic(self) -> str:
        parent_div = self.__main_page.find("div", class_="playerAvatarAutoSizeInner")
        photo_source = parent_div.find("img").get("src")
        return FileOutput("reisXXX1").profile_pic(photo_source)


class FileOutput:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.user_folder = self._create_folder()

    def _create_folder(self) -> str:
        folder_name = f"[{date.isoformat(date.today())}]" + self.user_id
        os.mkdir(folder_name)
        return folder_name

    def profile_pic(self, src: str) -> str:
        full_path = f"{self.user_folder}/{os.path.basename(src)}"
        with open(full_path, "wb") as profile_pic_f:
            profile_pic_f.write(requests.get(src).content)
        return os.path.basename(src)
