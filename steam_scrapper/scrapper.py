from bs4 import BeautifulSoup
from helpers import SteamPages, JsonJobs, RequestJobs


class SteamUser:
    def __init__(self, profile_link: str) -> None:
        self.profile_link = profile_link
        self.requst_jobs = RequestJobs()
        self.steam_pages = SteamPages(profile_link)
        self.__main_page = self.steam_pages.main_page
        self.steam_id = self.steam_pages.steam_id

    def clean_text(self, text: str) -> str:
        new_text = text.replace("\t", "")
        new_text = new_text.replace("\n", "")
        new_text = new_text.replace("\r", " ")
        return new_text

    def last_activities(self) -> list:
        activities: list[dict] = []

        recent_games = self.__main_page.find_all("div", class_="recent_game")
        game: BeautifulSoup
        for game in recent_games:

            activity_info = {
                "game_name": game.find("div", class_="game_name").text,
                "game_link": game.find("div", class_="game_info_cap")
                .find("a")
                .get("href"),
                "game_play_time": self.clean_text(
                    game.find("div", class_="game_info_details").text
                ),
                "game_achievement_summary": game.find("span", class_="ellipsis").text,
                "last_game_achievements_earned": [],
            }
            last_achievements = []
            achievement: BeautifulSoup
            for achievement in game.find_all("div", class_="game_info_achievement"):
                last_achievements.append(achievement.get("data-tooltip-text"))

            activity_info["last_game_achievements_earned"] = last_achievements

            activities.append(activity_info)
        return activities

    def current_status(self) -> str:
        status = self.__main_page.find("div", class_="profile_in_game_header").text
        return status

    def recent_play_time(self) -> str:
        play_time_ = self.__main_page.find(
            "div", class_="recentgame_quicklinks recentgame_recentplaytime"
        )
        return play_time_.text.replace("\n", "")

    def current_level(self) -> str:
        level = self.__main_page.find("span", class_="friendPlayerLevelNum").text
        return level

    def profile_summary(self) -> str:
        p_summary = self.__main_page.find("div", class_="profile_summary").text
        return p_summary

    def country(self) -> str:
        country = self.__main_page.find("div", class_="header_real_name ellipsis").text
        return country.strip()

    def username(self) -> str:
        name = self.__main_page.find("span", class_="actual_persona_name").text
        return name

    def profile_pic(self) -> str:
        parent_div = self.__main_page.find("div", class_="playerAvatarAutoSizeInner")
        photo_source = parent_div.find("img").get("src")
        return photo_source

    def badges(self) -> list[dict]:
        profile_badges: list[dict] = []

        badge_page = self.steam_pages.badge_page()

        badge_list = badge_page.find("div", class_="badges_sheet").find_all(
            "div", class_="badge_row is_link"
        )
        for badge in badge_list:
            badge_link = badge.find("a").get("href")

            badge_title, badge_xp, badge_unlock_time = badge.find(
                "div", class_="badge_info_description"
            ).find_all("div")

            badge_dict = {
                "badge_link": badge_link,
                "badge_title": badge_title.text,
                "badge_xp": self.clean_text(badge_xp.text),
                "badge_unlocked_at": self.clean_text(badge_unlock_time.text),
            }
            profile_badges.append(badge_dict)

        return profile_badges

    def games(self) -> list[dict]:
        user_games: list[dict] = []
        user_page = self.steam_pages.games_page()
        tag = user_page.findAll("script")

        for result in JsonJobs.extract_json_objects(str(tag[-1])):
            user_games.append(result)
        return user_games

    def inventory(self) -> list[dict]:
        inventory_page = self.steam_pages.inventory_page()

        games_list_tabs = inventory_page.find(
            "select", id="responsive_inventory_select"
        ).find_all("option")

        game_appid_list = [
            game.get("value").replace("#", "") for game in games_list_tabs
        ]
        inventory: list[dict] = []
        for game_id in game_appid_list:
            link = f"https://steamcommunity.com/inventory/{self.steam_pages.steam_id}/{game_id}/2?l=english&count=75"

            data = self.requst_jobs.get_req(
                link,
                json=True,
            )

            inventory += JsonJobs.parse_inventory(data)

        return inventory

    def screen_shots(self) -> list[str]:
        screen_shots_source: list[str] = []

        screen_shots_page = self.steam_pages.screenshots_page()

        for screen_shot in screen_shots_page.find_all("div", class_="floatHelp"):
            screen_shot = screen_shot.find("a")
            screen_shots_source.append(screen_shot.get("href"))

        return screen_shots_source

    def recommends(self) -> list[dict]:
        recommendations: list[dict] = []
        recommendations_page = self.steam_pages.recommended_page()
        recommendations_page = recommendations_page.find("div", id="leftContents")
        recommend: BeautifulSoup
        for recommend in recommendations_page.find_all("div", class_="review_box"):
            recommended_game = {
                "appid": recommend.find("div", class_="title")
                .find("a")
                .get("href")
                .split("/")[-2],
                "title": recommend.find("div", class_="title").text,
                "posted": recommend.find("div", class_="posted").text.replace("\t", ""),
                "description": recommend.find("div", class_="content").text.replace(
                    "\t", ""
                ),
            }
            recommendations.append(recommended_game)
        return recommendations

    def artwork(self) -> list[str]:
        artworks: list[str] = []
        artwork_page = self.steam_pages.artwork_page()
        artwork_page = artwork_page.find("div", class_="imageWall5Floaters")

        for artwork in artwork_page.find_all("div", class_="floatHelp"):
            artwork = artwork_page.find("a")
            artworks.append(artwork.get("href"))

        return artworks

    def group(self) -> list[dict]:
        groups: list[dict] = []
        group_page = self.steam_pages.groups_page()
        group_list = group_page.find("div", class_="profile_groups search_results")
        group_list = group_list.find_all("div", class_="group_block invite_row")
        group_item: BeautifulSoup
        for group_item in group_list:
            group_element = {
                "title": group_item.find("a", class_="linkTitle").text,
                "link": group_item.find("a", class_="linkTitle").get("href"),
                "member_count": group_item.find(
                    "a", class_="groupMemberStat linkStandard"
                ).text,
                "in_game_member_count": group_item.find(
                    "span", class_="groupMemberStat membersInGame"
                ).text,
                "member_online": group_item.find(
                    "span", class_="groupMemberStat membersOnline"
                ).text,
                "member_in_chat": group_item.find(
                    "a", class_="groupMemberStat linkStandard steamLink"
                ).text,
            }
            groups.append(group_element)
        return groups

