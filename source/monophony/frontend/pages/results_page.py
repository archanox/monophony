import monophony.backend.yt
from monophony.frontend.widgets.group_row import MonophonyGroupRow
from monophony.frontend.widgets.song_row import MonophonySongRow
from monophony.frontend.widgets.artist_row import MonophonyArtistRow

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, GLib, GObject, Gtk


class MonophonyResultsPage(Gtk.Box):
	def __init__(self, player: object, query: str='', artist: str='', filter_: str=''):
		super().__init__(orientation = Gtk.Orientation.VERTICAL)

		self.pge_status = Adw.StatusPage()
		self.pge_status.set_vexpand(True)
		self.pge_status.set_valign(Gtk.Align.FILL)
		self.pge_status.set_icon_name('system-search-symbolic')
		self.pge_status.set_title(_('No Results'))
		self.pge_status.set_visible(False)
		self.append(self.pge_status)

		self.pge_results = Adw.PreferencesPage.new()
		self.pge_results.set_vexpand(True)
		self.pge_results.set_valign(Gtk.Align.FILL)
		self.pge_results.set_visible(False)
		self.append(self.pge_results)

		spn_loading = Gtk.Spinner.new()
		spn_loading.set_halign(Gtk.Align.CENTER)
		spn_loading.set_valign(Gtk.Align.CENTER)
		spn_loading.set_vexpand(True)
		self.box_loading = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.box_loading.set_margin_bottom(10)
		self.box_loading.append(spn_loading)
		self.box_loading.bind_property(
			'visible',
			spn_loading,
			'spinning',
			GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL
		)
		self.append(self.box_loading)
		self.box_loading.set_visible(True)

		self.set_vexpand(True)
		self.query = query
		self.filter = filter_
		self.artist = artist
		self.results = []
		self.search_lock = GLib.Mutex()
		self.player = player

		GLib.Thread.new(None, self.do_search if self.query else self.do_get_artist)
		GLib.timeout_add(500, self.await_results)

	def do_search(self):
		self.search_lock.lock()
		self.results = monophony.backend.yt.search(self.query, self.filter)
		self.search_lock.unlock()

	def do_get_artist(self):
		self.search_lock.lock()
		results = monophony.backend.yt.get_artist(self.artist)
		if not results:
			self.pge_status.set_visible(True)
			self.box_loading.set_visible(False)
			self.search_lock.unlock()
			return

		self.results = results
		self.search_lock.unlock()

	def await_results(self) -> bool:
		if not self.search_lock.trylock():
			return True

		self.box_loading.set_visible(False)
		self.pge_status.set_visible(len(self.results) == 0)
		if not self.results:
			self.pge_status.set_title(_('No Results'))
		else:
			self.pge_results.set_visible(True)
			box_top = Adw.PreferencesGroup.new()
			box_songs = Adw.PreferencesGroup.new()
			box_videos = Adw.PreferencesGroup.new()
			box_albums = Adw.PreferencesGroup.new()
			box_playlists = Adw.PreferencesGroup.new()
			box_artists = Adw.PreferencesGroup.new()
			box_top.set_title(_('Top Result'))
			box_songs.set_title(_('Songs'))
			box_albums.set_title(_('Albums'))
			box_videos.set_title(_('Videos'))
			box_playlists.set_title(_('Community Playlists'))
			box_artists.set_title(_('Artists'))
			window = self.get_ancestor(Gtk.Window)

			if not self.filter:
				btn_more = Gtk.Button.new_with_label(_('More'))
				btn_more.connect(
					'clicked',
					lambda _b, f: window._on_show_more(self.query, f),
					'songs'
				)
				box_songs.set_header_suffix(btn_more)

				btn_more = Gtk.Button.new_with_label(_('More'))
				btn_more.connect(
					'clicked',
					lambda _b, f: window._on_show_more(self.query, f),
					'albums'
				)
				box_albums.set_header_suffix(btn_more)

				btn_more = Gtk.Button.new_with_label(_('More'))
				btn_more.connect(
					'clicked',
					lambda _b, f: window._on_show_more(self.query, f),
					'playlists'
				)
				box_playlists.set_header_suffix(btn_more)

				btn_more = Gtk.Button.new_with_label(_('More'))
				btn_more.connect(
					'clicked',
					lambda _b, f: window._on_show_more(self.query, f),
					'videos'
				)
				box_videos.set_header_suffix(btn_more)

				btn_more = Gtk.Button.new_with_label(_('More'))
				btn_more.connect(
					'clicked',
					lambda _b, f: window._on_show_more(self.query, f),
					'artists'
				)
				box_artists.set_header_suffix(btn_more)

			non_empty = []
			for item in self.results:
				if item['type'] == 'song':
					if item['top']:
						box_top.add(MonophonySongRow(item, self.player))
						non_empty.append(box_top)
						continue
					box_songs.add(MonophonySongRow(item, self.player))
					if box_songs not in non_empty:
						non_empty.append(box_songs)
				elif item['type'] == 'video':
					if item['top']:
						box_top.add(MonophonySongRow(item, self.player))
						non_empty.append(box_top)
						continue
					box_videos.add(MonophonySongRow(item, self.player))
					if box_videos not in non_empty:
						non_empty.append(box_videos)
				elif item['type'] == 'album':
					if item['top']:
						box_top.add(MonophonyGroupRow(item, self.player))
						non_empty.append(box_top)
						continue
					box_albums.add(MonophonyGroupRow(item, self.player))
					if box_albums not in non_empty:
						non_empty.append(box_albums)
				elif item['type'] == 'playlist':
					if item['top']:
						box_top.add(MonophonyGroupRow(item, self.player))
						non_empty.append(box_top)
						continue
					box_playlists.add(MonophonyGroupRow(item, self.player))
					if box_playlists not in non_empty:
						non_empty.append(box_playlists)
				elif item['type'] == 'artist':
					if item['top']:
						box_top.add(MonophonyArtistRow(item))
						non_empty.append(box_top)
						continue
					box_artists.add(MonophonyArtistRow(item))
					if box_artists not in non_empty:
						non_empty.append(box_artists)
			for box in non_empty:
				self.pge_results.add(box)

		self.search_lock.unlock()
		return False