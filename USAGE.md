### List of methods

#### Methods for advanced search
- `search_movies(options, page=1, sort=MovieSorts.BY_RATING_COUNT)`
- `search_creators(options, page=1, sort=CreatorSorts.BY_FAN_COUNT)`

#### Methods for text search
- `text_search(search, page=1)`
- `text_search_movies(search, page=1)`
- `text_search_creators(search, page=1)`
- `text_search_series(search, page=1)`
- `text_search_users(search, page=1)`

#### Methods for searching stuff via CSFD.cz's autocomplete API
- `search_tags(search)`
- `search_actors(search)`
- `search_directors(search)`
- `search_composers(search)`
- `search_screenwriters(search)`
- `search_authors(search)`
- `search_cinematographers(search)`
- `search_producers(search)`
- `search_editors(search)`
- `search_sound_engineers(search)`
- `search_scenographers(search)`
- `search_mask_designers(search)`
- `search_costume_designers(search)`

#### Methods for getting News information
- `news(nid)`
- `news_url(nid)`
- `news_title(nid)`
- `news_text(nid)`
- `news_date(nid)`
- `news_author_id(nid)`
- `news_author_name(nid)`
- `news_most_read_news(nid)`
- `news_most_latest_news(nid)`
- `news_related_news(nid)`
- `news_image(nid)`
- `news_prev_news_id(nid)`
- `news_next_news_id(nid)`

#### Methods for getting News list information
- `news_list(page=1)`
- `news_list_url(page=1)`
- `news_list_main_news()`
- `news_list_news(page=1)`
- `news_list_most_read_news()`
- `news_list_most_latest_news()`
- `news_list_has_prev_page(page=1)`
- `news_list_has_next_page(page=1)`

#### Methods for getting Movie information
- `movie(mid)`
- `movie_url(mid)`
- `movie_type(mid)`
- `movie_title(mid)`
- `movie_year(mid)`
- `movie_duration(mid)`
- `movie_genres(mid)`
- `movie_origins(mid)`
- `movie_rating(mid)`
- `movie_ranks(mid)`
- `movie_other_names(mid)`
- `movie_creators(mid)`
- `movie_vods(mid)`
- `movie_tags(mid)`
- `movie_reviews_count(mid)`
- `movie_reviews(mid)`
- `movie_gallery_count(mid)`
- `movie_gallery(mid)`
- `movie_trivia_count(mid)`
- `movie_trivia(mid)`
- `movie_premieres(mid)`
- `movie_plot(mid)`
- `movie_cover(mid)`

#### Methods for getting Creator information
- `creator(cid, sort=CreatorFilmographySorts.BY_NEWEST)`
- `creator_url(cid)`
- `creator_type(cid)`
- `creator_name(cid)`
- `creator_age(cid)`
- `creator_birth_date(cid)`
- `creator_birth_place(cid)`
- `creator_bio(cid)`
- `creator_trivia_count(cid)`
- `creator_trivia(cid)`
- `creator_ranks(cid)`
- `creator_gallery_count(cid)`
- `creator_gallery(cid)`
- `creator_filmography(cid, sort=CreatorFilmographySorts.BY_NEWEST)`
- `creator_image(cid)`

#### Methods for getting User information
- `user(uid)`
- `user_url(uid)`
- `user_name(uid)`
- `user_real_name(uid)`
- `user_origin(uid)`
- `user_about(uid)`
- `user_registered(uid)`
- `user_last_login(uid)`
- `user_points(uid)`
- `user_awards(uid)`
- `user_most_watched_genres(uid)`
- `user_most_watched_types(uid)`
- `user_most_watched_origins(uid)`
- `user_reviews_count(uid)`
- `user_last_reviews(uid)`
- `user_ratings_count(uid)`
- `user_last_ratings(uid)`
- `user_is_currently_online(uid)`
- `user_image(uid)`

#### Methods for getting other User information
- `user_ratings(uid, mtype=None, origin=None, genre=None, sort=UserRatingsSorts.BY_NEWLY_ADDED, page=1)`

#### Methods for getting Most Favorite Users information
- `favorite_users()`
- `favorite_users_most_favorite_users()`
- `favorite_users_by_regions()`
- `favorite_users_by_country()`

#### Methods for getting Most Active Users information
- `active_users(origin=None, sort=ActiveUsersSorts.ALL_TIME)`
- `active_users_by_reviews(origin=None, sort=ActiveUsersSorts.ALL_TIME)`
- `active_users_by_diaries(origin=None, sort=ActiveUsersSorts.ALL_TIME)`
- `active_users_by_content(origin=None, sort=ActiveUsersSorts.ALL_TIME)`
- `active_users_by_trivia(origin=None, sort=ActiveUsersSorts.ALL_TIME)`
- `active_users_by_biography(origin=None, sort=ActiveUsersSorts.ALL_TIME)`

#### Methods for getting DVDs information
- `dvds_monthly_by_release_date(year=None, page=1, month=Months.JANUARY)`
- `dvds_monthly_by_rating(year=None, page=1, month=Months.JANUARY)`
- `dvds_yearly_by_release_date(year=None)`
- `dvds_yearly_by_rating(year=None)`

#### Methods for getting Blu-rays information
- `blurays_monthly_by_release_date(year=None, page=1, month=Months.JANUARY)`
- `blurays_monthly_by_rating(year=None, page=1, month=Months.JANUARY)`
- `blurays_yearly_by_release_date(year=None)`
- `blurays_yearly_by_rating(year=None)`
