from sys import argv
from youtube_dl import YoutubeDL
from mutagen.easyid3 import EasyID3
from requests import get as http_get
from slugify import slugify
from mimetypes import guess_extension
from tqdm import tqdm

import os

ytdl = YoutubeDL()

def simple_info(playlist_link):
    result = {}
    info = ytdl.extract_info(playlist_link, download=False)

    if info['_type'] != 'playlist':
        print("Given URL is not a playlist")
        exit(1)
    
    result['playlist_title'] = info['title']
    result['entries'] = []
    res_entries = result['entries']

    for entry in info['entries']:
        res_entries.append({
            'title': entry['title'],
            'uploader': entry['uploader'],
            'formats': { i['format_id']: (i['abr'], i['url']) for i in entry['formats'] if 'abr' in i },
        })
    
    return result

def get_song_info(song, album_author):
    print(f"Video title: {song['title']}\nVideo uploader: {song['uploader']}")

    title =  input(f'mp3 title ({song["title"]}): ')
    if title.strip() == '': title = song['title']

    author = input(f'mp3 song author ({album_author}): ')
    if author.strip() == '': author = album_author

    print("Format ID | Average bitrate")
    for format_id in song['formats']:
        print(f"{format_id:>9} | {song['formats'][format_id][0]}")

    _format = ''
    default_format = sorted(song['formats'], key=lambda format_id: int(song['formats'][format_id][0]))[-1]
    while not (_format in song['formats']):
        _format = input(f'choose format id ({default_format}): ')
        if _format.strip() == '': _format = default_format

    return { 'title': title, 'author': author, 'url': song['formats'][_format][1]}

def get_user_choices(info):
    album_title  = input('mp3 album title: ')
    album_author = input('mp3 album author: ')

    if album_title.strip() == '' or album_author.strip() == '':
        print('Please specify album title and album author')
        exit(1)

    song_choices = [get_song_info(i, album_author) for i in info['entries']]

    return { 'author': album_author, 'title': album_title, 'songs': song_choices }

def download_files(choices):
    dir_name = slugify(choices['title'])
    os.mkdir(dir_name)

    for song in choices['songs']:
        response = http_get(song['url'], allow_redirects=True, stream=True)

        extension = guess_extension(response.headers['content-type'])
        print(f"Extension: {extension}")
        if extension == None:
            print("Cannot guess filename extension")
            continue

        filename_no_ext  = slugify(song['title'])
        print(f"Filename: {filename_no_ext}")
        filename = filename_no_ext + extension
        print(f"Filename: {filename}")
        
        file_info = { 'ext': extension, 'fname': filename, "fname_no_ext": filename_no_ext }
        song['file_info'] = file_info

        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=filename)
        with open(os.path.join(dir_name, filename), 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

def convert_files(choices):
    dir_name = slugify(choices['title'])

    for song in choices['songs']:
        filename = os.path.join(dir_name, song['file_info']['fname'])
        filename_no_ext = os.path.join(dir_name, song['file_info']['fname_no_ext'])

        os.system(f"ffmpeg -i {filename} {filename_no_ext}.mp3")
        os.remove(filename)

        song['mp3_filename'] = filename_no_ext + ".mp3"

def add_metadata(choices):
    for index, song in enumerate(choices['songs']):
        tag = EasyID3(song['mp3_filename'])

        tag['genre'] = 'mygenre'
        tag['artist'] = song['author']
        tag['title'] = song['title']
        tag['date'] = '2020'
        tag['album'] = choices['title']
        tag['albumartist'] = choices['author']
        tag['tracknumber'] = f'{index + 1}'
        tag['discnumber'] = '1'

        tag.save(v2_version=3)

def main():
    if len(argv) < 2:
        print("Give playlist link as argument")
        exit(1)

    playlist = argv[1]

    info = simple_info(playlist)
    choices = get_user_choices(info)

    download_files(choices)
    convert_files(choices)
    add_metadata(choices)



if __name__ == "__main__":
    main()