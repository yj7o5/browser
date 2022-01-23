PORT := 8000

http: 
	python3 ./browser.py http://example.org/index.html

https:
	python3 ./browser.py https://example.org/index.html

localhost: default_server
	python3 ./browser.py http://localhost:8000/
	kill $$(lsof -ti :$(PORT))

view_source:
	python3 ./browser.py view-source:https://example.org/

entities: default_server
	python3 ./browser.py http://localhost:$(PORT)/html_entities.html
	kill $$(lsof -ti :$(PORT))

file:
	python3 ./browser.py file:///Users/yawarjamal/projects/browser/demo_file.txt

file_default:
	python3 ./browser.py file://

data:
	python3 ./browser.py "data:text/html,<h1>Hello, World</h1>"

redirect: default_server
	python3 ./browser.py http://browser.engineering/redirect

cached_file: cache_server
	python3 ./browser.py http://localhost:8000/with_cache.html
	# make sure "cached" folder does contain the cached file
	[[ -f ./.cache/with_cache.html ]] || (printf "expected \"with_cache.html\" to be cached, found none" >&2; exit 1)
	python3 ./browser.py http://localhost:8000/with_cache.html
	echo "Should have retrieved \"with_cache.html\" document instantenously from cache" $(PORT) 
	sleep 15
	python3 ./browser.py http://localhost:8000/with_cache.html
	echo "Should have taken > 10 seconds to load because of cache expiry"
	kill $$(lsof -ti :$(PORT))

non_cached_file: cache_server
	python3 ./browser.py http://localhost:8000/without_cache.html
	sleep 5
	python3 ./browser.py http://localhost:8000/without_cache.html
	echo "Result should have come with delay due to no-cache" $(PORT)
	kill $$(lsof -ti :$(PORT))
	
cache_server:
	python3 ./cache_server.py $(PORT) &
	echo "Started cache server listening on port " $(PORT) &
	sleep 5

default_server:
	python3 -m http.server 8000 &
	sleep 1

all: http https localhost view_source redirect entities file file_default data
