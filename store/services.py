from django.utils import timezone

from store.models import Coupon
from user.models import User


def calculate_boost(data):
    rank_data = {
        0: {
            0: {'price': 300, 'time': 2},
            1: {'price': 300, 'time': 2},
            2: {'price': 300, 'time': 2},
            3: {'price': 300, 'time': 2},
        },
        1: {
            0: {'price': 400, 'time': 2},
            1: {'price': 400, 'time': 2},
            2: {'price': 400, 'time': 2},
            3: {'price': 400, 'time': 2},
        },
        2: {
            0: {'price': 500, 'time': 2},
            1: {'price': 500, 'time': 2},
            2: {'price': 500, 'time': 2},
            3: {'price': 500, 'time': 2},
        },
        3: {
            0: {'price': 600, 'time': 3},
            1: {'price': 600, 'time': 3},
            2: {'price': 600, 'time': 3},
            3: {'price': 600, 'time': 3},
        },
        4: {
            0: {'price': 800, 'time': 5},
            1: {'price': 800, 'time': 5},
            2: {'price': 800, 'time': 5},
            3: {'price': 800, 'time': 5},
        },
        5: {
            0: {'price': 1100, 'time': 7},
            1: {'price': 1100, 'time': 7},
            2: {'price': 1100, 'time': 7},
            3: {'price': 1100, 'time': 7},
        },
        6: {
            0: {'price': 2000, 'time': 7},
            1: {'price': 2000, 'time': 7},
            2: {'price': 2000, 'time': 7},
            3: {'price': 2000, 'time': 7},
        },
        7: {3: {'price': 5000, 'time': 15}},
        8: {3: {'price': 10000, 'time': 15}},
    }

    # server_data = {
    #     1 : 1,
    #     0 : 0.8,
    # }

    price = 0
    time = 0

    current_position = int(data['current_position'])
    desired_position = int(data['desired_position'])
    current_division = int(data['current_division'])
    desired_division = int(data['desired_division'])
    if 'coupon_code' in data:
        coupon = data['coupon_code']
    # print('-----', current_position, current_division, desired_position, desired_division)

    while (current_position, current_division) != (desired_position, desired_division):
        # print(current_position, current_division, desired_position, desired_division)
        price += rank_data[current_position][current_division]['price']
        time += rank_data[current_position][current_division]['time']

        if current_division != 0 and current_position != 7:
            current_division -= 1
        else:
            if current_position == 7 and desired_position == 8:
                current_position += 1
                price += rank_data[current_position][current_division]['price']
                time += rank_data[current_position][current_division]['time']
                break
            if current_position == 6 and desired_position == 7:
                current_position += 1
                current_division = max(rank_data[current_position].keys())
                price += rank_data[current_position][current_division]['price']
                time += rank_data[current_position][current_division]['time']
                break

            current_position += 1
            current_division = max(rank_data[current_position].keys())
    # server = (float(data['server']))
    price = int(price * float(data['server']) * float(data['lp_per_win']))

    if data['duo_booster']:
        price *= 1.3

    if data['specific_role']:
        price *= 1.2

    if data.get('coupon_code'):
        price = price - (price * coupon.sale) / 100
    print(round(price), time)
    return round(price)


def calculate_qualification(data):
    price_rank = {
        0: {'price': 160},  # unranked
        1: {'price': 160},  # iron
        2: {'price': 160},  # bronze
        3: {'price': 180},  # silver
        4: {'price': 200},  # gold
        5: {'price': 220},  # platina
        6: {'price': 250},  # emerald
        7: {'price': 280},  # diamond
        8: {'price': 300},  # master
        9: {'price': 350},  # grandmaster
    }
    price = 0

    previous_position = int(data['previous_position'])
    game_count = int(data['game_count'])
    if 'coupon_code' in data:
        coupon = data['coupon_code']

    price = price_rank[previous_position]['price'] * game_count

    if data['duo_booster']:
        price *= 1.3

    if data['specific_role']:
        price *= 1.2

    if data.get('coupon_code'):
        price = price - (price * coupon.sale) / 100
    if data['server'] == '0.8':
        price *= 0.8
    print('прайс---', int(price), price)
    return round(price)


def check_coupon(name: str, user: User) -> tuple[bool, str, int]:
    """Проверяет может ли пользователь применить купон"""
    coupon = Coupon.objects.filter(name=name)

    if not coupon.exists():
        return False, 'Купон не найден', 0

    coupon = coupon.last()

    user_coupons = user.qualification_orders.all().values('coupon_code')
    if any(coupon.id == next(iter(i.values())) for i in user_coupons):
        return False, 'Купон уже был использован', 0

    user_coupons1 = user.boost_orders.all().values('coupon_code')
    if any(coupon.id == next(iter(i.values())) for i in user_coupons1):
        return False, 'Купон уже был использован', 0

    if coupon.is_active and coupon.count > 0 and coupon.end_date > timezone.now():
        return True, 'Купон успешно применен', coupon.sale
    return False, 'Купон недействителен или закончился', 0
