import monophony.backend.playlists
from monophony.frontend.widgets.group_row import MonophonyGroupRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, GObject, Gtk


class MonophonyLibraryPage(Gtk.Box):
	def __init__(self, player: object):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)

		self.player = player
		self.playlist_widgets = []
		self.set_vexpand(True)

		self.box_meta = Adw.PreferencesPage.new()
		self.append(self.box_meta)

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('io.gitlab.zehkira.Monophony')
		self.pge_status.set_title(_('Your Library is Empty'))
		self.pge_status.set_description(_('Find songs to play using the search bar above'))
		self.pge_status.bind_property(
			'visible',
			self.box_meta,
			'visible',
			GObject.BindingFlags.SYNC_CREATE
			| GObject.BindingFlags.BIDIRECTIONAL
			| GObject.BindingFlags.INVERT_BOOLEAN
		)
		self.append(self.pge_status)

		self.btn_play = Gtk.Button.new_with_label(_('Play All'))
		self.btn_play.connect('clicked', self._on_play_all)
		self.box_playlists = Adw.PreferencesGroup()
		self.box_playlists.set_vexpand(True)
		self.box_playlists.set_title(_('Your Playlists'))
		self.box_playlists.set_header_suffix(self.btn_play)
		self.box_meta.add(self.box_playlists)

		GLib.timeout_add(100, self.update)

	def _on_play_all(self, _b):
		playlists = monophony.backend.playlists.read_playlists()
		all_songs = []
		for title, content in playlists.items():
			all_songs.extend(content)

		GLib.Thread.new(None, self.player.play_queue, all_songs, 0)

	def update(self) -> True:
		new_playlists = monophony.backend.playlists.read_playlists()

		remaining_widgets = []
		for widget in self.playlist_widgets:
			if widget.is_ancestor(self.box_meta):
				remaining_widgets.append(widget)
		self.playlist_widgets = remaining_widgets

		for title in new_playlists.keys():
			for widget in self.playlist_widgets:
				if widget.get_title() == GLib.markup_escape_text(title, -1):
					break
			else: # nobreak
				new_widget = MonophonyGroupRow(
					{'title': title, 'contents': new_playlists[title]},
					self.player,
					True
				)
				self.playlist_widgets.append(new_widget)
				self.box_playlists.add(new_widget)

		self.box_meta.set_visible(len(self.playlist_widgets) > 0)

		return True
