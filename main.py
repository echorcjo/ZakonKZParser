import random
import requests
import time
import lxml
from bs4 import BeautifulSoup
from datetime import date


# consts
HEADERS = {
	'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}
TODAY = date.today()
PROXY = [
	'222.167.234.172:1000',
	'201.92.247.3:1000',
	'76.119.53.226:6391',
	'67.82.164.145:26677',
	'90.30.133.60:21011'
]


# parsing content, info
def parsePage(url, className):
	time.sleep(random.randint(3, 5))
	response = requests.get(url, headers=HEADERS, proxies=PROXY[random.randint(0, 5)])
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


# searching needed news
def search(News, url):
	time.sleep(random.randint(3, 5))
	proxy = {
		'http': 'http://' + PROXY[random.randint(0, 5)],
		'https': 'https://' + PROXY[random.randint(0, 5)]
	}
	response = requests.get(url, headers=HEADERS, proxies=proxy)
	try:
		# данные которые передаются через API я сохранил в формате JSON
		# в этих же данных хранится дата и ссылка нашего новостя, то что нам нужно
		xhr = response.json()
		for data in xhr['data_list']:
			if str(data['data']) != str(TODAY):
				return False
			for new in data['news_list']:
				News.append(parsePage(f'https://www.zakon.kz/{new["alias"]}', 'articleBlock'))
		return True
	except response.status_code != 200:
		# код 200 это код когда соеденение будет установлено
		# если же это не так то что то пошло не так
		print('There is no Connection 1')
		exit(response.status_code)


def parse():
	News = []
	# перебираю все страницы, пока ихние даты совпадает с сегодняшней
	# если в какой то момент это не будет работать цикл прекратить свою работу
	for i in range(1, 10 ** 6):
		if not search(News, f'https://www.zakon.kz/api/all-news-ajax/?pn={i}&pSize=24'):
			break
	with open(f'Data/{TODAY}.txt', 'w') as outfile:
		outfile.write(str(News))


if __name__ == '__main__':
	# данный сайт типа 'client side rendering'
	# это значит данные о новостях нам передается через API
	# из-за этого мы не сможем ее просто так спарсить с BS4
	# я нашел ссылку запроса и через нее передается нам данные ввиде JSON файла
	parse()
	# в каких же случаех парсер перестанет работать
	# 1. Если АДМИНЫ поменяют какой-то тег/класс в коде HTML
	# 2. Если они будут блокировать IP который будет отправлять много запросов
	# 3. Если сайт начнет блокировать частые запросы на сервер из одного IP
	# Чтобы решить проблему под номером 3 я отправляю запросы каждые 3-5 секунд
	# почему рандомное число?
	# потому что думал если бот который будет искать последовательность запросов
	# и она найдет что мой парсер отправляет запросы в фиксированной период времени
	# Чтобы решить проблему под номером 2 я собрал IP в каком-то файле и передавал это IP в requests
