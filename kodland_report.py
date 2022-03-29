import os
import requests
import datetime
import re
import platform
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

from data import teacher_name, team_lead_name, path_to_folder_zoom, folder_name_google_disk

goodle_form_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSfkYyW4H8QtOMe3JAg_ELRRPKsis1WHp4NXJ2dst3S3FH3ZZQ'

url_response = goodle_form_URL + '/formResponse'
url_referer = goodle_form_URL + '/viewform'

# Определения сепаратора для разных ОС
separator = '/'
if platform.system() == 'Windows' or platform.system() == 'win32':
	separator = '\\'
user_agent = {
	'Referer': url_referer,
	'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
}

# Аутентификация гугл
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def get_group_name(filename):
	"""Получить группу из названия видеозаписи урока"""
	filename_split = filename.split('_')
	group_name = filename_split[1] + '_' + filename_split[2]
	return group_name.replace('й', 'й')


def get_lesson(filename):
	"""Получить модуль и урок из названия видеозаписи урока"""
	filename_split = filename.split('_')
	return filename_split[4].split('.')[0]


def get_course(filename):
	"""Получить курс по id из названия видеозаписи урока"""
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
	} # словарь, в котором хранятся курсы как в гугл форме
	filename_split = filename.split('_')
	course_number = filename_split[3]
	return courses_dict.get(course_number)


def check_filename(filename):
	"""Проверка формата названия видеорука"""
	result = re.match(r'Онлайн_Ind\d{1,}_\d{1,}_М[1-8]У[1-8]\.mp4', filename)
	if not result:
		print('ERROR: Формат названия видеозаписи неверный\nПример: Онлайн_Ind1422_301_М1У5.mp4')
		return 1
	return 0


def send_google_form(path_to_file='', link_to_file=''):
	"""Отправка гугл формы"""
	filename = path_to_file.split(separator)[-1]
	group_name = get_group_name(filename)
	date_file = str(datetime.datetime.fromtimestamp(os.path.getctime(path_to_file))).split('-')
	form_data_test = {
		'entry.433313432': teacher_name, # ФИО
		'entry.1399459001': team_lead_name, # ТЛ
		'entry.213406366': group_name, #Номер группы
		'entry.648502256': 'Индивидуальные уроки (8 лет и старше)', # Формат обучения
		'entry.324580992_year': date_file[0], # дата год
		'entry.324580992_month': date_file[1], # дата месяц
		'entry.324580992_day': date_file[2].split()[0], # дата день
		'entry.708310721': get_lesson(filename), # Модуль и урок
		'entry.779449585': get_course(filename), # Какой курс
		'entry.1989654872': link_to_file, # Ссылка на видео на гугл диск
	} # данные для отправки гугл формы
	r = requests.post(url_response, data=form_data_test, headers=user_agent)
	if r.status_code == 200:
		print(f'Форма по группе {group_name} отправлена успешно')
	else:
		print(f'\nERROR: Форма по группе {group_name} не отправлена, произошла какая-то ошибка')


def clear_google_disk(dir_id):
	"""Удаление видеоуроков, которые хранятся на диске больше месяца и перемещение их в корзину"""
	file_list = drive.ListFile({'q': f"'{dir_id}' in parents and trashed=false"}).GetList()
	for file in file_list:
		file = drive.CreateFile({"id": file['id']})
		date_of_upload_file = datetime.datetime.strptime(file['createdDate'].split('T')[0], "%Y-%m-%d")
		td = datetime.datetime.now() - date_of_upload_file
		if td.days >= 31:
			file.Trash() # удаление файла с гугл диск по истечении 31 дня


def upload_lessons():
	"""Загрузка видеоуроков из папки на гугл диск"""
	file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	dir_id = ''
	for dir in file_list:
		if(dir['title'] == folder_name_google_disk):
			dir_id = dir['id']
	if dir_id == '':
		print('ERROR: Я не смог найти твою папку на гугл диск')
		exit()
	clear_google_disk(dir_id) # удаление уроков, которые были загружены более 31 дня назад
	for dirpath, dirnames, filenames in os.walk(path_to_folder_zoom):
		for filename in filenames:
			if filename.endswith('.mp4') and not filename.startswith('uploaded_'):
				if check_filename(filename):
					continue
				file = drive.CreateFile({
					'title': filename,
					"parents": [{"kind": "drive#fileLink", "id": dir_id}],
				})
				path_to_file = os.path.join(dirpath, filename)
				file.SetContentFile(path_to_file)
				file.Upload()
				file.InsertPermission({
					'type': 'anyone',
					'value': 'withLink',
					'role': 'reader',
				})
				new_filename = dirpath + separator + 'uploaded_' + filename
				os.rename(path_to_file, new_filename)
				link_to_file = file['alternateLink']
				# Загрузка формы по этому уроку
				send_google_form(new_filename, link_to_file)


if __name__ == '__main__':
	upload_lessons()
