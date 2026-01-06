import flet as ft
from datetime import datetime
import json
import os
import traceback

def main(page: ft.Page):
    # 設置防護網
    try:
        # --- 1. APP 基本設定 ---
        page.title = "超級喝水管家 (萬能版)"
        page.window_width = 400
        page.window_height = 750
        page.bgcolor = "white"
        page.scroll = "auto"

        # --- 2. 智慧資料庫邏輯 (自動切換模式) ---
        STORAGE_KEY = "water_app_data"
        FILE_NAME = "water_record.json"
        today_key = datetime.now().strftime("%Y-%m-%d")

        # 偵測是否支援 client_storage (手機保險箱)
        use_client_storage = hasattr(page, "client_storage") and page.client_storage is not None

        def load_data():
            try:
                if use_client_storage:
                    # 嘗試從手機保險箱讀取
                    if page.client_storage.contains_key(STORAGE_KEY):
                        return page.client_storage.get(STORAGE_KEY)
                else:
                    # 【電腦備用方案】從 JSON 檔案讀取
                    if os.path.exists(FILE_NAME):
                        with open(FILE_NAME, "r", encoding="utf-8") as f:
                            return json.load(f)
            except Exception:
                # 如果讀取失敗，就回傳空的，不要讓程式當機
                print("讀取資料失敗，重置資料")
                pass
            return {}

        def save_data(data):
            try:
                if use_client_storage:
                    # 存入手機保險箱
                    page.client_storage.set(STORAGE_KEY, data)
                else:
                    # 【電腦備用方案】存入 JSON 檔案
                    with open(FILE_NAME, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"存檔失敗: {e}")

        # 初始化資料
        all_data = load_data()
        if today_key not in all_data:
            all_data[today_key] = []

        daily_goal = 2000

        # --- 3. UI 介面 (Emoji 版) ---
        date_text = ft.Text(f"📅 {today_key}", size=16, color="grey")
        amount_text = ft.Text("0", size=60, weight="bold", color="blue")
        status_text = ft.Text("加油！", size=18, color="orange")
        progress_bar = ft.ProgressBar(width=300, value=0, color="blue", bgcolor="#eeeeee")
        input_field = ft.TextField(label="輸入ml", width=150, text_align="center")
        history_column = ft.Column()

        # --- 4. 邏輯區 ---
        def update_ui():
            current_data = all_data.get(today_key, [])
            total = sum(item["amount"] for item in current_data)

            amount_text.value = str(total)
            
            p = total / daily_goal
            progress_bar.value = min(p, 1.0)

            if total >= daily_goal:
                status_text.value = "🎉 達標！"
                status_text.color = "green"
            else:
                diff = daily_goal - total
                status_text.value = f"還差 {diff} ml"
                status_text.color = "blue"

            history_column.controls.clear()
            
            for i, item in enumerate(reversed(current_data)):
                original_index = len(current_data) - 1 - i
                
                row = ft.Row(
                    [
                        ft.Text(item["time"], color="grey"),
                        ft.Text(f"+{item['amount']} ml", weight="bold", size=18),
                        ft.ElevatedButton(
                            "刪除", 
                            color="red",
                            bgcolor="#ffebee",
                            on_click=lambda e, idx=original_index: delete_data(idx)
                        )
                    ],
                    alignment="spaceBetween"
                )
                card = ft.Container(content=row, padding=10, bgcolor="#f0f8ff", border_radius=10)
                history_column.controls.append(card)

            page.update()

        def add_water(amount):
            now = datetime.now().strftime("%H:%M")
            if today_key not in all_data: all_data[today_key] = []
            
            all_data[today_key].append({"time": now, "amount": amount})
            save_data(all_data)
            update_ui()

        def add_custom(e):
            if not input_field.value: return
            try:
                val = int(input_field.value)
                add_water(val)
                input_field.value = ""
            except:
                pass
            page.update()

        def delete_data(index):
            if 0 <= index < len(all_data[today_key]):
                del all_data[today_key][index]
                save_data(all_data)
                update_ui()

        # --- 5. 畫面組裝 ---
        # 顯示目前的儲存模式 (偵錯用)
        mode_text = "📱 手機模式" if use_client_storage else "💻 電腦模式 (JSON)"
        
        page.add(
            ft.Column(
                [
                    ft.Text(mode_text, size=12, color="grey"),
                    ft.Text("💧", size=80),
                    date_text,
                    ft.Text("今日總水量"),
                    amount_text,
                    progress_bar,
                    status_text,
                    ft.Divider(height=20, color="transparent"),
                    
                    ft.Row(
                        [
                            ft.ElevatedButton("+100", on_click=lambda e: add_water(100)),
                            ft.ElevatedButton("+300", on_click=lambda e: add_water(300)),
                            ft.ElevatedButton("+500", on_click=lambda e: add_water(500)),
                        ], 
                        alignment="center"
                    ),
                    ft.Container(height=10),
                    
                    ft.Row(
                        [
                            input_field,
                            ft.ElevatedButton("加入", on_click=add_custom)
                        ],
                        alignment="center"
                    ),
                    ft.Divider(),
                    ft.Text("📜 歷史紀錄"),
                    history_column
                ],
                horizontal_alignment="center"
            )
        )
        
        update_ui()

    except Exception:
        # 錯誤捕捉
        error_msg = traceback.format_exc()
        page.clean()
        page.add(
            ft.Text("程式發生錯誤：", color="red", size=20, weight="bold"),
            ft.Container(
                content=ft.Text(error_msg, color="red", size=14),
                bgcolor="#ffebee",
                padding=10
            )
        )
        page.update()

ft.app(target=main)