# JKDEV NEWS SERVER


## Модель пользователя
```python
class User:
    login = ""
    pwd = ""
    mail = ""
    telegram = ""
    subscriptions = {"vk": [], "instagram": []}
```


## Общая структура запроса

`GET '/<login>/<method>?<query>'`
*Да-да, везде используются только GET-запросы*

**login** - обращение к пользователю осуществляется по его логину
**method** - метод, который необходимо применить к данному пользователю
**query** - список параметров

## /register
#### Параметры:

**pwd** - хэш пароля `обязательно`
**mail** - почта юзера `необязательно`
**telegram** - телеграм юзера `необязательно`

>**Внимание!!!** Передавать гет-запросом необходимо не сам пароль, а его хеш!!!

Пример запроса: `GET /testUser/register?pwd=HASHOFPWD&mail=testUser@jkdev.ru`

**Варианты ответа:**

`{"code": 406, "description": "Username already taken"}`

`{"code": 200, "description": "Registration success"}`

## /addSubscription

**multiple** - переключатель алгоритма работы метода (см. дальше)
**source** - источник новостей *(вк, инстаграм и др)*
**subscriptions** - список в формате JSON, либо одна подписка

#### Multiple

> Если в строке запроса указан параметр `multiple=<any value>`, то сервер будет ждать json-список подписок
> Если в строке запроса **отсутствует** параметр `multiple`, сервер ожидает одну подписку

Примеры запроса:
`/testUser/addSubscription?source=instagram&subscriptions=instagram.com/tvoye_litso`
`/testUser/addSubscription?multiple=true&source=vk&subscriptions=["vk.com/dev", "vk.com/community", "vk.com/gohome"]`

**Ответ:**

Если повезёт, сервер выдаст ответ `{"code": 200, "description": "Success adding subscriptions"}`

## /deleteSubscription

*Работает по той же логике, что и **/addSubscription**, но удаляет полученные подписки*

**Ответ:**

*Всё хорошо*: 
`{"code": 200, "description": "Success deleting subscriptions"}`
*Категории подписок (параметр source) для данного пользователя не существует*:
`{"code": 404, "description": "Source not found"}`
*Пользователь не был подписан на данный ресурс:*
`{"code": 404, "description": "Subscription not found"}`