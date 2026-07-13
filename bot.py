from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters


# =========================
# 1. 텔레그램 봇 토큰
# =========================
# 실제 토큰은 공개 채팅, 발표자료, 깃허브에 올리면 안 됩니다.
TOKEN = "8746270836:AAG_wac0YY-wLmNHTG2LpDO3uT3vktJva_Q"


# =========================
# 2. 웹페이지 주소
# =========================
# 나중에 실제 웹사이트 배포 주소로 바꾸면 됩니다.
WEB_URL = "http://127.0.0.1:5000"


# =========================
# 3. 가상 데이터
# =========================
# 아직 로드셀/OCR/웹캠이 완성되지 않았으므로 테스트용 임시 데이터 사용

user_name = "사용자"

target_water = 1200          # 하루 목표 음수량 ml
water_today = 650            # 오늘 누적 음수량 ml

sugar_limit = 50             # 하루 당류 기준 g
sugar_today = 42             # 오늘 누적 당류 g

caffeine_limit = 300         # 하루 카페인 기준 mg
caffeine_today = 210         # 오늘 누적 카페인 mg

last_drink_minutes = 130     # 마지막 음수 후 지난 시간, 분 단위

# 자동 알림 중복 방지용 변수
sent_50_alert = False
sent_70_alert = False
sent_100_alert = False
sent_afternoon_low_alert = False

recent_logs = [
    {
        "time": "09:10",
        "drink": "물",
        "amount": 200,
        "sugar": 0,
        "caffeine": 0,
        "source": "로드셀 측정"
    },
    {
        "time": "11:30",
        "drink": "믹스커피",
        "amount": 100,
        "sugar": 6,
        "caffeine": 50,
        "source": "즐겨찾기 버튼"
    },
    {
        "time": "14:20",
        "drink": "카페라떼",
        "amount": 350,
        "sugar": 36,
        "caffeine": 160,
        "source": "OCR 인식"
    }
]


# =========================
# 4. 기본 계산 함수
# =========================

def calculate_rate(value, limit):
    """기준값 대비 퍼센트 계산"""
    if limit == 0:
        return 0
    return int(value / limit * 100)


def get_water_rate():
    """오늘 음수량 달성률"""
    return calculate_rate(water_today, target_water)


def get_sugar_rate():
    """오늘 당류 기준 대비 비율"""
    return calculate_rate(sugar_today, sugar_limit)


def get_caffeine_rate():
    """오늘 카페인 기준 대비 비율"""
    return calculate_rate(caffeine_today, caffeine_limit)


def get_water_emoji(rate):
    """수분 달성률 이모지"""
    if rate >= 100:
        return "🎉"
    elif rate >= 71:
        return "🟢"
    elif rate >= 51:
        return "🟡"
    else:
        return "🔴"


def get_ingredient_emoji(rate):
    """당류/카페인 상태 이모지"""
    if rate >= 90:
        return "🔴"
    elif rate >= 70:
        return "🟡"
    else:
        return "🟢"


# =========================
# 5. 버튼 조회용 메시지
# =========================

def make_water_message():
    rate = get_water_rate()

    if rate <= 30:
        status = "🔴 매우 부족"
        comment = "오늘 수분 섭취량이 많이 부족해요. 지금은 물을 우선적으로 마시는 것이 좋습니다."
    elif rate <= 50:
        status = "🔴 부족"
        comment = "현재 수분 섭취량이 부족해요. 다음 음료는 물을 추천합니다."
    elif rate <= 70:
        status = "🟡 주의"
        comment = "목표량에 가까워지고 있어요. 조금만 더 마시면 안정적인 상태에 도달할 수 있습니다."
    elif rate <= 100:
        status = "🟢 양호"
        comment = "좋아요! 오늘 수분 섭취가 비교적 안정적으로 이루어지고 있습니다."
    else:
        status = "🎉 목표 달성"
        comment = "오늘 목표 음수량을 달성했어요. 과하게 마시기보다는 일정한 간격을 유지해보세요."

    return (
        "💧 오늘 음수량\n\n"
        f"현재 음수량: {water_today}ml\n"
        f"목표 음수량: {target_water}ml\n"
        f"달성률: {rate}%\n"
        f"상태: {status}\n\n"
        f"{comment}"
    )


def make_sugar_message():
    rate = get_sugar_rate()

    if rate >= 90:
        status = "🔴 위험"
        comment = "당류 섭취량이 높은 편이에요. 다음 음료는 물이나 무가당 음료를 추천합니다."
    elif rate >= 70:
        status = "🟡 주의"
        comment = "당류 섭취량이 기준에 가까워지고 있어요. 단 음료 섭취에 주의해주세요."
    else:
        status = "🟢 안정"
        comment = "현재 당류 섭취 상태는 안정적인 편입니다."

    return (
        "🍬 오늘 당류\n\n"
        f"오늘 섭취 당류: {sugar_today}g\n"
        f"기준 당류: {sugar_limit}g\n"
        f"기준 대비: {rate}%\n"
        f"상태: {status}\n\n"
        f"{comment}"
    )


def make_caffeine_message():
    rate = get_caffeine_rate()

    if rate >= 90:
        status = "🔴 위험"
        comment = "카페인 섭취량이 높은 편이에요. 오늘은 커피나 에너지드링크 섭취를 줄이는 것이 좋습니다."
    elif rate >= 70:
        status = "🟡 주의"
        comment = "카페인 섭취량이 기준에 가까워지고 있어요. 다음 음료는 카페인이 없는 음료를 추천합니다."
    else:
        status = "🟢 안정"
        comment = "현재 카페인 섭취 상태는 안정적인 편입니다."

    return (
        "☕ 오늘 카페인\n\n"
        f"오늘 섭취 카페인: {caffeine_today}mg\n"
        f"기준 카페인: {caffeine_limit}mg\n"
        f"기준 대비: {rate}%\n"
        f"상태: {status}\n\n"
        f"{comment}"
    )


def make_recent_logs_message():
    text = "📈 오늘 통계 / 최근 음수 기록\n\n"

    for log in recent_logs:
        text += f"• {log['time']} / {log['drink']} / {log['amount']}ml\n"
        text += f"  당류 {log['sugar']}g, 카페인 {log['caffeine']}mg\n"
        text += f"  기록 방식: {log['source']}\n\n"

    return text


def make_no_drink_check_message():
    rate = get_water_rate()

    if last_drink_minutes >= 120:
        return (
            "⏰ 미섭취 상태 확인\n\n"
            f"마지막 음수 이후 약 {last_drink_minutes}분이 지났어요.\n"
            "오랜 시간 동안 음료를 마시지 않았습니다.\n\n"
            f"현재 음수량: {water_today}ml\n"
            f"목표 음수량: {target_water}ml\n"
            f"현재 달성률: {rate}%\n\n"
            "지금 물 한 잔을 마셔보는 건 어떨까요?"
        )

    return (
        "⏰ 미섭취 상태 확인\n\n"
        f"마지막 음수 이후 약 {last_drink_minutes}분이 지났어요.\n"
        f"현재 달성률: {rate}%\n\n"
        "아직은 추가 알림이 필요한 상태는 아닙니다."
    )


# =========================
# 6. 간결한 하루 평가
# =========================
# 하루 평가와 밤 평가를 통합한 최종 형태

def make_daily_summary_message():
    water_rate = get_water_rate()
    sugar_rate = get_sugar_rate()
    caffeine_rate = get_caffeine_rate()

    water_emoji = get_water_emoji(water_rate)
    sugar_emoji = get_ingredient_emoji(sugar_rate)
    caffeine_emoji = get_ingredient_emoji(caffeine_rate)

    if sugar_rate >= 90 and caffeine_rate >= 90:
        comment = "오늘은 당류와 카페인 섭취가 모두 높은 편이었어요. 내일은 물이나 무가당 음료를 선택해보세요."
    elif water_rate < 50:
        comment = "오늘은 수분 섭취가 부족한 편이었어요. 내일은 조금 더 자주 마셔보세요."
    elif water_rate >= 100 and sugar_rate < 70 and caffeine_rate < 70:
        comment = "오늘 목표 음수량을 달성했어요. 좋은 음수 습관을 잘 유지하고 있어요."
    elif water_rate >= 100 and caffeine_rate >= 70:
        comment = "오늘 목표 음수량은 달성했지만, 카페인 섭취가 높은 편이에요. 내일은 카페인 없는 음료를 선택해보세요."
    elif water_rate >= 100 and sugar_rate >= 70:
        comment = "오늘 목표 음수량은 달성했지만, 당류 섭취가 높은 편이에요. 내일은 단 음료를 조금 줄여보세요."
    elif sugar_rate >= 70:
        comment = "수분 섭취는 괜찮았지만, 당류 섭취가 높은 편이라 단 음료를 줄이면 좋아요."
    elif caffeine_rate >= 70:
        comment = "수분 섭취는 괜찮았지만, 카페인 섭취가 높은 편이라 내일은 카페인 없는 음료를 추천해요."
    else:
        comment = "오늘은 수분과 성분 섭취가 전반적으로 안정적이었어요."

    return (
        "📝 오늘의 음수 평가\n\n"
        f"💧 수분 달성률: {water_rate}% {water_emoji}\n"
        f"🍬 당류 섭취 상태: {sugar_rate}% {sugar_emoji}\n"
        f"☕ 카페인 섭취 상태: {caffeine_rate}% {caffeine_emoji}\n\n"
        f"{comment}"
    )


# =========================
# 7. 자동 알림용 메시지 함수
# =========================

def make_auto_no_drink_alert_message():
    rate = get_water_rate()

    if rate <= 50:
        return (
            "💧 수분 섭취 알림\n\n"
            f"마지막 음수 이후 약 {last_drink_minutes}분이 지났어요.\n"
            f"현재 목표 달성률도 {rate}%로 낮은 편입니다.\n\n"
            f"현재 음수량: {water_today}ml\n"
            f"목표 음수량: {target_water}ml\n\n"
            "오늘 수분 섭취가 부족할 수 있어요.\n"
            "지금은 물을 우선적으로 마시는 것을 추천합니다."
        )

    elif rate >= 70:
        return (
            "💧 수분 섭취 간격 알림\n\n"
            f"마지막 음수 이후 약 {last_drink_minutes}분이 지났어요.\n\n"
            f"현재 음수량: {water_today}ml\n"
            f"목표 음수량: {target_water}ml\n"
            f"현재 달성률: {rate}%\n\n"
            "오늘 전체 음수량은 비교적 괜찮지만,\n"
            "너무 긴 간격보다는 조금씩 나누어 마시는 것이 좋습니다."
        )

    return (
        "💧 수분 섭취 알림\n\n"
        f"마지막 음수 이후 약 {last_drink_minutes}분이 지났어요.\n"
        "오랜 시간 동안 음료를 마시지 않았습니다.\n\n"
        f"현재 음수량: {water_today}ml\n"
        f"목표 음수량: {target_water}ml\n"
        f"현재 달성률: {rate}%\n\n"
        "지금 물 한 잔을 마셔보는 건 어떨까요?"
    )


def make_50_percent_alert_message():
    rate = get_water_rate()

    return (
        "💧 오늘 목표의 절반을 달성했어요!\n\n"
        f"현재 음수량: {water_today}ml\n"
        f"목표 음수량: {target_water}ml\n"
        f"달성률: {rate}%\n\n"
        "좋아요. 오늘 음수 목표의 절반 이상을 채웠어요.\n"
        "남은 시간 동안 조금씩 나누어 마셔보세요."
    )


def make_70_percent_alert_message():
    rate = get_water_rate()

    return (
        "💧 목표에 가까워지고 있어요!\n\n"
        f"현재 음수량: {water_today}ml\n"
        f"목표 음수량: {target_water}ml\n"
        f"달성률: {rate}%\n\n"
        "이제 목표량에 꽤 가까워졌어요.\n"
        "조금만 더 유지하면 오늘 목표를 달성할 수 있습니다."
    )


def make_100_percent_alert_message():
    return (
        "🎉 오늘 목표 음수량 달성!\n\n"
        f"현재 음수량: {water_today}ml\n"
        f"목표 음수량: {target_water}ml\n\n"
        "좋아요! 오늘 목표 음수량을 달성했어요.\n"
        "꾸준한 음수 습관을 잘 유지하고 있습니다."
    )


def make_afternoon_low_alert_message():
    rate = get_water_rate()

    return (
        "⚠️ 오늘 수분 섭취가 부족해요\n\n"
        f"현재 음수량: {water_today}ml\n"
        f"목표 음수량: {target_water}ml\n"
        f"달성률: {rate}%\n\n"
        "하루가 많이 지났지만 아직 목표량의 절반에 도달하지 못했어요.\n"
        "남은 시간 동안 물을 조금씩 나누어 마셔보세요."
    )


def make_once_caffeine_alert(drink_name, caffeine_amount):
    if caffeine_amount >= 150:
        return (
            "☕ 카페인 단일 섭취 경고\n\n"
            f"방금 기록된 음료: {drink_name}\n"
            f"카페인 함량: {caffeine_amount}mg\n\n"
            "한 번에 섭취한 카페인 양이 높은 편이에요.\n"
            "이후에는 카페인이 적은 음료를 선택하는 것이 좋습니다."
        )

    return None


# =========================
# 8. 자동 알림 조건 테스트
# =========================

def check_auto_alert_conditions():
    global sent_50_alert, sent_70_alert, sent_100_alert, sent_afternoon_low_alert

    alerts = []
    rate = get_water_rate()

    if last_drink_minutes >= 120:
        alerts.append(make_auto_no_drink_alert_message())

    if rate >= 50 and not sent_50_alert:
        alerts.append(make_50_percent_alert_message())
        sent_50_alert = True

    if rate >= 70 and not sent_70_alert:
        alerts.append(make_70_percent_alert_message())
        sent_70_alert = True

    if rate >= 100 and not sent_100_alert:
        alerts.append(make_100_percent_alert_message())
        sent_100_alert = True

    # 실제 자동 알림 연결 시 사용
    # if current_hour >= 17 and rate < 50 and not sent_afternoon_low_alert:
    #     alerts.append(make_afternoon_low_alert_message())
    #     sent_afternoon_low_alert = True

    return alerts


def make_auto_alert_test_message():
    alerts = check_auto_alert_conditions()

    if not alerts:
        return (
            "✅ 자동 알림 조건 테스트\n\n"
            "현재 가상 데이터 기준으로 자동 발송이 필요한 알림은 없습니다."
        )

    text = "🔔 자동 알림 조건 테스트\n\n"
    text += "현재 가상 데이터 기준으로 아래 알림이 발송될 수 있습니다.\n\n"

    for index, alert in enumerate(alerts, start=1):
        text += f"[알림 {index}]\n{alert}\n\n"

    return text


# =========================
# 9. 하단 키보드 메뉴
# =========================
# 설정 버튼 제거 버전

keyboard = [
    ["💧 오늘 음수량", "🍬 오늘 당류"],
    ["☕ 오늘 카페인", "📈 오늘 통계"],
    ["🌐 웹페이지", "⏰ 미섭취 확인"],
    ["📝 하루 평가", "🔔 자동 알림 테스트"]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)


# =========================
# 10. 텔레그램 명령어/버튼 처리
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "안녕하세요!\n"
        "잘마시조 스마트 컵받침 알림 봇입니다 😊\n\n"
        "아래 버튼을 눌러 오늘의 음수 상태를 확인할 수 있어요."
    )

    await update.message.reply_text(message, reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💧 오늘 음수량":
        await update.message.reply_text(make_water_message(), reply_markup=reply_markup)

    elif text == "🍬 오늘 당류":
        await update.message.reply_text(make_sugar_message(), reply_markup=reply_markup)

    elif text == "☕ 오늘 카페인":
        await update.message.reply_text(make_caffeine_message(), reply_markup=reply_markup)

    elif text == "📈 오늘 통계":
        await update.message.reply_text(make_recent_logs_message(), reply_markup=reply_markup)

    elif text == "🌐 웹페이지":
        web_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("잘마시조 웹페이지 열기", url=WEB_URL)]
        ])

        await update.message.reply_text(
            "아래 버튼을 누르면 잘마시조 웹페이지로 이동할 수 있습니다.",
            reply_markup=web_button
        )

    elif text == "⏰ 미섭취 확인":
        await update.message.reply_text(make_no_drink_check_message(), reply_markup=reply_markup)

    elif text == "📝 하루 평가":
        await update.message.reply_text(make_daily_summary_message(), reply_markup=reply_markup)

    elif text == "🔔 자동 알림 테스트":
        await update.message.reply_text(make_auto_alert_test_message(), reply_markup=reply_markup)

    else:
        await update.message.reply_text(
            "아래 버튼 중 하나를 선택해주세요.",
            reply_markup=reply_markup
        )


# =========================
# 11. 봇 실행
# =========================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("잘마시조 통합 텔레그램 봇 실행 중!")
    app.run_polling()


if __name__ == "__main__":
    main()