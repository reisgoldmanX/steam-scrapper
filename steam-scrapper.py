from src.helpers import WritingJobs
from src.scrapper import SteamUser

import argparse
from tqdm import tqdm


# user = SteamUser("https://steamcommunity.com/id/reisXXX1/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "profile_link", help="The profile link you want to scrape.", type=str
    )
    parser.add_argument(
        "-d",
        "--download",
        help="Downloads and writes data to a directory.",
        action="store_true",
    )
    parser.add_argument(
        "action", choices=["all", "images", "text"], help="Choose which data to scrape."
    )

    args = parser.parse_args()
    procces(args)


def procces(arguments):
    profile = SteamUser(arguments.profile_link)
    methods = [
        profile.username,
        profile.country,
        profile.profile_summary,
        profile.current_level,
        profile.current_status,
        profile.last_activities,
        profile.badges,
        profile.games,
        profile.inventory,
        profile.recommends,
        profile.group,
        profile.screen_shots,
        profile.profile_pic,
        profile.artwork,
    ]
    profile.requst_jobs
    if arguments.download:
        output_dir = WritingJobs.create_output_dir(file_name=profile.steam_id)
        json_dir = WritingJobs.create_json(output_dir)

    if arguments.action == "all":
        method_list = methods
    elif arguments.action == "text":
        method_list = methods[:11]
    elif arguments.action == "images":
        method_list = methods[11:]

    for method in tqdm(method_list):

        json_obj = {method.__name__: method()}

        if arguments.download:
            WritingJobs.write_json(json_dir, json_obj)

            if method.__name__ in ["screen_shots", "artwork"]:
                for link in json_obj[method.__name__]:
                    WritingJobs.download_content(
                        profile.requst_jobs, output_dir, (method.__name__, link)
                    )

            elif method.__name__ == "profile_pic":
                WritingJobs.download_content(
                    profile.requst_jobs,
                    output_dir,
                    (method.__name__, json_obj[method.__name__]),
                )


if __name__ == "__main__":
    main()
