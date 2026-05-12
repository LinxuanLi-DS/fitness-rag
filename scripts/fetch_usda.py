import os
import json
import pandas as pd
from tqdm import tqdm

DATA_DIR = "data/raw/usda/FoodData_Central_foundation_food_csv_2026-04-30"
OUTPUT_FILE = "data/raw/usda/foods.json"

# 我们关心的营养素
TARGET_NUTRIENTS = {
    "Energy (Atwater General Factors)",
    "Protein",
    "Total lipid (fat)",
    "Carbohydrate, by difference",
    "Fiber, total dietary",
    "Sugars, Total",
    "Sodium, Na",
}

def main():
    print("读取 CSV 文件...")
    foods_df = pd.read_csv(f"{DATA_DIR}/food.csv")
    nutrients_df = pd.read_csv(f"{DATA_DIR}/nutrient.csv")
    food_nutrient_df = pd.read_csv(f"{DATA_DIR}/food_nutrient.csv")

    print(f"食物总数: {len(foods_df)}")

    # 只保留我们关心的营养素
    target_ids = nutrients_df[nutrients_df["name"].isin(TARGET_NUTRIENTS)][["id", "name", "unit_name"]]
    merged = food_nutrient_df.merge(target_ids, left_on="nutrient_id", right_on="id")

    # 按食物 ID 分组营养数据
    print("整理营养数据...")
    nutrient_map = {}
    for _, row in tqdm(merged.iterrows(), total=len(merged)):
        fdc_id = row["fdc_id"]
        if fdc_id not in nutrient_map:
            nutrient_map[fdc_id] = {}
        nutrient_map[fdc_id][row["name"]] = f"{row['amount']} {row['unit_name']}"

    # 组合成最终结果
    print("组合数据...")
    all_foods = []
    for _, food in tqdm(foods_df.iterrows(), total=len(foods_df)):
        fdc_id = food["fdc_id"]
        record = {
            "fdc_id": int(fdc_id),
            "name": food["description"],
            "category": food.get("food_category_id", ""),
            "nutrients": nutrient_map.get(fdc_id, {})
        }
        all_foods.append(record)

    # 保存
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_foods, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 完成！共 {len(all_foods)} 条食物数据")
    print(f"保存至 {OUTPUT_FILE}")
    print(f"\n示例数据：")
    for food in all_foods[:3]:
        if food["nutrients"]:
            print(json.dumps(food, indent=2, ensure_ascii=False))
            break

if __name__ == "__main__":
    main()