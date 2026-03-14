from fastapi import FastAPI, HTTPException
from typing import Dict

app = FastAPI()

# ЗАПАХ 10: Глобальна змінна замість бази даних чи репозиторію
db = []


@app.post("/process_order")
def p_o(
    data: Dict,
):  # ЗАПАХ 4: Погані назви (p_o), ЗАПАХ 9: Відсутність типізації Pydantic (Dict)
    # ЗАПАХ 6: Мертвий код
    x = 10
    debug_mode = True
    # print("Processing started")

    # ЗАПАХ 5: Глибоко вкладені умови (Arrow anti-pattern)
    if "user_id" in data:
        if data["user_id"] > 0:
            if "items" in data and len(data["items"]) > 0:
                total = 0

                # ЗАПАХ 3: Дублювання логіки та відсутність перевірки типів всередині циклу
                for i in data["items"]:
                    if "price" in i and "qty" in i:
                        if i["price"] < 0 or i["qty"] < 0:
                            raise HTTPException(
                                status_code=400, detail="Invalid item data"
                            )
                        total += i["price"] * i["qty"]
                    else:
                        raise HTTPException(status_code=400, detail="Bad item format")

                # ЗАПАХ 2: Магічні числа (1000, 0.9, 500, 0.95)
                if total > 1000:
                    total = total * 0.9
                elif total > 500:
                    total = total * 0.95

                # ЗАПАХ 8: Згустки даних (Data Clumps) - адреса передається розрізнено
                if "street" in data and "city" in data and "zip" in data:
                    shipping = 50
                    if data["city"] == "Kyiv":
                        shipping = 0

                    final_total = total + shipping

                    # ЗАПАХ 1: Великий метод (God Method) - функція робить валідацію, бізнес-логіку і збереження
                    order = {
                        "id": len(db) + 1,
                        "u_id": data["user_id"],
                        "t": final_total,
                        "s": data["street"],
                        "c": data["city"],
                        "z": data["zip"],
                    }
                    db.append(order)
                    return {
                        "status": "ok",
                        "order_id": order["id"],
                        "total": order["t"],
                    }
                else:
                    raise HTTPException(status_code=400, detail="Bad address")
            else:
                raise HTTPException(status_code=400, detail="No items")
        else:
            raise HTTPException(status_code=400, detail="Bad user")
    else:
        raise HTTPException(status_code=400, detail="No user")


@app.get("/order/{o_id}")
def g_o(o_id: int):  # Погані назви
    # ЗАПАХ 7: Неефективний пошук
    for o in db:
        if o["id"] == o_id:
            return o
    raise HTTPException(status_code=404, detail="Not found")
