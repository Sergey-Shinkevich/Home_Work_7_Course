import re
from rest_framework.serializers import ValidationError

class YouTubeValidator:
    """Валидатор для проверки того, что ссылки в материалах ведут только на youtube.com"""
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Получаем значение проверяемого поля из словаря данных
        val = value.get(self.field)
        if val:
            # Ищем все URL-адреса в тексте с помощью регулярного выражения
            urls = re.findall(r'https?://[^\s]+', val)
            for url in urls:
                # Если в ссылке нет упоминания youtube.com, выбрасываем ошибку
                if 'youtube.com' not in url:
                    raise ValidationError('Разрешены ссылки только на сторонний ресурс youtube.com.')
