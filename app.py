import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 임시 저장 공간
# 나중에는 DB로 바꿀 수 있음
saved_user = None
saved_drinks = []


def classify_user_type(diseases):
    """선택한 항목에 따라 사용자 타입 문장 만들기"""
    if not diseases:
        return "일반 사용자"

    type_map = {
        "diabetes": "당류 섭취 주의",
        "hyperlipidemia": "지방·당류 섭취 주의",
        "cirrhosis": "카페인·당류 섭취 주의",
        "heart_failure": "수분 섭취량 조절 주의",
    }

    selected_types = [type_map[d] for d in diseases if d in type_map]
    return ", ".join(selected_types)


def calculate_recommended_water(weight):
    """
    프로젝트 기준 권장 음수량 계산식
    몸무게 * 30 * 1/2
    """
    return int(weight * 30 * 0.5)


@app.route("/", methods=["GET", "POST"])
def index():
    global saved_user, saved_drinks

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        weight = float(request.form.get("weight"))
        diseases = request.form.getlist("disease")

        recommended_water = calculate_recommended_water(weight)
        user_type = classify_user_type(diseases)

        # 자주 마시는 음료 여러 개 받기
        drink_names = request.form.getlist("drink_name")
        drink_amounts = request.form.getlist("drink_amount")
        drink_caffeines = request.form.getlist("drink_caffeine")
        drink_sugars = request.form.getlist("drink_sugar")
        
        

        saved_drinks = []

        for i in range(len(drink_names)):
            if drink_names[i].strip() == "":
                continue

            drink = {
                "name": drink_names[i],
                "amount": drink_amounts[i] if drink_amounts[i] else "0",
                "caffeine": drink_caffeines[i] if drink_caffeines[i] else "0",
                "sugar": drink_sugars[i] if drink_sugars[i] else "0",
                
                
            }
            saved_drinks.append(drink)

        saved_user = {
            "name": name,
            "age": age,
            "weight": weight,
            "diseases": diseases,
            "user_type": user_type,
            "recommended_water": recommended_water
        }

    if saved_user:
        return redirect(url_for("dashboard"))

    return render_template(
    "index.html",
    user=saved_user,
    drinks=saved_drinks
)

@app.route("/dashboard")
def dashboard():

    global saved_user
    global saved_drinks

    if saved_user is None:
        return redirect(url_for("index"))

    # -----------------------
    # 임시 데이터
    # 나중에는 센서에서 받아올 예정
    # -----------------------

    today_water = 1600
    caffeine = 120
    sugar = 18

    goal = saved_user["recommended_water"]

    percent = int(today_water / goal * 100)

    if percent > 100:
        percent = 100

    remain = max(goal - today_water, 0)

    return render_template(
        "dashboard.html",
        user=saved_user,
        drinks=saved_drinks,
        today_water=today_water,
        goal=goal,
        percent=percent,
        remain=remain,
        caffeine=caffeine,
        sugar=sugar
    )
    
import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )