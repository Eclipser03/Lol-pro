LOGGING = {
    'version': 1,  # Версия конфигурации логирования
    'disable_existing_loggers': False,  # Не отключать существующие логгеры
    'formatters': {  # Формат вывода логов
        'main_format': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {  # Обработчики логов (куда отправлять логи)
        'console': {
            'level': 'INFO',  # Уровень логов
            'class': 'logging.StreamHandler',  # Выводить логи в консоль
            'formatter': 'main_format',
        },
    },
    'loggers': {  # Логгеры для разных частей приложения
        'main': {  # Логгер для вашего приложения
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
