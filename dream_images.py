import random
import flickr_api
from flickr_api import Photo, Walker

FLICKR_USER_ID = '126377022@N07'
API_KEY = "9fc869c68e7ddb1d6cb48f64a8044a78"
API_SECRET = "f0b61a5aec4da80b"

flickr_api.set_keys(API_KEY, API_SECRET)


def get_photo(keyword, surreal=False):
    query_string = "bookcentury:1700 "+keyword
    if surreal:
        query_string += " surreal"
    w = Walker(Photo.search, text=query_string, sort="relevance", per_page=200)
    num_results = len(w)
    if num_results == 0:
        return False
    photo_num = random.randrange(min(num_results, 10))
    photo = w[photo_num:].next()
    return photo.getPhotoFile()
