import requests
from bs4 import BeautifulSoup
from datetime import date


HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
TODAY = date.today()


def parsePage(url, className):
	response = requests.get(url, HEADERS)
	try:
		soup = BeautifulSoup(response.content, 'lxml').find(class_=className)
		try:
			full_info = {
				'date': soup.find('div', class_='info').find('div', class_='date').text,
				'title': soup.find('h1').text,
				'description': soup.find('div', class_='description').text,
				'content': '',
				'author': f'https://www.zakon.kz{soup.find("div", class_="author").find("a").href}'
			}
			for content in soup.select('p, blockquote, quote'):
				full_info['content'] += content.text
			return full_info
		except soup is None:
			print('Error: There is no Content')
			exit(404)
	except response.status_code != 200:
		print('Error: There is no Connection 2')
		exit(response.status_code)


def search(News, url):
	response = requests.get(url, HEADERS)
	try:
		xhr = response.json()
		for data in xhr['data_list']:
			if str(data['data']) != str(TODAY):
				return False
			for new in data['news_list']:
				News.append(parsePage(f'https://www.zakon.kz/{new["alias"]}', 'articleBlock'))
		return True
	except response.status_code != 200:
		print('There is no Connection 1')
		exit(response.status_code)


def parse():
	News = []
	# перебтраю все страницы
	for i in range(1, 10 ** 6):
		if not search(News, f'https://www.zakon.kz/api/all-news-ajax/?pn={i}&pSize=24'):
			break
	with open(f'Data/{TODAY}.txt', 'w') as outfile:
		outfile.write(str(News))


if __name__ == '__main__':
	parse()
