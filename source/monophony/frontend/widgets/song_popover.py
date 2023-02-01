import monophony.backend.cache
import monophony.backend.playlists

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gdk, GLib, Gtk, Pango


class MonophonySongPopover(Gtk.Popover):
	def __init__(self, btn: Gtk.MenuButton, player: object, song: dict, group: dict = None, editable: bool = False):
		super().__init__()

		self.player = player
		self.song = song
		self.group = group

		box_pop = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		box_pop.set_spacing(5)
		if editable:
			box_move = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
			box_move.set_spacing(5)
			btn_up = Gtk.Button.new_from_icon_name('go-up')
			btn_up.set_has_frame(False)
			btn_up.set_hexpand(True)
			btn_up.connect('clicked', self._on_move_clicked, -1)
			box_move.append(btn_up)
			btn_down = Gtk.Button.new_from_icon_name('go-down')
			btn_down.set_has_frame(False)
			btn_down.set_hexpand(True)
			btn_down.connect('clicked', self._on_move_clicked, 1)
			box_move.append(btn_down)
			btn_uncache = Gtk.Button.new_with_label(_('Remove from downloads'))
			btn_uncache.set_has_frame(False)
			btn_cache = Gtk.Button.new_with_label(_('Download to Music folder'))
			btn_cache.set_has_frame(False)
			box_pop.append(box_move)
			if monophony.backend.cache.is_song_cached(song['id']):
				btn_uncache.connect('clicked', self._on_uncache_clicked)
				box_pop.append(btn_uncache)
			elif Player.online:
				btn_cache.connect('clicked', self._on_cache_clicked)
				box_pop.append(btn_cache)
			else:
				btn_song.set_sensitive(False)
		if player.get_current_song() != song:
			btn_queue = Gtk.Button.new_with_label(_('Add to queue'))
			btn_queue.set_has_frame(False)
			btn_queue.connect('clicked', self._on_queue_clicked)
			box_pop.append(btn_queue)
		btn_new = Gtk.Button.new_with_label(_('New playlist...'))
		btn_new.set_has_frame(False)
		btn_new.connect('clicked', self._on_new_clicked)
		box_pop.append(btn_new)
		playlists = monophony.backend.playlists.read_playlists()
		if playlists:
			box_pop.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
		for name, songs in playlists.items():
			box_playlist = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
			box_playlist.set_spacing(5)
			chk_playlist = Gtk.CheckButton.new()
			lbl_playlist = Gtk.Label.new(name)
			lbl_playlist.set_ellipsize(Pango.EllipsizeMode.END)
			lbl_playlist.set_max_width_chars(20)
			chk_playlist.set_active(song['id'] in [s['id'] for s in songs])
			chk_playlist.connect('toggled', self._on_playlist_toggled, name)
			box_playlist.append(chk_playlist)
			box_playlist.append(lbl_playlist)
			box_pop.append(box_playlist)

		self.set_child(box_pop)
		btn.set_popover(self)

	def _on_queue_clicked(self, _b):
		self.popdown()
		if self.song:
			GLib.Thread.new(None, self.player.queue_song, self.song)

	def _on_move_clicked(self, _b, direction: int):
		self.popover.popdown()
		index = self.group['contents'].index(self.song)
		monophony.backend.playlists.swap_songs(
			self.group['name'], index, index + direction
		)

	def _on_uncache_clicked(self, _b):
		self.popdown()
		monophony.backend.cache.uncache_song(self.song['id'])

	def _on_cache_clicked(self, _b):
		self.popdown()
		monophony.backend.cache.cache_song(self.song['id'])

	def _on_new_clicked(self, _b):
		self.popdown()

	def _on_playlist_toggled(self, chk: Gtk.CheckButton, name: str):
		if chk.get_active():
			monophony.backend.playlists.add_song(self.song, name)
		else:
			monophony.backend.playlists.remove_song(self.song['id'], name)
			if self.editable and name == self.group['title']:
				self.popdown()
