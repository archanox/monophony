import json, os

import ytmusicapi


# playlists = {
#	'my playlist': [
#		{'id': 'ASvGDFQwe', 'title': 'Cool song'}
#	]
# }


### --- PLAYLIST FUNCTIONS --- ###


def add_playlist(name: str, songs: dict = None):
	new_lists = read_playlists()
	name = get_unique_name(name)
	new_lists[name] = songs if songs else []
	new_lists[name] = list(dict.fromkeys(new_lists[name])) # remove duplicates
	write_playlists(new_lists)


def rename_playlist(name: str, new_name: str) -> bool:
	new_lists = read_playlists()
	if new_name not in new_lists:
		new_lists[new_name] = new_lists.pop(name)
		write_playlists(new_lists)
		return True

	return False


def import_playlist(name: str, data: str) -> bool:
	new_lists = read_playlists()
	playlist = []

	yt = ytmusicapi.YTMusic()
	playlist_id = data.split('list=')[1].split('&')[0]
	songs = yt.get_playlist(playlist_id, limit = None)['tracks']

	for song in songs:
		if not song['videoId']:
			continue

		parsed_song = {
			'title': song['title'],
			'author': song['artists'][0]['name'],
			'length': song['duration'] if 'duration' in song else '',
			'id': song['videoId'],
		}
		if parsed_song not in playlist:
			playlist.append(parsed_song)

	name = get_unique_name(name)
	new_lists[name] = playlist
	write_playlists(new_lists)
	return True


def remove_playlist(name: str):
	new_lists = read_playlists()
	new_lists.pop(name)
	write_playlists(new_lists)


### --- SONG FUNCTIONS --- ###


def is_song_in_any_playlist(id_: str) -> bool:
	for playlist in read_playlists().values():
		for song in playlist:
			if song['id'] == id_:
				return True

	return False


def add_song(song: dict, playlist: str):
	new_lists = read_playlists()
	if song not in new_lists[playlist]:
		new_lists[playlist].append(song)
	write_playlists(new_lists)


def rename_song(index: int, playlist: str, new_name: str):
	new_lists = read_playlists()
	new_lists[playlist][index]['title'] = new_name
	write_playlists(new_lists)


def swap_songs(p_name: str, i: int, j: int):
	lists = read_playlists()
	i = 0 if i >= len(lists[p_name]) else i
	j = 0 if j >= len(lists[p_name]) else j
	lists[p_name][i], lists[p_name][j] = lists[p_name][j], lists[p_name][i]
	write_playlists(lists)


def move_song(p_name: str, from_i: int, to_i: int):
	lists = read_playlists()

	to_song = lists[p_name][to_i]
	from_song = lists[p_name].pop(from_i)
	lists[p_name].insert(lists[p_name].index(to_song), from_song)

	write_playlists(lists)


def remove_song(id_: str, playlist: str):
	new_lists = read_playlists()
	new_lists[playlist] = [s for s in new_lists[playlist] if s['id'] != id_]
	write_playlists(new_lists)


### --- UTILITY FUNCTIONS --- ###


def get_unique_name(base: str) -> str:
	lists = read_playlists()
	name = base

	if name in lists:
		i = 1
		while f'{name} ({str(i)})' in lists:
			i += 1

		name = f'{name} ({str(i)})'

	return name


def write_playlists(playlists: dict):
	dir_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony'
	lists_path = dir_path  + '/playlists.json'

	all_songs = []
	for songs in playlists.values():
		all_songs.extend(songs)

	try:
		with open(str(lists_path), 'w') as lists_file:
			json.dump(playlists, lists_file)
	except FileNotFoundError:
		os.makedirs(str(dir_path))
		write_playlists(playlists)


def read_playlists() -> dict:
	lists_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony/playlists.json'

	try:
		with open(lists_path, 'r') as lists_file:
			return json.load(lists_file)
	except OSError:
		return {}
