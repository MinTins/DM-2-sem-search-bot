from aiogram import Bot, Dispatcher, types, executor, utils
from main import *
from file_loaded import files_on_server

from config import BOT_TOKEN, CHAT_TO_LOAD_FILES


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

on_loading=defaultdict(bool)

async def load_on_server(task, path, desc, res_number=0, request=" "):
	file = await bot.send_document(CHAT_TO_LOAD_FILES, document=open(path, "rb"))
	files_on_server[path] = file.document.file_id
	on_loading[path] = False

	return types.InlineQueryResultCachedDocument(id=f"res{res_number}", title=desc, document_file_id=file.document.file_id, description=desc, caption=task,reply_markup={"inline_keyboard": 
				[[{"text": "Відкрить результати", "switch_inline_query_current_chat": request}]]})


async def search_results(query):
	search = query.query

	searched_tasks = await search_fragment(search, formated_tasks)
	data_files = await research_files(searched_tasks)
	data_files = set(data_files[:15])

	result = await gen_inline_res(query, data_files)

	return result


async def need_to_load(files):
	no_exist = []

	for file in files:
		if not files_on_server.get(file[1]):
			no_exist.append(file)

	return no_exist


async def save_loaded_base(file,files_on_server):
	with open(file, "w", encoding="utf-8") as f:
		f.write(f"{files_on_server=}")


async def gen_inline_res(query, files):
	result = []
	loading = False

	need_to_loading = await need_to_load(files)

	if need_to_loading:
		loading = True
		await bot.answer_inline_query(query.id, results=[], switch_pm_text=f"Йде загрузка {len(need_to_loading)}/{len(files)} файлів. Почекайте трохи і напишіть ще раз.", switch_pm_parameter="need_loading", cache_time=0, is_personal=True)



	res_number = 0
	for file in files:
		doc = None

		if (file_id:=files_on_server.get(file[1])):
			doc = types.InlineQueryResultCachedDocument(id=f"res{res_number}", title=file[1].split("\\")[-1], document_file_id=file_id, description=file[2], caption=file[0], reply_markup={"inline_keyboard": 
				[[{"text": "Відкрить результати", "switch_inline_query_current_chat": query.query}]]})
			res_number += 1

		else:
			if not on_loading[file[1]]:
				on_loading[file[1]] = True
				doc = await load_on_server(*file, res_number=res_number, request=query.query)
				res_number += 1

			if loading:
				await save_loaded_base("file_loaded.py", files_on_server)

		if doc:
			result.append(doc)

	return result




@dp.inline_handler(lambda inline_query: True)
async def inline_worker(query):
	if len(query.query) > 0:
		print(query)
		if query.from_user.username in ["mintnt", "sanfunok", "junior_programer", "DmytroKravchuk"]:
			result = await search_results(query)
			if result:
				await bot.answer_inline_query(query.id, results=result, cache_time=500, is_personal=False)

			else:
				await bot.answer_inline_query(query.id, results=[], switch_pm_text=f"Не знайдено співпадінь по запросу.", switch_pm_parameter="empty", cache_time=0, is_personal=True)
	


executor.start_polling(dp, skip_updates=True)