## Steam Game Reviews Scraper

This project is an automated scraper that collects user reviews and game metadata from Steam, leveraging **Selenium** and **BeautifulSoup** in **Python**. The scraper operates responsibly, abiding by Steam's `robots.txt` file to ensure ethical web scraping practices.

### Key Features:
- **Selenium Automation**: Uses Selenium WebDriver to dynamically scroll and load additional reviews from Steam game pages, enabling large-scale data collection.
- **BeautifulSoup Parsing**: Parses the HTML content retrieved by Selenium to extract meaningful information like reviews and game details.
- **Headless Mode**: Runs in a headless Chrome browser to improve performance and reduce system overhead.
- **Ranking-Based Data Collection**: Scrapes data from the top 40 games ranked by sales, revenue, and reviews in six major game genres:
  - Action
  - Adventure
  - Role-Playing
  - Strategy
  - Simulation
  - Sports & Racing
- **Multi-threading**: Implements threading to simultaneously scrape multiple games, enhancing efficiency.
- **Customizable Review Limits**: Allows for specifying the number of reviews per game.

### Data Collected:
The scraper gathers extensive information on both games and player reviews:

1. **Game Descriptions**:
   - Columns:
     - `name`: The name of the game.
     - `short_description`: A brief description of the game.
     - `long_description`: A more detailed description of the game.
     - `genres`: The game's genre(s).
     - `minimum_system_requirement`: The minimum system requirements for the game.
     - `recommend_system_requirement`: The recommended system requirements.
     - `release_date`: The game's release date.
     - `developer`: The game's developer(s).
     - `publisher`: The game's publisher(s).
     - `overall_player_rating`: The overall player rating for the game.
     - `number_of_reviews_from_purchased_people`: The number of reviews from verified purchases.
     - `number_of_english_reviews`: The number of English-language reviews.
     - `link`: The URL to the game's Steam page.

2. **Player Reviews**:
   - Columns:
     - `review`: The text of the user’s review.
     - `hours_played`: Total hours the user has played the game.
     - `helpful`: The number of helpful votes the review received.
     - `funny`: The number of "funny" votes the review received.
     - `recommendation`: Whether the user recommends the game (positive/negative).
     - `date`: The date the review was posted.
     - `game_name`: The name of the game the review refers to.
     - `username`: The username of the reviewer.

3. **Genre-Based Ranking**:
   - Columns:
     - `game_name`: The name of the game.
     - `genre`: The genre of the game.
     - `rank_type`: The type of rank (e.g., sales, revenue, reviews).
     - `rank`: The game's ranking within that genre.

### File Outputs:
1. **Game Descriptions File**: Stores comprehensive metadata for each game, including descriptions, system requirements, release details, and ratings.
2. **Player Reviews File**: Contains detailed user review data, capturing the review text, playtime, helpfulness, and more.
3. **Genre Ranking File**: Lists each game’s rank by sales, revenue, or reviews within its respective genre.

### Data Usage:
This project provides a robust dataset that can be used for further analysis of game performance, user sentiment, and trends in various game genres based on sales, reviews, and player engagement.
