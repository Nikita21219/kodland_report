from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os
import requests
import datetime

goodle_form_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSc-RUvaDkEG19GHG_P2kWe0XCOjdWndRlBUQvirw4xCcOtwtg'
url_response = goodle_form_URL + '/formResponse'
url_referer = goodle_form_URL + '/viewform'
form_data = {
	'entry.' : 'Мадорский Никита Вячеславович | 123202', # ФИО преподавателя
	'entry.': 'Анцупова Александра ТЛ2', #ТЛ
	'entry.': 'Индивидуальные уроки (8 лет и старше)', #Формат обучения
	'entry.': 'Python Базовый', #Какой курс
	'entry.': 'М1У3', #Какой модуль и урок вы прошли
	'entry.': 'Онлайн_Ind1422', #Номер группы
	'entry.': '2022', #Дата проведения занятия год
	'entry.': '03', #Дата проведения занятия месяц
	'entry.': '09', #Дата проведения занятия день
	'entry.': 'Нет', #Возникали ли технические трудности
	'entry.': '5', #Насколько вы удовлетворены методическими материалами
	'entry.': 'Да', #Успели пройти весь материал
	'entry.': 'Нет', #Был ли непонятный для ученика материал
	'entry.': 'Да', #Уложились в тайминг?
	'entry.': 'https://test.mp4', #Ссылка на запись урока
} # real form!!!!

form_data_test = {
	'entry.215990568' : 'Мадорский Никита Вячеславович', # ФИО
	'entry.701392505' : 'Анцупова Александра ТЛ2', # ТЛ
	'entry.92894374' : 'Индивидуальные уроки (8 лет и старше)', # Формат обучения
	'entry.535140742' : 'Python Базовый', # Какой курс
	'entry.1911636169': 'М1У1', #модуль и урок
	'entry.356726832': 'Онлайн_Ind1422', #Номер группы
	'entry.1703763926_year' : str(datetime.datetime.today().year), # дата год
	'entry.1703763926_month' : str(datetime.datetime.today().month), # дата месяц
	'entry.1703763926_day' : str(datetime.datetime.today().day), # дата день
	'entry.2031718956' : '5', # Насколько вы удовлетворены 
	# 'entry.92894374_sentinel': '',
	# 'entry.535140742_sentinel': '',
	# 'entry.2031718956_sentinel': '',
} # test form

user_agent = {
	'Referer': url_referer,
	'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
}


# r = requests.post(url_response, data=form_data_test, headers=user_agent)
# print(r.status_code)
# exit()


gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

path_file = '/Users/a1/Downloads/2022-03-09 12.00.07 Kodland_Ind 77631215385/Онлайн_Ind1422М1У5.mp4'


def upload_test():
	my_file = drive.CreateFile({'title': f'test_photo.jpg'})
	my_file.SetContentFile('/Users/a1/Downloads/Работа/Кодленд/GUI/test_photo.jpg')
	my_file.Upload()
	my_file.InsertPermission({
		'type': 'anyone',
		'value': 'withLink',
		'role': 'reader',
	})
	link_to_file = my_file['alternateLink']


def get_group_name(filename):
	filename_split = filename.split('_')
	return filename_split[0] + '_' + filename_split[1]


def get_lesson(filename):
	filename_split = filename.split('_')
	return filename_split[2]


def get_course(filename):
	courses_dict = {
		'28' : 'Python Pro',
		'67' : 'Python Базовый',
		'183' : 'Python Pro',
		'185' : 'Python Базовый',
		'186' : 'Python Базовый',
		'299' : 'Python Pro',
		'300' : 'Python Pro',
		'301' : 'Python Базовый',
		'379' : 'Python Pro',
		'425' : 'Python Pro',
	}
	filename_split = filename.split('_')
	course_number = filename_split[3]
	return courses_dict.get(course_number)


def upload_lesson():
	# filename в формате Онлайн_Ind1422_М1У1_301
	videos = []
	for dirpath, dirnames, filenames in os.walk("/Users/a1/Downloads/Работа/Кодленд/Записи уроков/"):
		# перебрать файлы
		for filename in filenames:
			if filename[-4:] == '.mp4':
				videos.append(filename)
				# my_file = drive.CreateFile({'title': f'{filename}'})
				# my_file.SetContentFile(os.path.join(dirpath, filename))
				# my_file.Upload()
				# my_file.InsertPermission({
				# 	'type': 'anyone',
				# 	'value': 'withLink',
				# 	'role': 'reader',
				# })




	# for file in os.listdir('/Users/a1/Downloads/Работа/Кодленд/Записи уроков'):
	#     my_file = drive.CreateFile({'title': f'Онлайн_Ind1422М1У5.mp4'})
	#     my_file.SetContentFile(path)
	#     my_file.Upload()


if __name__ == '__main__':
	# upload_lesson()
	# upload_test()

# file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
# file1.SetContentString('Hello World!') # Set content of the file from given string.
# file1.Upload()
