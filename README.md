# album_maker

Skrypt w python, który pobiera piosenki z playlisty youtube. Użytkownik interaktywnie
wybiera:

- tytuł albumu
- autora albumu
- tytuł piosenek
- autorów piosenek
- bitrate każdego utworu

skrypt pobiera audio w wybranym formacie, konwertuje do .mp3 i ustawia metadane mp3
pobrane od użytkownika.

# Wymagania

- ffmpeg w PATH systemowym

### Wymagania pip

- youtube-dl
- mutagen
- requests
- slugify
- mimetypes
- tqdm

# Użycie

```
python ./album_maker.py <link do playlisty youtube>
```
