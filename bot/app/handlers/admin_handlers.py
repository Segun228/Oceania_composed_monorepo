from app.handlers.router import admin_router as router
import logging
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram import F
from typing import Dict, Any
from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot
from aiogram.exceptions import TelegramAPIError
from io import BytesIO
import asyncio

from aiogram.types import InputFile

from app.keyboards import inline_admin as inline_keyboards

from app.states.states import Post, Category, Send, File

from aiogram.types import BufferedInputFile


from app.keyboards.inline_admin import get_catalogue, get_posts

from app.filters.IsAdmin import IsAdmin

from app.requests.user.login import login
from app.requests.helpers.get_cat_error import get_cat_error_async
from app.requests.get.get_categories import get_categories
from app.requests.get.get_post import get_post
from app.requests.post.postPhotos import post_photos
from app.requests.helpers.get_cat_error import get_cat_error_async

from app.requests.post.postCategory import post_category
from app.requests.post.postPost import post_post
from app.requests.put.putCategory import put_category
from app.requests.put.putPost import put_post
from app.requests.delete.deleteCategory import delete_category
from app.requests.delete.deletePost import delete_post
from app.requests.user.get_alive import get_alive
from app.requests.user.make_admin import make_admin

from app.requests.files.get_report import get_report
from app.requests.files.put_report import put_report
from app.requests.files.replace_report import replace_report
#===========================================================================================================================
# Конфигурация основных маршрутов
#===========================================================================================================================


@router.message(CommandStart(), IsAdmin())
async def cmd_start_admin(message: Message, state: FSMContext):
    data = await login(telegram_id=message.from_user.id)
    if data is None:
        logging.error("Error while logging in")
        await message.answer("Бот еще не проснулся, попробуйте немного подождать 😔", reply_markup=inline_keyboards.restart)
        return
    await state.update_data(telegram_id = data.get("telegram_id"))
    await message.reply("Приветствую, админ! 👋")
    await message.answer("Я бот Oceanica. Я помогу вам выбрать нужные позиции рыбы и морепродуктов и расскажу о новых поступлениях")
    await message.answer("Сейчас ты можешь создавать, удалять и изменять как категории, так и объявления")
    await message.answer("Также ты можешь активировать расслыку по активным пользователям")
    await message.answer("Я много что умею 👇", reply_markup=inline_keyboards.main)
    await state.clear()


@router.callback_query(F.data == "restart", IsAdmin())
async def callback_start_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    data = await login(telegram_id=callback.from_user.id)
    if data is None:
        logging.error("Error while logging in")
        await callback.message.answer("Бот еще не проснулся, попробуйте немного подождать 😔", reply_markup=inline_keyboards.restart)
        return
    await state.update_data(telegram_id = data.get("telegram_id"))
    await callback.message.reply("Привет, админ! 👋")
    await callback.message.answer("Я бот Oceanica. Я помогу вам выбрать нужные позиции рыбы и морепродуктов и расскажу о новых поступлениях")
    await callback.message.answer("Я много что умею 👇", reply_markup=inline_keyboards.main)
    await callback.answer()


@router.message(Command("help"), IsAdmin())
async def cmd_help(message: Message):
    await message.reply(text="Этот бот помогает выбирать рыбу и морепродукты из нужных категорий\n\n Он может выполнять несколько интересных функций \n\nВы можете выбирать интересующие вас виды рыбы и морепродуктов из категорий, имеющихся в наличии\n\nЕсли у вас остались вопросы, звоните нам или пишите в тех поддержку, мы всегда на связи:\n\nтелефон коммерческого агента\n\n@dianabol_metandienon_enjoyer", reply_markup=inline_keyboards.home)

@router.message(Command("contacts"), IsAdmin())
async def cmd_contacts(message: Message):
    text = "Связь с менеджером: 📞\n\n\\тут телефон коммерческого агента\n\n"+"Связь с разрабом: 📞\n\n\\@dianabol\\_metandienon\\_enjoyer 🤝"
    await message.reply(text=text, reply_markup=inline_keyboards.home, parse_mode='MarkdownV2')

@router.callback_query(F.data == "contacts", IsAdmin())
async def contacts_callback(callback: CallbackQuery):
    text = "Связь с менеджером: 📞\n\n\\тут телефон коммерческого агента\n\n"+"Связь с разрабом: 📞\n\n\\@dianabol\\_metandienon\\_enjoyer 🤝"
    await callback.message.edit_text(text=text, reply_markup=inline_keyboards.home, parse_mode='MarkdownV2')
    await callback.answer()

@router.callback_query(F.data == "main_menu", IsAdmin())
async def main_menu_callback(callback: CallbackQuery):
    await callback.message.answer("Я много что умею 👇", reply_markup=inline_keyboards.main)
    await callback.answer()

#===========================================================================================================================
# Каталог
#===========================================================================================================================
@router.callback_query(F.data == "catalogue", IsAdmin())
async def catalogue_callback_admin(callback: CallbackQuery):
    categories = await get_categories(telegram_id= callback.from_user.id)
    await callback.message.answer("Вот доступные категории👇", reply_markup= await get_catalogue(categories= categories, telegram_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data.startswith("category_"), IsAdmin())
async def category_catalogue_callback_admin(callback: CallbackQuery):
    await callback.answer()
    category_id = callback.data.split("_")[1]
    categories = await get_categories(telegram_id= callback.from_user.id)
    print(category_id)
    current_category = None
    if categories is not None:
        for category in categories:
            if str(category.get("id")) == str(category_id):
                current_category = category
                break
    
    if current_category is None or current_category.get("posts") is None or current_category.get("posts") == []:
        await callback.message.answer("Извините, тут пока пусто, возвращаейтесь позже!", reply_markup= await get_posts(posts=current_category.get("posts"), category=current_category ))
        await callback.answer()
        return
    await callback.message.answer("Вот доступные предложения👇", reply_markup= await get_posts(category= current_category ,posts = current_category.get("posts", [])))


@router.callback_query(F.data.startswith("post_"), IsAdmin())
async def post_catalogue_callback_admin(callback: CallbackQuery):
    await callback.answer()
    post_id = callback.data.split("_")[2]
    category_id = callback.data.split("_")[1]
    post_data = await get_post(
        telegram_id=callback.from_user.id,
        post_id = post_id,
        category_id = category_id
    )
    if post_data is None or not post_data:
        await callback.message.answer("Извините, не удалось получить доступ к позиции", reply_markup=inline_keyboards.home)
        return
    await send_post_photos(callback = callback, post = post_data)
    message_text = (
        f"📝 **Информация о товаре:**\n\n"
        f"**Название:** `{post_data.get('title')}`\n\n"
        f"**Описание:** `{post_data.get('description')}`\n\n"
        f"**Прайс:** `{post_data.get('price')}`\n\n"
        f"**Страна:** `{post_data.get('country')}`\n\n"
        f"**Вес:** `{post_data.get('weight')}`\n\n"
    )
    await callback.message.answer(
        text=message_text,
        parse_mode="MarkdownV2",
        reply_markup= await inline_keyboards.get_post_menu(
            category_id= category_id,
            post_id= post_id,
        )
    )
#===========================================================================================================================
# Поддержка
#===========================================================================================================================


async def send_post_photos(callback: CallbackQuery, post: Dict[str, Any]):
    photo_ids = post.get('photos', [])

    if not photo_ids:
        await callback.message.answer("К сожалению, у этой позиции нет фотографий.")
        return

    first_photo_id = photo_ids[0]
    caption_text = f"**{post.get('title', 'Без названия')}**"
    
    await callback.message.answer_photo(
        photo=first_photo_id,
        caption=caption_text,
        parse_mode="MarkdownV2"
    )

    for photo_id in photo_ids[1:]:
        await callback.message.answer_photo(photo=photo_id)

#===========================================================================================================================
# Создание категории
#===========================================================================================================================


@router.callback_query(F.data == "create_category", IsAdmin())
async def category_create_callback_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Введите название категории")
    await state.set_state(Category.handle_category)
    await callback.answer()

@router.message(Category.handle_category, IsAdmin())
async def category_enter_name_admin(message: Message, state: FSMContext):
    name = (message.text).strip()
    response = await post_category(telegram_id=message.from_user.id, title=name)
    if not response:
        await message.answer("Извините, не удалось создать категорию", reply_markup=inline_keyboards.main)
        return
    await message.answer("Категория создана!", reply_markup= await get_catalogue(telegram_id = message.from_user.id))
    await state.clear()


#===========================================================================================================================
# Создание поста
#===========================================================================================================================


@router.callback_query(F.data.startswith("create_post_"), IsAdmin())
async def post_create_callback_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    catergory_id = callback.data.split("_")[2]
    await state.update_data(category = catergory_id)
    await callback.message.answer("Введите название поста")
    await state.set_state(Post.handle_post)


@router.message(Post.handle_post, IsAdmin())
async def post_enter_name_admin(message: Message, state: FSMContext):
    title = (message.text).strip()
    if not title:
        await message.answer("Введите валидное имя поста")
        return
    await state.update_data(title = title)
    await state.set_state(Post.title)
    await message.answer("Введите описание поста")


@router.message(Post.title, IsAdmin())
async def post_enter_description_admin(message: Message, state: FSMContext):
    description = (message.text).strip()
    if not description:
        await message.answer("Введите валидное описание поста")
        return
    await state.update_data(description=description)
    await state.set_state(Post.description)
    await message.answer("Введите цену")


@router.message(Post.description, IsAdmin())
async def post_enter_price_admin(message: Message, state: FSMContext):
    price = (message.text).strip()
    if not price or not price.isdigit():
        await message.answer("Введите валидную цену")
        return
    await state.update_data(price = price)
    await state.set_state(Post.price)
    await message.answer("Введите страну происхождения")


@router.message(Post.price, IsAdmin())
async def post_enter_country_admin(message: Message, state: FSMContext):
    country = (message.text).strip()
    if not country:
        await message.answer("Введите валидное название страны")
        return
    await state.update_data(country = country)
    await state.set_state(Post.country)
    await message.answer("Введите вес")

@router.message(Post.country, IsAdmin())
async def post_enter_quantity_admin(message: Message, state: FSMContext):
    weight = (message.text).strip()
    if not weight or not weight.isdigit():
        await message.answer("Введите валидное количество")
        return
    data = await state.get_data()
    post_data = await post_post(
        telegram_id= message.from_user.id,
        category_id= data.get("category"),
        title = data.get("title"),
        description= data.get("description"),
        country= data.get("country"),
        price = data.get("price"),
        weight= weight
    )
    if not post_data:
        await message.answer("Извините, ошибка при создании поста", reply_markup=await get_catalogue(telegram_id = message.from_user.id))
        return
    await message.answer("Пост успешно создан")
    message_text = (
        f"📝 **Информация о товаре:**\n\n"
        f"**Название:** `{post_data.get('title')}`\n\n"
        f"**Описание:** `{post_data.get('description')}`\n\n"
        f"**Прайс:** `{post_data.get('price')}`\n\n"
        f"**Страна:** `{post_data.get('country')}`\n\n"
        f"**Вес:** `{post_data.get('weight')}`\n\n"
    )
    await message.answer(message_text, reply_markup=await inline_keyboards.get_post_menu(category_id=post_data.get("category"), post_id=post_data.get("id")), parse_mode="MarkdownV2")
    await state.clear()
#===========================================================================================================================
# Редактирование категории
#===========================================================================================================================
@router.callback_query(F.data.startswith("edit_category_"), IsAdmin())
async def category_edit_callback_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    category_id = callback.data.split("_")[2]
    await state.set_state(Category.handle_edit_category)
    await state.update_data(category_id = category_id)
    await callback.message.answer("Введите название категории")

@router.message(Category.handle_edit_category, IsAdmin())
async def category_edit_name_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data.get("category_id")
    name = (message.text).strip()
    response = await put_category(telegram_id=message.from_user.id, title=name, category_id=category_id)
    if not response:
        await message.answer("Извините, не удалось отредактировать категорию", reply_markup=inline_keyboards.main)
        return
    await message.answer("Категория отредактирована!", reply_markup=await get_catalogue(telegram_id = message.from_user.id))
    await state.clear()

#===========================================================================================================================
# Редактирование поста
#===========================================================================================================================


@router.callback_query(F.data.startswith("edit_post_"), IsAdmin())
async def post_edit_callback_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    catergory_id, post_id = callback.data.split("_")[2:]
    await state.update_data(category = catergory_id)
    await state.update_data(post_id = post_id)
    await callback.message.answer("Введите название поста")
    await state.set_state(Post.handle_edit_post)


@router.message(Post.handle_edit_post, IsAdmin())
async def post_edit_name_admin(message: Message, state: FSMContext):
    title = (message.text).strip()
    if not title:
        await message.answer("Введите валидное имя поста")
        return
    await state.update_data(title = title)
    await state.set_state(Post.title)
    await message.answer("Введите описание поста")


@router.message(Post.title, IsAdmin())
async def post_edit_description_admin(message: Message, state: FSMContext):
    description = (message.text).strip()
    if not description:
        await message.answer("Введите валидное описание поста")
        return
    await state.update_data(description=description)
    await state.set_state(Post.description)
    await message.answer("Введите цену")


@router.message(Post.description, IsAdmin())
async def post_edit_price_admin(message: Message, state: FSMContext):
    price = (message.text).strip()
    if not price or not price.isdigit():
        await message.answer("Введите валидную цену")
        return
    await state.update_data(price = price)
    await state.set_state(Post.price)
    await message.answer("Введите страну происхождения")


@router.message(Post.price, IsAdmin())
async def post_edit_country_admin(message: Message, state: FSMContext):
    country = (message.text).strip()
    if not country:
        await message.answer("Введите валидное название страны")
        return
    await state.update_data(country = country)
    await state.set_state(Post.country)
    await message.answer("Введите вес")


@router.message(Post.country, IsAdmin())
async def post_edit_quantity_admin(message: Message, state: FSMContext):
    weight = (message.text).strip()
    if not weight or not weight.isdigit():
        await message.answer("Введите валидное количество")
        return
    data = await state.get_data()
    post_data = await put_post(
        telegram_id= message.from_user.id,
        category_id= data.get("category"),
        title = data.get("title"),
        description= data.get("description"),
        country= data.get("country"),
        price = data.get("price"),
        weight= weight,
        post_id= data.get("post_id"),
    )
    if not post_data:
        await message.answer("Извините, ошибка при обновлении поста", reply_markup= await get_catalogue(telegram_id = message.from_user.id))
        return
    await message.answer("Пост успешно обновлен")
    message_text = (
        f"📝 **Информация о товаре:**\n\n"
        f"**Название:** `{post_data.get('title')}`\n\n"
        f"**Описание:** `{post_data.get('description')}`\n\n"
        f"**Прайс:** `{post_data.get('price')}`\n\n"
        f"**Страна:** `{post_data.get('country')}`\n\n"
        f"**Вес:** `{post_data.get('weight')}`\n\n"
    )
    await message.answer(message_text, reply_markup=await inline_keyboards.get_post_menu(category_id=data.get("category"), post_id=data.get("post_id")), parse_mode="MarkdownV2")
    await state.clear()

#===========================================================================================================================
# Удаление категории
#===========================================================================================================================

@router.callback_query(F.data.startswith("delete_category_"), IsAdmin())
async def category_delete_callback_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    category_id = callback.data.split("_")[2]
    response = await delete_category(telegram_id=callback.from_user.id, category_id=category_id)
    if not response:
        await callback.message.answer("Извините, не удалось удалить категорию", reply_markup=inline_keyboards.main)
        return
    await callback.message.answer("Категория удалена!", reply_markup=await get_catalogue(telegram_id = callback.from_user.id))
    await state.clear()


#===========================================================================================================================
# Удаление поста
#===========================================================================================================================

@router.callback_query(F.data.startswith("delete_post_"), IsAdmin())
async def post_delete_callback_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    catergory_id, post_id = callback.data.split("_")[2:]
    response = await delete_post(telegram_id=callback.from_user.id, category_id=catergory_id, post_id=post_id)
    if not response:
        await callback.message.answer("Извините, не удалось удалить пост",reply_markup= await get_catalogue(telegram_id = callback.from_user.id))
    await callback.message.answer("Пост успешно удален",reply_markup=await get_catalogue(telegram_id = callback.from_user.id))
    await state.clear()

#===========================================================================================================================
# Добавление фото
#===========================================================================================================================


@router.callback_query(F.data.startswith("add_photo_"), IsAdmin())
async def post_add_photos_callback_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        post_id = callback.data.split("_")[2]
        await state.update_data(post_id=int(post_id))
    except (IndexError, ValueError):
        await callback.message.answer("Ошибка: неверный ID поста.", reply_markup=await get_catalogue(telegram_id= callback.from_user.id))
        await state.clear()
        return
    await callback.message.answer("Отправьте фотографии для поста. После того как закончите, напишите 'Готово'.")
    await state.set_state(Post.waiting_for_photos)


@router.message(Post.waiting_for_photos, IsAdmin(), F.photo)
async def handle_photo_upload_admin(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(photo_id)
    await state.update_data(photos=photos)
    await message.answer("Фотография добавлена. Отправьте ещё или напишите 'Готово'.")

@router.message(Post.waiting_for_photos, F.text.lower() == "готово", IsAdmin())
async def finish_photo_upload_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("post_id")
    photo_ids = data.get("photos", [])
    
    if not photo_ids:
        await message.answer("Вы не отправили ни одной фотографии. Попробуйте снова.")
        return
    response = await post_photos(telegram_id= message.from_user.id ,post_id= post_id, photos= photo_ids)
    if response:
        await message.answer("Фотографии успешно добавлены к посту ID!", reply_markup=await get_catalogue(telegram_id=message.from_user.id))
    else:
        await message.answer("Извините, не удалось добавить фотографии.")
    await state.clear()


#===========================================================================================================================
# Создание рассылки
#===========================================================================================================================

@router.callback_query(F.data == "send_menu", IsAdmin())
async def send_menu_admin(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Send.handle)
    await callback.message.answer(
        "Напишите текст сообщения или прикрепите фото с подписью. "
        "Будьте внимательны: отменить рассылку будет невозможно."
    )

@router.message(Send.handle, IsAdmin(), F.photo)
async def send_photo_message(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    caption = message.caption or ""
    await state.update_data(photo=photo, caption=caption)
    await message.answer("Фото получено. Начинаю рассылку...")
    await start_broadcast(state, message, message.bot)


@router.message(Send.handle, IsAdmin(), F.text)
async def send_text_message(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Текст получен. Начинаю рассылку...")
    await start_broadcast(state, message, message.bot)


async def start_broadcast(state: FSMContext, message: Message, bot: Bot):
    data = await state.get_data()
    users_data = await get_alive(telegram_id=message.from_user.id)

    if not users_data:
        await message.answer("Ошибка при рассылке. Попробуйте позже.")
        await state.clear()
        return

    tasks = []
    for user in users_data:
        user_id = user.get("telegram_id")
        if "photo" in data:
            tasks.append(
                bot.send_photo(chat_id=user_id, photo=data["photo"], caption=data.get("caption", ""))
            )
        elif "text" in data:
            tasks.append(
                bot.send_message(chat_id=user_id, text=data["text"])
            )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_sends = sum(1 for r in results if not isinstance(r, TelegramAPIError))
    failed_sends = len(results) - successful_sends

    await message.answer(
        f"Рассылка завершена.\n✅ Успешно: {successful_sends}\n❌ Ошибки: {failed_sends}",
        reply_markup=inline_keyboards.main
    )
    await state.clear()

#===========================================================================================================================
# Разрешение доступа
#===========================================================================================================================


@router.callback_query(F.data.startswith("access_give"), IsAdmin())
async def give_acess_admin(callback: CallbackQuery, state: FSMContext, bot:Bot):
    request = str(callback.data)
    try:
        user_id = list(request.split("_"))[2]
        if not user_id:
            logging.error("Ошибка предоставления доступа")
            return
        response = await make_admin(
            telegram_id= callback.from_user.id,
            target_user_id= user_id
        )
        if not response:
            logging.error("Ошибка предоставления доступа")
            await bot.send_message(chat_id=int(user_id), text="К сожалению, вам было отказано в предоставлении прав администратора", reply_markup=inline_keyboards.home)
        else:
            logging.info(response)
            await callback.message.answer("Права администратора были успешно предоставлены", reply_markup=inline_keyboards.home)
            await bot.send_message(chat_id=user_id, text="Вам были предоставлены права администратора", reply_markup=inline_keyboards.home)
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data.startswith("access_reject"), IsAdmin())
async def reject_acess_admin(callback: CallbackQuery, state: FSMContext, bot:Bot):
    request = str(callback.data)
    try:
        user_id = list(request.split("_"))[2]
        await bot.send_message(chat_id=int(user_id), text="К сожалению, вам было отказано в предоставлении прав администратора", reply_markup=inline_keyboards.home)
    except Exception as e:
        logging.error(e)



#===========================================================================================================================
# Файловое меню
#===========================================================================================================================


@router.callback_query(F.data == "file_panel", IsAdmin())
async def file_panel_admin(callback: CallbackQuery, state: FSMContext, bot:Bot):
    await callback.message.edit_text(
        "Выберите интересующую функцию",
        reply_markup= inline_keyboards.file_panel
    )


@router.callback_query(F.data == "get_report", IsAdmin())
async def send_report_admin(callback: CallbackQuery, state: FSMContext, bot: Bot):

    await callback.answer("Готовлю ваш отчёт...", show_alert=False)
    docs = await get_report(telegram_id=callback.from_user.id)

    if not docs:
        await callback.message.answer("Извините, не удалось загрузить отчёт. Обратитесь в поддержку.")
        return

    await callback.message.answer(
        "Вот ваш отчёт!"
    )

    await bot.send_document(
        chat_id=callback.message.chat.id,
        document=BufferedInputFile(docs.getvalue(), filename="report.xlsx"),
        reply_markup=inline_keyboards.file_panel
    )
    await state.clear()



@router.callback_query(F.data == "add_posts", IsAdmin())
async def file_add_posts_admin(callback: CallbackQuery, state: FSMContext, bot:Bot):
    await callback.message.answer(
        "Это текущие позиции"
    )
    docs = await get_report(telegram_id=callback.from_user.id)
    await bot.send_document(
        chat_id=callback.message.chat.id,
        document=BufferedInputFile(docs.getvalue(), filename="report.xlsx"),
    )
    await callback.message.answer(
        "Вы в режиме добавления позиций. Отправте в чат файл с позициями, которые хотите добавить, в том же формате"
    )
    await state.set_state(File.waiting_for_file)


@router.message(File.waiting_for_file, IsAdmin())
async def upload_add_file_admin(message: Message, state: FSMContext, bot: Bot):
    try:

        file = await bot.get_file(message.document.file_id)
        file_bytes = await bot.download_file(file.file_path)
        response = await put_report(message.from_user.id, file_bytes)

        # Обработка результата
        if not response:
            await message.answer(
                "К сожалению, не удалось обработать файл. Убедитесь, что формат файла соответствует установленному."
            )
            await state.clear()
            return
        await message.answer("Файл успешно получен и обработан!", reply_markup= inline_keyboards.file_panel)
        await state.clear()

    except Exception as e:
        await state.clear()
        logging.error(f"Ошибка при обработке Excel: {e}")
        await message.answer("Не удалось обработать файл. Убедитесь, что это корректный Excel (.xlsx).", reply_markup= inline_keyboards.file_panel)


@router.callback_query(F.data == "replace_posts", IsAdmin())
async def file_replace_posts_admin(callback: CallbackQuery, state: FSMContext, bot:Bot):
    await callback.message.answer(
        "Это текущие позиции"
    )
    docs = await get_report(telegram_id=callback.from_user.id)
    await bot.send_document(
        chat_id=callback.message.chat.id,
        document=BufferedInputFile(docs.getvalue(), filename="report.xlsx"),
    )
    await callback.message.answer(
        "Вы в режиме полного обновления позиций. Отправте в чат файл с позициями, которые хотите добавить, в том же формате. Будте внимательны, текущие позиции будут удалены"
    )
    await state.set_state(File.waiting_for_replace_file)


@router.message(File.waiting_for_replace_file, IsAdmin())
async def upload_replace_file_admin(message: Message, state: FSMContext, bot: Bot):
    try:
        file = await bot.get_file(message.document.file_id)
        file_bytes = await bot.download_file(file.file_path)
        response = await replace_report(message.from_user.id, file_bytes)
        if not response:
            await message.answer(
                "К сожалению, не удалось обработать файл. Убедитесь, что формат файла соответствует установленному."
            )
            await state.clear()
            return
        await message.answer("Файл успешно получен и обработан! Позиции обновлены", reply_markup= inline_keyboards.file_panel)
        await state.clear()

    except Exception as e:
        logging.error(f"Ошибка при обработке Excel: {e}")
        await state.clear()
        await message.answer("Не удалось обработать файл. Убедитесь, что это корректный Excel (.xlsx).", reply_markup= inline_keyboards.file_panel)
