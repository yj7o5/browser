import os
import time
import datetime as dt
import collections as colls

CacheEntry = colls.namedtuple("CacheEntry", "key file_path expires_at")

CACHE_DIR = "./.cache"

"""
  This cache module holds a collection of cached page entries that are hold upto
  the given TTL after which they're expired and removed from the collection
"""
class Cache:
  def __init__(self):
    # hold caced pages entry references
    self._entries = {}

  def set(self, url, body, headers, ttl):
    # assume we have only 1 level ex: http://[localhost]:[port]/document.html
    # because we could have N level deep paths such as http://[localhost]:[port]/path/to/document.html
    # and thus we could run into collision and override previously made entries
    name = url.split("/")[-1]

    # determine file path and expire datetime based on specified TTL
    file_path = os.path.join(CACHE_DIR, name)
    expires_at = dt.datetime.now() + dt.timedelta(seconds=ttl)

    entry = CacheEntry(url, file_path, expires_at)

    if not os.path.isdir(CACHE_DIR):
      os.mkdir(CACHE_DIR)

    with open(file_path, mode="w") as file:
      # write HTTP headers onto disk
      self.__write_headers(file, headers)

      # write HTTP body onto disk
      file.write(body)

    self._entries[url] = entry

  def get(self, url):
    if not url in self._entries:
      return None, None

    entry = self._entries[url]

    if entry.expires_at < dt.datetime.now():
      os.remove(entry.file_path)
      del self._entries[url]
      return None, None

    with open(entry.file_path, mode="r") as file:
      headers = self.__read_headers(file)
      body = file.read()

    return headers, body

  def remove(self, url):
    if not url in self._entries:
      return False

    entry = self._entries[url]

    os.remove(entry.file_path)
    del self._entries[url]

    return True

  def __write_headers(self, file, headers):
    for k in headers:
      file.write(k + ": " + headers[k] + "\n")
    file.write("\n\n")

  def __read_headers(self, file):
    headers = {}
    line = file.readline()
    while line != "":
      k, v = line.split(":")
      headers[k.strip()] = v.strip()
      line = file.readline().strip()

    # skip extra newline that separates the headers and body
    file.readline()

    return headers
