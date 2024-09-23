import concurrent
import contextlib
import math
import threading

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import regex as re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from selenium.webdriver.support.select import Select
from datetime import datetime


@contextlib.contextmanager
def timer(line):
    start = time.time()
    yield
    end = time.time()
    print("time right now:", datetime.now())
    print(line + " elapsed time:", end - start, "s")


def scroll_down(driver, number_of_reviews_per_game=0, additional_info=""):
    with timer("scroll down" + additional_info):
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_limit = number_of_reviews_per_game // 10
        if scroll_limit == 0:
            scroll_limit = 500
        counter = 0
        check = False
        while True:

            if scroll_limit <= counter:
                print("scrolled down till the specified number of reviews was obtained")
                print("number of scrolls down:", counter)
                break
            # Scroll down to the bottom.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(2)

            # Calculate new scroll height and compare with last scroll height.
            new_height = driver.execute_script("return document.body.scrollHeight")
            if number_of_reviews_per_game == 0:
                if new_height == last_height:
                    if check:
                        break
                    else:
                        check = True
                        time.sleep(1)
                else:
                    check = False

                last_height = new_height

            counter += 1

            print("number of scrolls till now:", counter)
            print("time right now:", datetime.now())


def add_options(options):
    options.add_argument("headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)


def passing_age_page(driver):
    with timer("passing age page"):
        try:
            year = driver.find_element(By.ID, "ageYear")
            dropdown = Select(year)
            dropdown.select_by_value("1999")
            view_page_button = driver.find_element(By.ID, "view_product_page_btn")
            driver.execute_script("arguments[0].click()", view_page_button)
            time.sleep(1)
        except:
            pass


def get_game_data(driver, link):
    with timer("game data"):
        for i in range(3):
            try:
                driver.get(link)

                passing_age_page(driver)

                scroll_down(driver, additional_info=" game page")

                soup = BeautifulSoup(driver.page_source, "lxml")
                break
            except:
                print("error fetching game data")
                time.sleep(2)
                continue

        game_description = {"name": soup.find_all("div", class_="apphub_AppName")[0].text.strip()
                            if soup.find_all("div", class_="apphub_AppName") is not None
                            else "",
                            "short_description": soup.find("div", class_="game_description_snippet").text.strip()
                            if soup.find("div", class_="game_description_snippet") is not None
                            else "",
                            "long_description": soup.find_all("div", id="aboutThisGame")[0].text.strip()
                            if soup.find_all("div", id="aboutThisGame") is not None
                            else "",
                            "genres": []
                            ,
                            "minimum_system_requirement":
                                [
                                    #    requirement.text.strip()
                                    # for requirement in
                                    # soup.find("div", class_=re.compile(
                                    #     "game_area_sys_req_leftCol|game_area_sys_req_full"))
                                    # .find("ul", class_="bb_ul")
                                    # .find_all("li")
                                ],
                            "recommend_system_requirement": [
                                # requirement.text.strip()
                                #                              for requirement in
                                #                              soup.find("div", class_=re.compile(
                                #                                  "game_area_sys_req_rightCol|game_area_sys_req_full"))
                                #                              .find("ul", class_="bb_ul")
                                #                              .find_all("li")
                            ],
                            "release_date": soup.find("div", class_="release_date").find("div", class_="date").text,
                            "developer": [[developer.text.strip()
                                           for developer in
                                           soup.find("div", class_="glance_ctn_responsive_left")
                                           .find_all("div", class_="dev_row")[0]
                                           .find_all("a")
                                           ]],
                            "publisher": [
                                [developer.text.strip()
                                 for developer in
                                 soup.find("div", class_="glance_ctn_responsive_left")
                                 .find_all("div", class_="dev_row")[1]
                                 .find_all("a")
                                 ]
                            ],
                            "overall_player_rating": soup.find_all("div", class_="user_reviews_summary_row")[1]
                            .find("span", class_=re.compile("game_review_summary"))
                            .text.strip()
                            if soup.find_all("div", class_="user_reviews_summary_row") is not None
                            else "",
                            "number_of_reviews_from_purchased_people":
                                soup.find_all("div", class_="user_reviews_summary_row")[1]
                                .find_all("span")[1]
                                .text.strip()
                                if soup.find_all("div", class_="user_reviews_summary_row") is not None
                                else "",
                            "number_of_english_reviews": soup.find("div", class_="user_reviews_filter_score visible")
                            .text
                            .split()[1]
                            if soup.find("div", class_="user_reviews_filter_score visible") is not None
                            else "",
                            "link": link
                            }
        genre = soup.find("div", class_="glance_tags popular_tags")
        if genre is None:
            game_description["genres"] = []
        else:
            genres = genre.find_all("a", class_="app_tag")
            if genres is not None:
                game_description["genres"].append([])
                for i in genre.find_all("a", class_="app_tag"):
                    game_description["genres"][0].append(i.text.strip())
            else:
                game_description["genres"] = []

        minimum_system_requirement = soup.find("div", class_=re.compile(
            "game_area_sys_req_leftCol|game_area_sys_req_full"))
        if minimum_system_requirement is None:
            game_description["minimum_system_requirement"] = []
        else:
            minimum_system_requirement = minimum_system_requirement.find("ul", class_="bb_ul")
            if minimum_system_requirement is None:
                game_description["minimum_system_requirement"] = []
            else:
                minimum_system_requirement = minimum_system_requirement.find_all("li")
                if minimum_system_requirement is None:
                    game_description["minimum_system_requirement"] = []
                else:
                    game_description["minimum_system_requirement"].append([])
                    for i in minimum_system_requirement:
                        game_description["minimum_system_requirement"][0].append(i.text.strip())

        recommend_system_requirement = soup.find("div", class_=re.compile(
            "game_area_sys_req_rightCol|game_area_sys_req_full"))
        if recommend_system_requirement is None:
            game_description["recommend_system_requirement"] = []
        else:
            recommend_system_requirement = recommend_system_requirement.find("ul", class_="bb_ul")
            if recommend_system_requirement is None:
                game_description["recommend_system_requirement"] = []
            else:
                recommend_system_requirement = recommend_system_requirement.find_all("li")
                if recommend_system_requirement is None:
                    game_description["recommend_system_requirement"] = []
                else:
                    game_description["recommend_system_requirement"].append([])
                    for i in recommend_system_requirement:
                        game_description["recommend_system_requirement"][0].append(i.text.strip())
        print(game_description)
        return game_description


def get_game_reviews(driver, game_name, total_number_of_reviews_per_games, max_number_of_reviews_per_game=0):
    with timer("Game reviews " + game_name):
        for i in range(3):
            try:
                all_reviews_button = driver.find_element(By.ID, "ViewAllReviewssummary").find_element(By.TAG_NAME, "a")

                driver.execute_script("arguments[0].click()", all_reviews_button)

                time.sleep(2)

                passing_age_page(driver)

                number_of_reviews = 0

                if total_number_of_reviews_per_games > max_number_of_reviews_per_game:
                    number_of_reviews = max_number_of_reviews_per_game
                else:
                    number_of_reviews = total_number_of_reviews_per_games

                scroll_down(driver, number_of_reviews, " reviews page for " + game_name)

                soup = BeautifulSoup(driver.page_source, 'lxml')

                review_pages = soup.find_all("div", id=re.compile(r"page\d"))[:max_number_of_reviews_per_game]

                break
            except:
                print("error fetching reviews from", game_name)
                time.sleep(2)
                continue

        reviews = []
        for review_page in review_pages:
            reviews_cards = review_page.find_all("div", class_="apphub_Card modalContentLink interactable")
            for review_card in reviews_cards:
                review = {
                    "helpful":
                        review_card.find("div", class_="found_helpful").text.split()[0].strip()
                        if review_card.find("div", class_="found_helpful").text.split()[0].strip() != "No"
                        else "0",
                    "funny":
                        review_card.find("div", class_="found_helpful").text.split()[5].replace("helpful", "")
                        if review_card.find("div", class_="found_helpful").text.split()[6] in ["people", "person"]
                        else "0",
                    "hours_played": review_card.find("div", class_="hours").text.split()[0].strip(),
                    "recommendation": review_card.find("div", class_="title").text.strip(),
                    "date": ' '.join(review_card.find("div", class_="date_posted").text.split()[1:]).strip(),
                    "review": ' '.join(
                        review_card.find("div", class_="apphub_CardTextContent").text.split()[3:]).strip(),
                    "username": review_card.find("div", class_="apphub_friend_block_container").text.strip(),
                    "game_name": game_name
                }
                reviews.append(review)

        print("Number of reviews " + game_name + " :", len(reviews))
        return reviews


def get_all_needed_genres_links(driver, link, genres):
    with (timer("genres links")):
        for i in range(3):
            try:
                driver.get(link)

                soup = BeautifulSoup(driver.page_source, "lxml")

                categories_tags = soup.find_all("div", class_="popup_body popup_menu_twocol_new")[1] \
                    .find_all("a", class_="popup_menu_item")

                links = {tag.text.strip(): tag["href"] for tag in categories_tags if tag.text.strip() in genres}
                break

            except:
                time.sleep(2)
                continue
        print("Number of Links:", len(links))
        print(links)
        return links


def click_show_more_in_genre_page(driver, number_of_clicks):
    with timer("click show more in genre page"):
        for i in range(0, number_of_clicks):
            for i in range(3):
                try:
                    show_more_button = driver.find_element(By.CLASS_NAME, "_36qA-3ePJIusV1oKLQep-w") \
                        .find_element(By.TAG_NAME, "button")
                    driver.execute_script("arguments[0].click()", show_more_button)
                    time.sleep(2)
                    break
                except:
                    time.sleep(2)


def change_ranking(driver, rank):
    with timer("changing ranking"):
        for i in range(3):
            try:
                ranks = driver.find_elements(By.CSS_SELECTOR, "div[class^='KDLASaMCaASZ6LnF3kQY8']")

                if rank.strip() == "Sales":
                    driver.execute_script("arguments[0].click()", ranks[0])
                elif rank.strip() == "Revenue":
                    driver.execute_script("arguments[0].click()", ranks[2])
                elif rank.strip() == "Review":
                    driver.execute_script("arguments[0].click()", ranks[3])

                time.sleep(2)
                break
            except:
                time.sleep(2)


def get_games_links_from_genre(driver, link, number_of_games_per_ranking, ranks):
    with timer("get game links"):
        with (timer("genres links")):
            for i in range(3):
                try:
                    driver.get(link)

                    time.sleep(2)

                    all_games_part = driver.find_element(By.ID, "SaleSection_13268")
                    driver.execute_script("arguments[0].scrollIntoView()", all_games_part)
                    break
                except:
                    time.sleep(2)
                    continue

        number_of_clicks = math.ceil(number_of_games_per_ranking / 12) - 1

        print("number of clicks:", number_of_clicks)

        games_links_list = {}

        for rank in ranks:
            change_ranking(driver, rank)

            click_show_more_in_genre_page(driver, number_of_clicks)
            for i in range(3):
                try:
                    soup = BeautifulSoup(driver.page_source, 'lxml')

                    games_tag_list = soup.find("div", id="SaleSection_13268") \
                                         .find_all("div", class_="_3rrH9dPdtHVRMzAEw82AId")[
                                     :number_of_games_per_ranking]

                    top_games = {tag.text.strip(): tag.find("a")["href"] for tag in games_tag_list}
                    break
                except:
                    time.sleep(2)
            games_links_list[rank] = top_games

        print("Number of games:", len(games_links_list))

        return games_links_list


def process_game(game_link, max_number_of_reviews_per_game, options, columns, game_description_columns):
    driver = webdriver.Edge(options=options)

    try:
        game_description = get_game_data(driver, game_link)
        game_players_reviews = get_game_reviews(driver, game_description["name"],
                                                int(game_description["number_of_english_reviews"].replace(",", "")),
                                                max_number_of_reviews_per_game)

        games_players_reviews_dataframe = pd.DataFrame(game_players_reviews, columns=columns)
        game_description_dataframe = pd.DataFrame(game_description, columns=game_description_columns)
        with threading.Lock():
            games_players_reviews_dataframe.to_csv("steam_game_reviews.csv", mode="a", header=False, index=False)
            print(game_description_dataframe)
            game_description_dataframe.to_csv("games_description.csv", mode="a", header=False, index=False)

        print()
    finally:
        driver.quit()

    return game_description


def main():
    games_description_columns = ["name", "short_description", "long_description", "genres",
                                 "minimum_system_requirement", "recommend_system_requirement", "release_date",
                                 "developer", "publisher",
                                 "overall_player_rating", "number_of_reviews_from_purchased_people",
                                 "number_of_english_reviews", "link"]

    games_players_reviews_columns = ["review", "hours_played", "helpful", "funny", "recommendation", "date",
                                     "game_name", "username"]

    games_genre_ranking_columns = ["game_name", "genre", "rank_type", "rank"]

    core_genres = [
        "Action",
        "Adventure",
        "Role-Playing",
        "Strategy",
        "Simulation",
        "Sports & Racing"
    ]

    ranks = ["Sales", "Revenue", "Review"]

    max_number_of_reviews_per_game = 5000
    number_of_games_per_ranking = 40
    max_threads = 5

    games_players_reviews_dataframe = pd.DataFrame(columns=games_players_reviews_columns)
    games_players_reviews_dataframe.to_csv("steam_game_reviews.csv", index=False)

    games_description_dataframe = pd.DataFrame(columns=games_description_columns)
    games_description_dataframe.to_csv("games_description.csv", index=False)

    games_genre_ranking = {col: [] for col in games_genre_ranking_columns}

    options = webdriver.EdgeOptions()

    add_options(options)

    driver = webdriver.Edge(options=options)

    home_page_link = "https://store.steampowered.com/"

    genres_links = get_all_needed_genres_links(driver, home_page_link, core_genres)

    genre_games_links = {
        genre: get_games_links_from_genre(driver, genre_link, number_of_games_per_ranking, ranks)
        for genre, genre_link in genres_links.items()
    }

    driver.quit()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        for genre, genre_games_links in genre_games_links.items():
            print(genre)
            for rank_type, games_links in genre_games_links.items():
                counter = 0

                for game, game_link in games_links.items():

                    counter += 1

                    if game not in games_genre_ranking["game_name"]:
                        print(game)
                        executor.submit(process_game, game_link, max_number_of_reviews_per_game, options,
                                        games_players_reviews_columns, games_description_columns)

                    games_genre_ranking["game_name"].append(game)
                    games_genre_ranking["genre"].append(genre)
                    games_genre_ranking["rank_type"].append(rank_type)
                    games_genre_ranking["rank"].append(counter)

                    print(games_genre_ranking)

    games_genre_ranking_dataframe = pd.DataFrame(games_genre_ranking)

    games_genre_ranking_dataframe.to_csv("games_ranking.csv", index=False)


if __name__ == "__main__":
    main()
