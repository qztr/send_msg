from send_msg.models import Supplier
from send_msg.timezones import Timezones
from send_msg import celery, app
import pause
from datetime import datetime, timezone


def time_to_wait(suppl_utc_bias=0, send_at_hour=10):
    """
    Возвращает: количество секунд (int)
    Принимает:
      suppl_utc_bias - временная зона получателя (int)
      send_at_hour - время в которое нужно отправить *письмо* (int)

    Вычисляем по формуле:
    h = s + 24 - t + my - adr
    s - время будущей отправки
    t - серверное время
    my - часовой пояс сервера
    adr - часовой пояс адресата
    """
    curr_time = datetime.now().hour * 60 + datetime.now().minute
    my_utc_bias = datetime.now().hour - datetime.now(timezone.utc).hour
    time_to_wait = (
        60 * (send_at_hour - suppl_utc_bias + my_utc_bias) + 24 * 60 - curr_time
    )
    return time_to_wait * 60


@celery.task
def send_msg_with_delay(utc_bias, phone):
    """
    Принимает:
      utc_bias - временная зона получателя (int)
      phone - номер получателя

    Добавляется в очередь и
    спит до наступления назначенного времени
    после чего отправляет письмо на номер
    """
    pause.minutes(time_to_wait(suppl_utc_bias=utc_bias))
    """
    ...
    ### Send msg to supplier`s number.
    Eg call func:
    send_msg(phone)
    ...
    """


@app.route("/activate_mailing", methods=["GET"])
def suppls():
    """
    Вызывает функцию добавления отправки сообщения в очередь
    для всех поставщиков, у которых действует подписка
    """
    zones = Timezones()
    all_suppliers = Supplier.query.filter(
        Supplier.subscription_cancelled.is_(False),
        Supplier.subscription_admin.is_(False),
    ).all()
    for s in all_suppliers:
        try:
            utc_bias = zones.timezones[s.district_id]
            send_msg_with_delay.delay(utc_bias, s.phone)
        except BaseException:
            pass
    return ("Mailing activated successfully!", 200)
