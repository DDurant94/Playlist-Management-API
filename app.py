from flask import Flask,jsonify,request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields,validate, ValidationError
from helpers import binary_search,PlaylistManager, merge_sort,merge_sort_playlist


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://root:sOaWj8"?G-1Aubxmxu<T@localhost/playlist_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

#<------------------------------------SQL Tables-------------------------------------->

class Song(db.Model):
  __tablename__ = "Songs"
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255),nullable=False)
  artist = db.Column(db.String(255),nullable=False)
  duration = db.Column(db.Float,nullable=False)
  genre_id = db.Column(db.Integer,db.ForeignKey("Genres.id"))
  genre = db.relationship("Genre",back_populates="songs",uselist=False)
    
class Genre(db.Model):
  __tablename__ = "Genres"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255),nullable=False)
  songs = db.relationship("Song",back_populates="genre")
  
class Playlist(db.Model):
  __tablename__ = "Playlists"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255),nullable=False)
  songs = db.relationship('PlaylistItems',back_populates='playlist')
  
class PlaylistItems(db.Model):
  __tablename__ = "PlaylistItems"
  id = db.Column(db.Integer, primary_key=True)
  playlist_id = db.Column(db.Integer, db.ForeignKey('Playlists.id'),nullable=False)
  song_id = db.Column(db.Integer,db.ForeignKey('Songs.id'),nullable=False)
  playlist = db.relationship('Playlist', back_populates='songs')
  song = db.relationship('Song')

Playlist.songs = db.relationship('PlaylistItems', back_populates='playlist')
#<--------------------------------Schema Tables--------------------------------------->

class SongSchema(ma.Schema):
  title = fields.String(required=True,validate=validate.Length(min=1))
  artist = fields.String(required=True,validate=validate.Length(min=1))
  duration = fields.Float(required=True,validate=validate.Range(min=0))
  genre_id = fields.Integer(required=True)
  
  class Meta:
    fields = ('title','artist','duration','genre_id','id')
    
song_schema = SongSchema()
songs_schema = SongSchema(many=True)

class GenreSchema(ma.Schema):
  name= fields.String(required=True,validate=validate.Length(min=1))
  
  class Meta:
    fields = ('name', 'id')
    
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

class PlaylistItemsSchema(ma.Schema):
  playlist_id = fields.Integer(required=True)
  song_id = fields.Integer(required=True)
  
class PlaylistSchema(ma.Schema):
  name = fields.String(required=True,validate=validate.Length(min=1))
  songs = fields.List(fields.Nested(PlaylistItemsSchema),required=True)
  
  class Meta:
    fields=('name','songs','id')
    
playlist_schema = PlaylistSchema()
playlists_schema = PlaylistSchema(many=True) 

with app.app_context():
  db.create_all()
#<--------------------------------Home Page------------------------------------------->

@app.route('/')
def home():
    return 'Welcome to Playlist Manager!'
#<--------------------------------End Routes------------------------------------------>

#<--------------------------------Song End Routes------------------------------------->
@app.route("/songs",methods=['GET'])
def get_all_songs():
  playlist_manager = PlaylistManager()
  sorted_songs = songs()
  [playlist_manager.add_song(song_data.id,song_data.title,song_data.artist,song_data.duration,song_data.genre.name) for song_data in sorted_songs]
  return playlist_manager.traversal()

@app.route("/songs",methods=["POST"])
def add_song():
  try:
    song_data = song_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  new_song = Song(title=song_data['title'],artist=song_data['artist'],duration=song_data['duration'],genre_id=song_data['genre_id'])
  db.session.add(new_song)
  db.session.commit()
  return jsonify({"message": f"{song_data['title']} has been successfully added!"}), 201

@app.route("/songs/<int:id>",methods=["PUT"])
def update_song(id):
  song = Song.query.get_or_404(id)
  try:
    song_data = song_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  song.title=song_data["title"]
  song.artist=song_data["artist"]
  song.duration=song_data["duration"]
  song.genre_id=song_data["genre_id"]
  db.session.commit()
  return jsonify({"message": f"{song_data['title']} has been successfully updated!"}), 201
  
@app.route("/songs/<string:title>",methods=["DELETE"])
def delete_song(title):
  song = Song.query.filter_by(title=title).first()
  if song:
    db.session.delete(song)
    db.session.commit()
    return jsonify({"message": "Song has been successfully Deleted!"}), 200
  return jsonify({"message": f"{title} not found!"}), 400

@app.route("/song-search/<string:title>")
def get_song_by_title(title):
  sorted_songs = songs()
  results = binary_search(sorted_songs,title)
  if results != -1:
    return results
  return jsonify({"message": f"{title} not found!"}), 400

def songs():
  songs_data = Song.query.all()
  merge_sort(songs_data)
  return songs_data
#<--------------------------------Genre End Routes------------------------------------>

@app.route("/genres",methods=["GET"])
def get_genres():
  genres = Genre.query.all()
  return genres_schema.jsonify(genres)

@app.route("/genres",methods=["POST"])
def add_genre():
  try:
    genre_data=genre_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages),400
  new_genre = Genre(name=genre_data['name'])
  db.session.add(new_genre)
  db.session.commit()
  return jsonify({"message": f"{genre_data['name']} has been successfully added!"}), 201

@app.route("/genres/<int:id>",methods=["PUT"])
def update_genre(id):
  genre = Genre.query.get_or_404(id)
  try:
    genre_data = genre_schema.load(request.json)
  except ValidationError as err:
    return jsonify(err.messages), 400
  genre.name = genre_data['name']
  db.session.commit()
  return jsonify({"message": f"{genre_data['name']} has been successfully updated!"}), 200

@app.route("/genres/<int:id>",methods=["DELETE"])
def delete_genre(id):
  genre = Genre.query.get_or_404(id)
  db.session.delete(genre)
  db.session.commit()
  return jsonify({"message": "Genre has been successfully Deleted!"}), 200

#<--------------------------------Playlist End Routes--------------------------------->
@app.route("/playlist",methods=["GET"])
def get_all_playlist():
  playlists = Playlist.query.all()
  return playlists_schema.jsonify(playlists)

@app.route("/playlist/<string:name>",methods=["GET"])
def get_playlist_by_name(name):
  playlist_manager = PlaylistManager()
  playlists_data = playlists()
  for playlist in playlists_data:
    if name in playlist['name']:
      for song in playlist['songs']:
        playlist_manager.add_song(song['title'],song['artist'],song['duration'],song['genre'])
    return playlist_manager.traversal()
  return jsonify({"message": "Playlist not Found!"}), 400
  
@app.route("/playlist-sorted/<string:name>/<string:sort_by>",methods=["GET"])
def sort_playlist(name,sort_by):
  sort = sort_by
  playlist_manager = PlaylistManager()
  playlists_data = playlists()
  for playlist in playlists_data:
    if name in playlist['name']:
      merge_sort_playlist(playlist['songs'],sort)
      for song in playlist['songs']:
        playlist_manager.add_song(song['id'],song['title'],song['artist'],song['duration'],song['genre'])
      return playlist_manager.traversal()
    return jsonify({"message": "Playlist not Found!"}), 400

@app.route("/create-playlist",methods=["POST"])
def create_playlist():
  data = request.get_json()
  name = data['name']
  song_ids = data['songs']
  new_playlist = Playlist(name=name)
  db.session.add(new_playlist)
  db.session.commit()
  for song in song_ids:
    song_id=song['song_id']
    new_playlist_item= PlaylistItems(playlist_id=new_playlist.id,song_id=song_id)
    db.session.add(new_playlist_item)
  db.session.commit()
  return jsonify({"message": f"Playlist '{name}' added successfully"}),201

@app.route('/add-song/<int:id>', methods=['POST'])
def add_songs(id):
    data = request.get_json()
    playlist = Playlist.query.get_or_404(id)   
    for song_id in data['songs']:
      Song.query.get_or_404(song_id['song_id'])
      song = PlaylistItems(playlist_id=playlist.id, song_id=song_id['song_id'])
      db.session.add(song)
    db.session.commit()
    return jsonify({"message": "Songs added successfully"})
  
@app.route('/remove-song/<int:id>', methods=['DELETE'])
def remove_songs(id):
    data = request.get_json()
    playlist = Playlist.query.get_or_404(id)    
    for song_id in data['songs']:
        PlaylistItems.query.filter_by(playlist_id=playlist.id, song_id=song_id['song_id']).delete()
    db.session.commit()
    return jsonify({"message": "Songs removed successfully"})
  
def playlists():
  playlists_data = Playlist.query.all()
  playlists = [{'id':playlist.id,'name': playlist.name, 'songs': [{'id':song.song.id,'title':song.song.title,'artist':song.song.artist,'duration':song.song.duration,'genre':song.song.genre.name}for song in playlist.songs]} for playlist in playlists_data]
  return playlists
    
#<------------------------------------------------------------------------------------>

if __name__ == '__main__':
  app.run(debug=True)