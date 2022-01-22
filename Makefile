http: 
	python3 ./browser.py http://example.org/index.html

https:
	python3 ./browser.py https://example.org/index.html

localhost: default_server
	python3 ./browser.py http://localhost:8000/
	kill $$(lsof -ti :8000)

view_source:
	python3 ./browser.py view-source:https://example.org/

entities: default_server
	python3 ./browser.py http://localhost:8000/html_entities.html
	kill $$(lsof -ti :8000)

file:
	python3 ./browser.py file:///Users/yawarjamal/projects/browser/demo_file.txt

file_default:
	python3 ./browser.py file://

data:
	python3 ./browser.py "data:text/html,<h1>Hello, World</h1>"

redirect: default_server
	python3 ./browser.py http://browser.engineering/redirect

default_server:
	python3 -m http.server 8000 &
	sleep 1

cached_file: cache_server
	python3 ./browser.py http://localhost:8000/with_cache.html
	# make sure "cached" folder does contain the cached file
	if [[ ! -f ./.cache/with_cache.html ]] \then printf "expected \"with_cache.html\" to stored in cache" >&2; exit 1
	sleep 31
	# after the timeout the cached file should have been removed
	if [[ -f ./.cache/with_cache.html ]] \then printf "expected \"with_cached.html\" not to be stored in cache" >&2; exit 1
	

non_cached_file: cache_server
	python3 ./browser.py http://localhost:8000/without_cache.html
	# after the timeout the cached file should have been removed
	if [[ -f ./.cache/with_cache.html ]] \then printf "expected no \"with_cached.html\" file cached" >&2; exit 1
	
PORT := 8000
cache_server:
	python ./cache_server.py $(PORT)
	echo "Starting cache server on port " $(PORT)
	sleep 5
	

all: http https localhost view_source redirect entities file file_default data
