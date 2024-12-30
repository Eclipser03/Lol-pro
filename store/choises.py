from django.db import models


class RankChoices(models.TextChoices):
    IRON = 'IRON', 'Железо'
    BRONZE = 'BRONZE', 'Бронза'
    SILVER = 'SILVER', 'Серебро'
    GOLD = 'GOLD', 'Голд'
    PLATINUM = 'PLATINUM', 'Платина'
    EMERALD = 'EMERALD', 'Эмеральд'
    DIAMOND = 'DIAMOND', 'Даймонд'
    MASTER = 'MASTER', 'Мастер'
    GRANDMASTER = 'GRANDMASTER', 'Грандмастер'


class DivisionChoices(models.TextChoices):
    DIVISION_1 = 'DIVISION 1', 'Дивизион 1'
    DIVISION_2 = 'DIVISION 2', 'Дивизион 2'
    DIVISION_3 = 'DIVISION 3', 'Дивизион 3'
    DIVISION_4 = 'DIVISION 4', 'Дивизион 4'


class CurrentLPChoices(models.TextChoices):
    LP_0_20 = '0-20LP', '0-20LP'
    LP_21_40 = '21-40LP', '21-40LP'
    LP_41_60 = '41-60LP', '41-60LP'
    LP_61_80 = '61-80LP', '61-80LP'
    LP_81_99 = '81-99LP', '81-99LP'


class LPPerWinChoices(models.TextChoices):
    LP_18_PLUS = '18+LP', '18+ LP'
    LP_15_17 = '15-17LP', '15-17 LP'
    LP_LESS_15 = '<15LP', '<15LP'


class ServerChoices(models.TextChoices):
    EU_WEST = 'EU WEST', 'Вест'
    RUSSIA = 'RUSSIA', 'Россия'


class QueueChoices(models.TextChoices):
    SOLO_DUO = 'SOLO/DUO', 'Соло-дуо'
    FLEX = 'FLEX', 'Флекс'
