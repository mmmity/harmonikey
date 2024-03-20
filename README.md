# harmonikey

A python-based application for typing practice with TUI (text user interface)

МФТИ, Практикум Python 2024, 1 курс, Б05-328, Канухин Александр

TODO: translate all below to English

## Описание

Клавиатурный тренажер - приложение для практики быстрой печати с текстовым интерфейсом (TUI).
Пользователю дается какой-то текст, загруженный из шаблонов или случайно сгенерированный. Нужно как можно быстрее набрать этот текст на клавиатуре без ошибок. 
Пользователь может видеть свои показатели (скорость набора в разных единицах измерения, количество допущенных ошибок и пр.) где-то в интерфейсе.

## Реализуемый функционал

#### Минимальный функционал
Возможность запустить тренажер на тексте, полученном откуда-то извне (может быть, захардкоженном).
Запуск тренажера: в одной части экрана показывает нужный текст, в другой поле для ввода от пользователя.
Пользователь набирает показанный ему текст с клавиатуры, тренажер не дает ему совершать ошибок. 
Как только весь текст был набран, показать время, которое было потрачено на набор. Также показать кнопки перезапуска, выхода, выбора нового текста.

#### Источники текста

1. Из отдельно данного текстового файла: перед запуском тренажера можно выбрать файл, из которого нужно загрузить текст для набора.
2. Сгенерированный, случайные слова: перед запуском тренажера можно тыкнуть флаг "случайный текст", после чего приложение сгенерирует набор слов на нужном языке (по умолчанию английский, возможно русский) из словаря. Опционально - поддержка нескольких словарей.


#### UI-фишки (опционально)
1. Вместо отдельного поля для текста и ввода сделать одно поле. Символы, введенные пользователем будут окрашиваться в другой цвет, возможно будет двигаться курсор (как сделано в [Monkeytype](https://monkeytype.com))
Позволить пользователю ошибаться, в таком случае отрисовывать символы, введенные им, поверх подсказки, но красным цветом. Позволить пользователю стирать то, что он уже ввел с помощью Backspace

2. В процессе набора текста показывать где-нибудь в углу статистику: wpm, cpm, количество ошибок. Сделать эту фичу отключаемой (статистика в любом случае будет показываться в конце)

#### Дополнительные фичи (опционально)
Переключаемые режимы:
- Бесконечно генерируемый текст и ограниченное время VS ограниченный, сгенерированный один раз либо загруженный из файла текст, и безлимитное время
- Вылетать при первой ошибке VS вообще не давать делать ошибки VS позволять ошибаться и исправлять, считая количество ошибок как доп. статистику

Создание пользователей и таблица лидеров по каждому тексту, как в рамках одного компьютера, так и глобальная, хранящаяся на сервере (похожая система лидеров реализована в [osu!](https://osu.ppy.sh))

Если что-то еще придумаю и реализую, то напишу сюда

## Архитектура

#### Класс `State`
Абстрактный класс состояния, от которого наследуются классы `MainMenu`, `BeforeTraining`, `Training`, `AfterTraining`.
Содержит ссылку на `Program`, в котором находится.
Методы:
- `visualize()` - возвращает интерфейсу, что именно нужно отрисовывать
- `handle_key(key)` - обрабатывает нажатую на клавиатуре кнопку
- `switch(State) -> State` - возвращает новое состояние

#### Класс `Program`
Содержит текущее состояние программы `State`

#### Класс `Training`
- Строка `text` и строка `input`. 
- Экземпляр структуры `Statistics`, в котором считается статистика
- Метод `handle_key(key)`, добавляет символ в `input`. Также метод проверяет, что введен правильный символ и как-то обрабатывает неправильные символы в зависимости от режима. Если текст полностью совпал с нужным, вызывает `finish()`
- Метод отрисовки `visualize()`: обрабатывает `text` и `input` и возвращает, что конкретно нужно отрисовать: это может быть просто два поля с двумя текстами, или одно поле с цветным текстом, плюс статистика
- Метод `finish()`, который меняет состояние у `Program` на `switch(AfterTraining)`, предварительно создав `AfterTraining` с посчитанной статистикой

#### Класс `AfterTraining`
- Экземпляр структуры `Statistics`, в котором считается статистика
- Метод `visualize()`, который возвращает интерфейсу кнопки перезапуска, выбора нового тренажера, выхода в меню и прочее, а так же статистику. Подсвечивает активную кнопку.
- Метод `handle_key(key)`, который при нажатии на навигационные кнопки меняет текущую выбранную кнопку, при нажатии на `Enter` применяет ее.
- У каждой кнопки есть свой метод, который переключает состояние, а так же есть атрибут - текущая активная кнопка.

#### Класс `MainMenu`
Содержит в себе несколько кнопок, которые меняют состояние, как в `AfterTraining` - выход, начать тренировку, и прочее.

#### Класс `BeforeTraining`
Как и в `AfterTraining`, содержит в себе несколько кнопок, которые меняют состояние. Также содержит виджет для выбора файла с текстом и пользователя, которые при нажатии `Enter` становится активным, деактивируется при нажатии `Escape` (в методе `handle_key(key)`). Пока он активен, все нажатые перенаправляются в него.

#### Класс `ChooseFileWidget`
Содержит текстовое поле и методы `visualize()` и `handle_key()`. Можно написать имя файла в текстовое поле, если оно активно, либо пройти по списку предлагаемых файлов. `visualize()` возвращает этот список.

В файле `main` создается экземпляр класса `Program`, события с клавиатуры перенаправляются в `Program.state`, отрисовка делается через `Program.visualize()`