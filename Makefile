http: 
	python3 ./browser.py http://example.org/index.html

https:
	python3 ./browser.py https://example.org/index.html

localhost: start_server
	python3 ./browser.py http://localhost:8000/
	kill $$(lsof -ti :8000)

view_source:
	python3 ./browser.py view-source:https://example.org/

redirect:
	python3 ./browser.py http://browser.engineering/redirect

entities: start_server
	python3 ./browser.py http://localhost:8000/html_entities.html
	kill $$(lsof -ti :8000)

file:
	python3 ./browser.py file:///Users/yawarjamal/projects/browser/demo_file.txt

file_default:
	python3 ./browser.py file://

data:
	python3 ./browser.py "data:text/html,<h1>Hello, World</h1>"

start_server:
	python3 -m http.server 8000 &
	sleep 1

all: http https localhost view_source redirect entities file file_default data
