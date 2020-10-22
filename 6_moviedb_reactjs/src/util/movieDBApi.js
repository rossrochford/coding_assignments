let MOVIEDB_API_KEY = "f3a05026119d09f84c9aaef927a18ac2";

export let MOVIEDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query_string}";
export let MOVIEDB_GET_MOVIE_URL = "https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}";
export let MOVIEDB_POSTER_URL = "https://image.tmdb.org/t/p/original{poster_path}";

MOVIEDB_SEARCH_URL = MOVIEDB_SEARCH_URL.replace("{api_key}", MOVIEDB_API_KEY);
MOVIEDB_GET_MOVIE_URL = MOVIEDB_GET_MOVIE_URL.replace("{api_key}", MOVIEDB_API_KEY);

/*
 
/3//search/movie/ keys:

['popularity', 'vote_count', 'video', 'poster_path', 'id', 'adult', 'backdrop_path', 'original_language', 'original_title', 'genre_ids', 'title', 'vote_average', 'overview', 'release_date']

/3/movie/<id> keys:

['adult', 'backdrop_path', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id', 'imdb_id', 'original_language', 'original_title', 'overview', 'popularity', 'poster_path', 'production_companies', 'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'tagline', 'title', 'video', 'vote_average', 'vote_count']

*/