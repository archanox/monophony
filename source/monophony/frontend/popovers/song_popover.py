import monophony.backend.cache
import monophony.backend.playlists

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio, Gtk


class MonophonySongPopover(Gtk.PopoverMenu):
	def __init__(self, btn: Gtk.MenuButton, song: dict):
		super().__init__()
		if 'author_id' not in song:
			print(song)

		self.song = song
		window = btn.get_ancestor(Gtk.Window)
		menu = Gio.Menu()

		if monophony.backend.cache.is_song_being_cached(song['id']):
			pass
		elif monophony.backend.cache.is_song_cached(song['id']):
			menu.append(_('Remove From Downloads'), 'uncache-song')
			window.install_action(
				'uncache-song',
				None,
				lambda w, *_: w._on_uncache_song(song)
			)
		else:
			menu.append(_('Download'), 'cache-song')
			window.install_action(
				'cache-song',
				None,
				lambda w, *_: w._on_cache_song(song)
			)

		menu.append(_('Add to...'), 'add-song-to')
		window.install_action(
			'add-song-to',
			None,
			lambda w, *_: w._on_add_clicked(song)
		)
		menu.append(_('View Artist'), 'show-artist')
		window.install_action(
			'show-artist',
			None,
			lambda w, *_: w._on_show_artist(song['author_id'])
		)
		self.set_menu_model(menu)
		btn.set_popover(self)
