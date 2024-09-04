from flask import jsonify
# doubly linked list
class DS_Song:
  def __init__(self,id,title,artist,duration,genre):
    self.id = id
    self.title = title
    self.artist = artist
    self.duration = duration
    self.genre = genre

class Node:
  def __init__(self,song):
    self.song = song
    self.next = None
    self.prev = None
      
class PlaylistManager:
  def __init__(self):
    self.head = None
    self.tail = None
    
  def add_song(self,id,title,artist,duration,genre):
    new_song = DS_Song(id,title,artist,duration,genre)
    new_node = Node(new_song)
    if not self.head:
      self.head = new_node
      self.tail = new_node
      
    else:
      self.tail.next = new_node
      new_node.prev = self.tail
      self.tail = new_node
  
  def insertion(self,position,id,title,artist,duration,genre):
    new_song = DS_Song(id,title,artist,duration,genre)
    new_node = Node(new_song)
    if not self.head:
      self.head = new_node
      self.tail = new_node
      return 
    if position == 0:
      new_node.next = self.head
      self.head.prev = new_node
      self.head = new_node
    else:
      current = self.head
      current_position = 0
      while current != None and current_position < position:
        current = current.next
        current_position +=1
      
      if current is None:
        self.tail.next = new_node
        new_node.prev = self.tail
        self.tail = new_node
      else:
        current.prev.next = new_node
        new_node.next = current
        new_node.prev = current.prev
        current.prev = new_node
    
  def deletion(self,title):
    current = self.head
    while current:
      if current.song.title == title:
        if current == self.head:
          self.head = current.next
        if current == self.tail:
          self.tail = current.prev
        if current.prev:
          current.prev.next = current.next
        if current.next:
          current.next.prev = current.prev
        return True
      current = current.next
    return False
    
  def traversal(self):
    if not self.head:
      return jsonify({"message": "No songs in playlist"}),400
    songs = []
    current = self.head
    while current:
      song = current.song
      songs.append({"id":song.id,"title": song.title, "artist": song.artist, "duration": song.duration, "genre": song.genre})
      current = current.next
    return jsonify(songs) 

# search for song title, artist or, genre
def binary_search(arr,title):
  low = 0
  high = len(arr) - 1 #getting last index
  while low <= high:
    mid = (low + high)//2
    print(arr[mid]['title'])
    if arr[mid]['title'] == title:
      return arr[mid]
    elif arr[mid]['title'] < title:
      low = mid + 1
    else:
      high = mid -1
  return -1

def merge_sort(arr):
  if len(arr) > 1:
    mid = len(arr)// 2 
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    merge_sort(left_half)
    merge_sort(right_half)
    
    i = j = k = 0
    
    while i < len(left_half) and j < len(right_half):
      if left_half[i].title < right_half[j].title:
        arr[k] = left_half[i]
        i += 1
      else:
        arr[k] = right_half[j]
        j += 1
      k += 1
    
    while i < len(left_half):
      arr[k] = left_half[i]
      i += 1
      k += 1
    
    while j < len(right_half):
      arr[k] = right_half[j]
      j+=1
      k += 1
      
      
def merge_sort_playlist(arr,sort_by):
  if len(arr) > 1:
    mid = len(arr)// 2 
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    merge_sort_playlist(left_half,sort_by)
    merge_sort_playlist(right_half,sort_by)
    
    i = j = k = 0
    
    while i < len(left_half) and j < len(right_half):
      if left_half[i][sort_by] < right_half[j][sort_by]:
        arr[k] = left_half[i]
        i += 1
      else:
        arr[k] = right_half[j]
        j += 1
      k += 1
    
    while i < len(left_half):
      arr[k] = left_half[i]
      i += 1
      k += 1
    
    while j < len(right_half):
      arr[k] = right_half[j]
      j+=1
      k += 1