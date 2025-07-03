import math

def calculate_recoil_coefficient():
    """
    計算並輸出在變更解析度與FOV設定後，用於滑鼠宏的後坐力補償係數。
    """
    print("--- PUBG 後坐力補償係數計算器 ---")
    print("請輸入您變更前後的螢幕解析度及遊戲內FOV值。")

    try:
        # 獲取使用者輸入
        old_w = int(input("請輸入【舊】螢幕寬度 (例如 1920): "))
        old_h = int(input("請輸入【舊】螢幕高度 (例如 1080): "))
        new_w = int(input("請輸入【新】螢幕寬度 (例如 2560): "))
        new_h = int(input("請輸入【新】螢幕高度 (例如 1440): "))
        fov_setting = float(input("請輸入您在遊戲中設定的FOV值 (例如 90 或 103): "))

        if old_w <= 0 or old_h <= 0 or new_w <= 0 or new_h <= 0 or fov_setting <= 0:
            print("\n錯誤：所有輸入值必須為正數。")
            return

    except ValueError:
        print("\n錯誤：輸入無效，請確保所有輸入均為數字。")
        return

    # --- 核心計算邏輯 ---

    # 1. 計算解析度變化帶來的係數
    # 係數與垂直解析度成正比
    resolution_factor = new_h / old_h

    # 2. 計算FOV變化帶來的係數
    ar_old = old_w / old_h
    ar_new = new_w / new_h

    # 如果宽高比不變，則FOV係數為1（無影響）
    if abs(ar_old - ar_new) < 0.001:
        fov_factor = 1.0
        hfov_old = fov_setting
        hfov_new = fov_setting
    else:
        # 参考宽高比 (PUBG的FOV設定基於16:9)
        ar_ref = 16.0 / 9.0

        # 將遊戲設定的HFOV（基於16:9）轉換為弧度
        hfov_ref_rad = math.radians(fov_setting)

        # 計算恆定的垂直FOV (VFOV)
        # tan(VFOV/2) = tan(HFOV_ref/2) / AR_ref
        tan_vfov_half = math.tan(hfov_ref_rad / 2) / ar_ref

        # 計算舊的實際水平FOV
        # tan(HFOV_old/2) = AR_old * tan(VFOV/2)
        tan_hfov_old_half = ar_old * tan_vfov_half
        hfov_old_rad = 2 * math.atan(tan_hfov_old_half)
        hfov_old = math.degrees(hfov_old_rad)

        # 計算新的實際水平FOV
        # tan(HFOV_new/2) = AR_new * tan(VFOV/2)
        tan_hfov_new_half = ar_new * tan_vfov_half
        hfov_new_rad = 2 * math.atan(tan_hfov_new_half)
        hfov_new = math.degrees(hfov_new_rad)

        # 後坐力體感與HFOV成反比（HFOV越小，畫面越“放大”，體感後坐力越大）
        # 因此係數為 旧HFOV / 新HFOV
        if hfov_new == 0:
            print("\n錯誤：計算出的新HFOV為0，無法計算係數。")
            return
        fov_factor = hfov_old / hfov_new

    # 3. 計算總係數
    total_coefficient = resolution_factor * fov_factor

    # --- 結果輸出 ---
    print("\n--- 計算結果 ---")
    print(f"舊解析度: {old_w}x{old_h} (宽高比: {ar_old:.2f}), 實際HFOV: {hfov_old:.2f}°")
    print(f"新解析度: {new_w}x{new_h} (宽高比: {ar_new:.2f}), 實際HFOV: {hfov_new:.2f}°")
    print("\n-------------------------------------------------")
    print(f"最終補償係數為: {total_coefficient:.4f}")
    print("-------------------------------------------------")
    print("\n使用方法:")
    print(f"【新】下壓像素 = 【舊】下壓像素 × {total_coefficient:.4f}")
    print("\n例如，如果舊設定下壓100像素，新設定下應下壓 {:.1f} 像素。".format(100 * total_coefficient))

if __name__ == "__main__":
    calculate_recoil_coefficient()
