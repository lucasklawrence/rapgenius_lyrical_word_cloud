# web imports
import requests
from bs4 import BeautifulSoup

# regular expression and string to find lyrics / parts of lyrics
import re
import string

# datetime to print time for each album
import datetime as datetime


class Stats:
    def __init__(self, word_count):
        self.word_count = word_count
        self.starting_letter_count = self.init_starting_letter_count()

        self.remove = {"and", "im", "or",
                          # pronouns
                          "i", "me", "my", "mine", "myself",
                          "you", "your", "yours", "yourself",
                          "he", "him", "his", "himself",
                          "she", "her", "hers", "herself",
                          "it", "its", "itself",
                          "we", "us", "our", "ours", "ourselves",
                          "they", "them", "their", "theirs"
        
                          # articles
                          "a", "the", "an",
                          # prepositions
                          "at", "in", "by", "for", "on", "to", "from", "of", "with"}

        self.word_count_minus = self.init_word_count_minus()

    def get_word_count(self):
        return self.word_count

    def set_word_count(self, word_count):
        self.word_count = word_count

    def init_starting_letter_count(self):
        starting_letter_count = {}
        for key in self.word_count:
            letter = key[0]
            if letter not in starting_letter_count:
                starting_letter_count[letter] = 1
            else:
                prev_count = starting_letter_count[letter]
                starting_letter_count[letter] = prev_count + 1

        return starting_letter_count

    def get_starting_letter_count(self):
        return self.starting_letter_count

    def get_word_count_minus(self):
        return self.word_count_minus

    def init_word_count_minus(self):
        word_count_minus = {}
        for key in self.word_count:
            if key not in self.remove:
                word_count_minus[key] = self.word_count[key]

        return word_count_minus


class Artist:
    def __init__(self, artist_name, artist_url):
        """
        :param artist_name: Name of music artist
        :param artist_url: Rap genius url of music artist
        """
        self.artist_name = artist_name
        self.artist_url = artist_url

        # initialize albums from artist url
        self.albums = list()
        self.init_albums()

        self.stats = self.init_stats()
        self.wordCloud = None
        # dictionary for word count with parts of speech removed
        self.wordCloudMinusPartsOfSpeech = None

    def get_artist_name(self):
        return self.artist_name

    def set_artist_name(self, artist_name):
        self.artist_name = artist_name

    def get_artist_url(self):
        return self.artist_url

    def set_artist_url(self, artist_url):
        self.artist_url = artist_url

    def get_albums(self):
        return self.albums

    def init_albums(self):
        # Get Albums from Artist
        genius_album_urls = get_artist_albums_from_artist_url(self.get_artist_url())

        # create albums for artist
        for genius_album_url in genius_album_urls:
            init_partition = str.partition(genius_album_url, "/albums/")
            album_name = (str.partition(init_partition[2], "/"))[2]
            album_name = str.replace(album_name, "-", " ")
            genius_album = Album(album_name, genius_album_url)
            self.add_album(genius_album)

    def add_album(self, album):
        self.albums.append(album)

    def get_stats(self):
        return self.stats

    def init_stats(self):
        combined_words = {}

        for album in self.get_albums():
            album_stats = album.get_stats()
            if album_stats is not None:
                album_word_count = album_stats.get_word_count()
                if album_word_count is not None:
                    for key in album_word_count:
                        if key not in combined_words:
                            combined_words[key] = album_word_count[key]
                        else:
                            prev_count = combined_words[key]
                            combined_words[key] = prev_count + album_word_count[key]

        return Stats(combined_words)

    def get_word_count(self):
        return self.wordCount

    def get_word_cloud(self):
        return self.wordCloud

    def set_word_cloud(self, wordcloud):
        self.wordCloud = wordcloud

    def get_word_cloud_minus(self):
        return self.wordCloudMinusPartsOfSpeech

    def set_word_cloud_minus(self, wordcloud):
        self.wordCloudMinusPartsOfSpeech = wordcloud


class Album:
    def __init__(self, album_name, album_url):
        self.album_name = album_name
        self.album_url = album_url

        # initialize songs
        self.songs = list()
        self.init_songs()

        self.stats = self.init_stats()
        self.wordCloud = None

        # dictionary for word count with parts of speech removed
        self.wordCountMinusPartsOfSpeech = {}
        self.wordCloudMinusPartsOfSpeech = None

    def get_album_name(self):
        return self.album_name

    def set_album_name(self, album_name):
        self.album_name = album_name

    def get_album_url(self):
        return self.album_url

    def set_album_url(self, album_url):
        self.album_url = album_url

    def get_songs(self):
        return self.songs

    def init_songs(self):
        # create songs for album
        song_urls = get_song_urls_from_album_url(self.get_album_url())
        print("Scraping lyrics for album: " + self.get_album_name())
        initial_time = datetime.datetime.now()
        for song_url in song_urls:
            song_title = (str.partition(song_url, "genius.com/"))[2]
            current_song = Song(song_title, song_url)
            self.add_song(current_song)
        end_time = datetime.datetime.now()
        elapsed_time = (end_time - initial_time).total_seconds()
        print("Finished in: " + str(elapsed_time) + " seconds")

    def add_song(self, song):
        self.songs.append(song)

    def get_stats(self):
        return self.stats

    def init_stats(self):
        combined_words = {}
        for song in self.get_songs():
            song_stats = song.get_stats()
            if song_stats is not None:
                song_word_count = song_stats.get_word_count()
                if song_word_count is not None:
                    for key in song_word_count:
                        if key not in combined_words:
                            combined_words[key] = song_word_count[key]
                        else:
                            prev_count = combined_words[key]
                            combined_words[key] = prev_count + song_word_count[key]

        return Stats(combined_words)

    def get_word_cloud(self):
        return self.wordCloud

    def set_word_cloud(self, wordcloud):
        self.wordCloud = wordcloud

    def get_word_cloud_minus(self):
        return self.wordCloudMinusPartsOfSpeech

    def set_word_cloud_minus(self, wordcloud):
        self.wordCloudMinusPartsOfSpeech = wordcloud


class Song:
    def __init__(self, song_name, song_url):
        self.song_name = song_name
        self.song_url = song_url
        self.lyrics = self.init_lyrics()
        self.wordCount = self.init_word_count()
        self.stats = self.init_stats()

    def get_song_name(self):
        return self.song_name

    def set_song_name(self, song_name):
        self.song_name = song_name

    def get_song_url(self):
        return self.song_url

    def set_song_url(self, song_url):
        self.song_url = song_url

    def get_lyrics(self):
        return self.lyrics

    def set_lyrics(self, lyrics):
        self.lyrics = lyrics

    def init_lyrics(self):
        html = requests.get(self.get_song_url())
        data = html.text
        soup = BeautifulSoup(data, "html.parser")
        lyrics_html = soup.find("div", {"class": "lyrics"})

        song_lyrics = None
        if lyrics_html is not None:
            song_lyrics = lyrics_html.get_text()

            # remove [Chorus: Artist 1] [Verse: Artist 2], etc
            song_lyrics = remove_items_in_brackets(song_lyrics)
            # removes punctuation
            song_lyrics = song_lyrics.translate(str.maketrans('', '', string.punctuation))

        return song_lyrics

    def get_stats(self):
        return self.stats

    def init_stats(self):
        return Stats(self.get_word_count())

    def get_word_count(self):
        return self.wordCount

    def init_word_count(self):
        word_count = {}
        if self.lyrics is None:
            return

        words = self.lyrics.lower().split()
        for word in words:
            if word not in word_count:
                word_count[word] = 1
            else:
                prev_count = word_count[word]
                word_count[word] = prev_count + 1

        return word_count


# Utilities

def get_artist_albums_from_artist_url(artist_link):
    html = requests.get(artist_link)
    data = html.text
    soup = BeautifulSoup(data, "html.parser")

    album_urls = set()
    for link in soup.find_all('a'):
        possible_link = link.get('href')
        if re.match('https://', possible_link) and re.search('/albums/', possible_link):
            if possible_link.lower() not in album_urls:
                album_urls.add(possible_link.lower())

    return album_urls


def get_song_urls_from_album_url(album_link):
    html = requests.get(album_link)
    data = html.text
    soup = BeautifulSoup(data, "html.parser")

    song_genius_urls = set()
    for link in soup.find_all('a'):
        possible_link = link.get('href')
        # this gets all possible songs from the album
        if possible_link is not None and re.search("-lyrics", possible_link):
            song_genius_url = possible_link.lower()
            if song_genius_url not in song_genius_urls:
                song_genius_urls.add(song_genius_url)

    return song_genius_urls


def get_lyrics_from_song_url(song_link):
    html = requests.get(song_link)
    data = html.text
    soup = BeautifulSoup(data, "html.parser")
    lyrics_html = soup.find("div", {"class": "lyrics"})

    song_lyrics = None
    if lyrics_html is not None:
        song_lyrics = lyrics_html.get_text()

        # remove [Chorus: Artist 1] [Verse: Artist 2], etc
        song_lyrics = remove_items_in_brackets(song_lyrics)
        # removes punctuation
        song_lyrics = song_lyrics.translate(str.maketrans('', '', string.punctuation))
    return song_lyrics


def remove_items_in_brackets(lyrics):
    initial_indices = list()
    end_indices = list()

    # get starting and ending points of brackets in string
    for index in range(len(lyrics)):
        if lyrics[index] == '[':
            initial_indices.append(index)
        if lyrics[index] == ']':
            end_indices.append(index)

    initial_length = len(initial_indices)
    end_length = len(end_indices)
    remove = list()

    # get strings that are in brackets to replace with empty strings
    if initial_length == end_length:
        for index in range(initial_length):
            initial_index = initial_indices[index]
            end_index = end_indices[index]
            remove.append(lyrics[initial_index:end_index + 1])

    # replace strings w/ empty string
    for item in remove:
        lyrics = lyrics.replace(item, "")

    return lyrics

