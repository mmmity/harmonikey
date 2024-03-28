# harmonikey

A python-based application for typing practice with TUI (text user interface)

МФТИ, Практикум Python 2024, 1 курс, Б05-328, Канухин Александр

## Описание

Клавиатурный тренажер - приложение для практики быстрой печати с текстовым интерфейсом (TUI).
Пользователю дается какой-то текст, загруженный из шаблонов или случайно сгенерированный. Нужно как можно быстрее набрать этот текст на клавиатуре без ошибок. 
Пользователь может видеть свои показатели (скорость набора в разных единицах измерения, количество допущенных ошибок и пр.) где-то в интерфейсе.

## На данный момент готово
Базовый интерфейс тренажера, загрузка текста из файла, подсчет и сохранение статистики в .csv-файл

## Запуск
Установить зависимости: `pip install -r requirements.txt`
Запустить: `python main.py`, находясь в корне проекта

В терминале появится бегущая строка со словами, которые нужно набирать.
В левом верхнем углу будет отображаться затраченное время и количество набранных слов.
После того, как текст закончится, результаты запуска (имя пользователя, файл с тренировкой, игровой режим (пока что захардкоженные), количество слов, количество символов, затраченное время, количество ошибок) сохранится в `stats.csv` тоже в корневой папке проекта.

## Реализуемый функционал

### Минимальный функционал
Возможность запустить тренажер на тексте, полученном откуда-то извне (может быть, захардкоженном).
Запуск тренажера: в одной части экрана показывает нужный текст, в другой поле для ввода от пользователя.
Пользователь набирает показанный ему текст с клавиатуры, тренажер не дает ему совершать ошибок. 
Как только весь текст был набран, показать время, которое было потрачено на набор. Также показать кнопки перезапуска, выхода, выбора нового текста.

### Источники текста

1. Из текстового файла: перед запуском тренажера можно выбрать файл, из которого нужно загрузить текст для набора.
2. Сгенерированный, случайные слова: перед запуском тренажера можно установить флаг "случайный текст", после чего приложение сгенерирует набор слов из файла словаря, который хранится в файлах приложения (слова в нем разделены переводами строки). По умолчанию будут даны топ1000 английских и русских слов, а так же топ10000 длины более 6 символов.


### UI-фишки (опционально)
1. Вместо отдельного поля для текста и ввода сделать одно поле. Символы, введенные пользователем будут окрашиваться в другой цвет, возможно будет двигаться курсор (как сделано в [Monkeytype](https://monkeytype.com))
Позволить пользователю ошибаться, в таком случае отрисовывать символы, введенные им, поверх подсказки, но красным цветом. Позволить пользователю стирать то, что он уже ввел с помощью Backspace

2. В процессе набора текста показывать где-нибудь в углу статистику: wpm (words per minute, количество набранных слов в минуту), cpm (characters per minute, количество набранных символов в минуту), количество ошибок. Сделать эту фичу отключаемой (статистика в любом случае будет показываться в конце)

### Дополнительные фичи (опционально)
Переключаемые режимы:
- Бесконечно генерируемый текст и ограниченное время VS ограниченный, сгенерированный один раз либо загруженный из файла текст, и безлимитное время
- Вылетать при первой ошибке VS вообще не давать делать ошибки VS позволять ошибаться и исправлять, считая количество ошибок как доп. статистику

Создание пользователей и хранение рекордов локально в csv-файлах

## Стек

Python 3.11

## Зависимости

[blessed](https://github.com/jquast/blessed) - фреймворк для создания текстовых интерфейсов

## Архитектура

### Класс `TextGenerator`
Абстрактный класс, от которого наследуются `RandomTextGenerator` и `FileTextGenerator`. Содержит методы `next_word() -> str`, а также `words_before(int) -> str` и `words_after(int) -> str` (для визуализации).

### Класс `RandomTextGenerator`
Содержит строку `vocab` со словарем, слова разделены переводами строки. Также содержит очередь `pool`, в которой всегда есть не более 7 сгенерированных слов. При инициализации случайно генерирует первые 4 слова.
Метод `next_word()` удаляет первое слово из `pool`, если в нем уже есть 7 слов, добавляет новое слово в конец и возвращает слово на `-4` позиции (в середине пула).
Метод `words_before(n: int)` возвращает `max(3, n)` слов из начала очереди, `words_after` - из конца.

### Класс `FileTextGenerator`
Содержит текст файла `words`, разделенный на слова пробельными символами. Также содержит указатель `current_word` на текущее слово, изначально стоящий на первом.
Метод `next_word()` возвращает слово под указателем, сдвинув указатель на 1. Если указатель больше, чем размер массива `words`, кидает исключение `EndOfFile`, которое поймается в классе `Training`, после чего вызовется `Training.finish()`
Метод `words_before(n: int)` возвращает `n` слов из текста перед текущим, если их столько есть, иначе все до начала, `words_after` - то же самое, но после текущего.

### Класс `TextOverseer`
Содержит `TextGenerator`, а так же строки `current_word`, `input` и `error`.
Также содержит ссылку на `Training`, к которому привязан.
Метод `handle_char(char|backspace)`, который добавляет символ в `input`, также как-то обрабатывая его, если он неверный, в зависимости от режима, стоящего в `Training` (не добавляет никуда, либо добавляет в `error` и увеличевает количество ошибок в `Training.Statistics`, либо кидает исключение, которое поймается в `Training`, вызвав `finish()`). Если `input` и `current_word` совпадали, а символ - пробел, то вызывает метод `Training.Statistics.add_word(current_word)`, и меняет слово на следующее в генераторе.

### Класс `Statictics`
Поля `word_count`, `character_count`, `error_count`, `start_timer`, `user`.
Методы `get_wpm`, `get_cpm`, возвращающие количество слов/символов, деленное на пройденное время.
Метод `add_word(string)`, который увеличивает `word_count` на 1, а `character_count` на длину слова.
Метод `save_to_file(file)`, который дописывает статистику в csv-файл

### Класс `FileStatistics`
Отвечает за загрузку глобальной статистики из файла. Содержит подструктуру `Entry`, в которой хранится статистика за один запуск.
Список `entries`, хранящий в себе все загруженные статистики запуска, а так же словари `by_user` и `by_text_tag`, в которых они сгруппированы по имени пользователя и по названию упражнения (либо название файла с текстом, либо, если слова случайные, название словаря).
Метод `add_file(filename)` подгружает статистику из нового файла, добавляя ее к уже существующей в экземпляре класса.
Метод `user_best_stats(username)` возвращает словарь, в котором лежат лучшие по wpm (words per minute) результаты пользователя за каждое упражнение.
Метод `text_best_stats(text_tag, n_entries)` возвращает список лучших по wpm (words per minute) запусков конкретного упражнения.

### Класс `State`
Абстрактный класс состояния, от которого наследуются классы `MainMenu`, `BeforeTraining`, `Training`, `AfterTraining`.
Содержит ссылку на `Program`, в котором находится.
Методы:
- `visualize()` - возвращает интерфейсу, что именно нужно отрисовывать
- `handle_key(key)` - обрабатывает нажатую на клавиатуре кнопку
- `switch(State) -> State` - возвращает новое состояние
- `tick()` - делает то, что нужно делать каждый тик программы в этом конкретном состоянии

### Класс `Program`
Содержит текущее состояние программы `State`


### Класс `Training`
- Экземпляр класса `Statistics`
- Экземпляр класса `TextOverseer`
- Метод `handle_key(key)`, если это Escape, то вызывает `finish()`, иначе отправляет в `TextOverseer`. Если прилетело исключение, вызывает `finish()`
- Метод отрисовки `visualize()`: использует методы `words_before()`, `words_after()` и атрибут `current_word()` у `TextOverseer.TextGenerator`, чтобы их отобразить в интерфейсе: несколько слов до текущего, несколько слов после, а так же то, которое сейчас пишется, вместе с позицией курсора.
- Метод `finish()`, который меняет состояние у `Program` на `switch(AfterTraining)`, предварительно создав `AfterTraining` с посчитанной статистикой

### Класс `Widget`
Абстрактный класс, содержащий что-то, что будет отображаться на экране. Имеет два наследника - `Button` и `TextInput`
Метод `visualize(is_active: bool)`, возвращающий форматированную строку, которая будет его визуализировать.
Метод `handle_key(key)` - обрабатывает нажатую клавишу

### Класс `Button`
Наследник класса `Widget`.
Содержит указатель на функцию `on_press` и строку `title`.
Метод `visualize(position, is_active)` просто выводит текст в нужном месте. Если `is_active == True`, то выводит его на цветном фоне.
Метод `handle_key(key)` - если был нажат Enter, вызывает `on_press`, иначе ничего не делает.

### Класс `TextInput`
Наследник класса `Widget`
Содержит строку `input`.
Метод `visualize(position, is_active)` просто выводит текст в нужном месте. Если `is_active == True`, то выводит его на цветном фоне.
Метод `handle_key(key)` - если `key` это печатный символ, добавляет его в `input`, если Backspace|Delete, убирает символ из `input`, иначе ничего не делает.


### Класс `AfterTraining`
- Экземпляр структуры `Statistics`, в котором считается статистика
- Одна кнопка с выходом в `MainMenu`.
- Метод `visualize()`, который возвращает интерфейсу статистику и кнопку выхода в меню, которая всегда активна.
- Метод `handle_key(key)`, который при нажатии на навигационные кнопки не делает ничего, иначе передает клавишу в кнопку.
- У каждой кнопки есть свой метод, который переключает состояние, а так же есть атрибут - текущая активная кнопка.

### Класс `MainMenu`
Содержит в себе несколько кнопок, которые меняют состояние, как в `AfterTraining` - выход, начать тренировку, и прочее. 
Метод `visualize()` выводит все виджеты в правильном порядке.
Метод `handle_key()`, если были нажаты стрелки влево-вправо, переключает активную кнопку, иначе передает ее в активную кнопку.

### Класс `BeforeTraining`
Как и в `AfterTraining`, содержит в себе несколько кнопок, которые меняют состояние. Также содержит виджет для выбора файла с текстом и пользователя.
Метод `visualize()` выводит все виджеты в правильном порядке.
Метод `handle_key()`, если были нажаты стрелки влево-вправо, переключает активный виджет, иначе передает его в активную кнопку.
