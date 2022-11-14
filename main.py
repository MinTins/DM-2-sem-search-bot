from collections import defaultdict
import re
import glob

#from data_topics import topics

with open("data_topics.py", "r", encoding="utf-8") as f:
	topics = f.read()


path_transl = {"Задачі з теорії автоматів": "Automate", "Задачі з теорії графів": "Graphs", "Задачі з теорії булевих функцій": "Bule"}


def formatting_data(topics) -> "Dict[Dict(task: task_number)]":
	result = defaultdict(dict)
	current_theme = None

	for x in re.finditer(r"(\*\*\*(?P<theme>[а-яієї ]+)\*\*\*|\n(?P<task>(?P<task_number>\d+)\..+))", topics, flags=re.IGNORECASE):
		if x.group("theme"):
			current_theme = x.group("theme")
			#print(current_theme)

		result[current_theme][x.group("task")] = x.group("task_number")

	return result


formated_tasks = formatting_data(topics)

async def search_fragment(search, data):
	search = re.sub("['`]", "’",search.lower())

	result: list = []

	for theme in data:
		for task in data[theme]:
			if task is not None and search in task.lower():
				task_number = data[theme][task]
				result.append((theme, task_number, task, task[task.lower().find(search)-20:len(search) + task.lower().find(search)+20] ))

	return result


async def research_files(datatuple):
	result = []

	for task in datatuple:
		theme_dir = path_transl[task[0]]

		files = glob.glob(f"{theme_dir}/*{task[1]}*.*")
		if files:
			result.extend((task[2], path, task[3]) for path in files)

	return result