from src.views import json_answer_cashback, json_answer_events, json_answer_main, json_answer_search


if __name__ == "__main__":
    json_answer_main("2018-01-11 01:03:22")
    json_answer_events("2018-01-11 01:03:22", "W")
    json_answer_cashback("2018", "3")
    json_answer_search("авиа")
    json_answer_search("cellphone")
    json_answer_search("transfer")
