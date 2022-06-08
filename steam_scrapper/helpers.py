from bs4 import BeautifulSoup
import requests

from json import JSONDecoder


class RequestJobs:
    def __init__(self):
        self.session = requests.Session()

    def get_req(self, link: str, json=False, proxy=True, timeout=10) -> str:
        try:
            if proxy is False:
                req = self.session.get(url=link, timeout=timeout)
            else:
                req = self.session.get(url=link, timeout=timeout)
        except requests.exceptions.RequestException as error:
            raise error
        if json is True:
            return req.json()
        else:
            return req.content


class SteamPages:
    def __init__(self, profile_link: str) -> None:
        self.profile_link = profile_link
        self.request_jobs = RequestJobs()
        self.main_page = BeautifulSoup(self.request_jobs.get_req(profile_link), "lxml")
        self.page_links = self.findPages()
        self.steam_id = self.get_SteamID()

    def get_SteamID(self) -> str:
        link_id = self.profile_link.split("/")[-2]
        steam_id_page = BeautifulSoup(
            self.request_jobs.get_req(
                "https://www.steamidfinder.com/lookup/" + link_id
            ),
            "lxml",
        )
        steam_id = steam_id_page.find_all("code")[2].text
        return steam_id

    def findPages(self) -> list[str]:
        source_parents = self.main_page.find_all(
            "div", class_="profile_count_link ellipsis"
        )
        pages = [page.find("a").get("href") for page in source_parents]
        return pages

    def badge_page(self) -> BeautifulSoup:
        return BeautifulSoup(self.request_jobs.get_req(self.page_links[0]), "lxml")

    def games_page(self) -> BeautifulSoup:
        return BeautifulSoup(
            self.request_jobs.get_req(self.page_links[1] + "&sort=playtime"), "lxml"
        )

    def inventory_page(self) -> BeautifulSoup:
        return BeautifulSoup(self.request_jobs.get_req(self.page_links[2]), "lxml")

    def screenshots_page(self) -> BeautifulSoup:
        return BeautifulSoup(
            self.request_jobs.get_req(
                self.page_links[3]
                + "/?appid=0&sort=newestfirst&browsefilter=myfiles&view=grid"
            ),
            "lxml",
        )

    def videos_page(self) -> BeautifulSoup:
        return BeautifulSoup(self.request_jobs.get_req(self.page_links[4]), "lxml")

    def recommended_page(self) -> BeautifulSoup:
        return BeautifulSoup(self.request_jobs.get_req(self.page_links[5]), "lxml")

    def images_page(self) -> BeautifulSoup:
        return BeautifulSoup(self.request_jobs.get_req(self.page_links[6]), "lxml")

    def groups_page(self) -> BeautifulSoup:
        return BeautifulSoup(self.request_jobs.get_req(self.page_links[7]), "lxml")

    def artwork_page(self) -> BeautifulSoup:
        id = self.profile_link.split("/")[-2]
        link = f"https://steamcommunity.com/id/{id}/images/?appid=0&sort=newestfirst&browsefilter=myfiles&view=grid"
        return BeautifulSoup(self.request_jobs.get_req(link), "lxml")


class JsonJobs:
    def parse_inventory(data: dict) -> list[dict]:
        inventory: list[dict] = []
        try:
            data = data["descriptions"]
        except KeyError:
            return []

        for element in data:
            appid = element["appid"]
            name = element["market_hash_name"]
            tradable = element["tradable"]
            try:
                description = "".join(line["value"] for line in element["descriptions"])
            except KeyError:
                description = ""

            try:
                tags = [
                    f"{tag['category']}: {tag['internal_name']}"
                    for tag in element["tags"]
                ]
            except KeyError:
                tags = []

            item = {
                "appid": appid,
                "name": name,
                "tradable": tradable,
                "description": description,
                "tags": tags,
            }
            inventory.append(item)

        return inventory

    def extract_json_objects(text, decoder=JSONDecoder()):
        """Find JSON objects in text, and yield the decoded JSON data

        Does not attempt to look for JSON arrays, text, or other JSON types outside
        of a parent JSON object.

        """
        pos = 0
        while True:
            match = text.find("{", pos)
            if match == -1:
                break
            try:
                result, index = decoder.raw_decode(text[match:])
                yield result
                pos = match + index
            except ValueError:
                pos = match + 1
