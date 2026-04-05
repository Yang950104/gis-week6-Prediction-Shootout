# Week 6 - 空間預測對決 (Spatial Prediction Shootout)

> GIS 應用課程 Week 6 作業：比較 Kriging、IDW、Nearest Neighbor、Random Forest 四種空間內插方法在降雨事件中的表現

---

## 專案概述

本專案針對兩個降雨事件（凱米颱風、梅雨季）進行空間預測分析，比較四種空間內插方法的差異，並產生差異地圖與不確定性分析。

### 分析事件
| 事件 | 時間 | 分析檔案 |
|------|------|----------|
| **Event 1: 凱米颱風 (Gaemi)** | 2024年7月 | `gaemi_analysis.py` |
| **Event 2: 梅雨季 (Plum Rain)** | 2024年5-6月 | `plumrain_analysis.py` |

---

## 專案結構

```
.
├── .gitignore
├── README.md
├── docs/
│   └── final_project_proposal.md    # 期末專案提案
├── notebooks/
│   ├── 01_data_preprocessing.ipynb   # 資料前處理
│   ├── 02_event1_gaemi.ipynb         # 凱米颱風分析
│   ├── 03_event2_plumrain.ipynb      # 梅雨季分析
│   ├── gaemi_analysis.py             # 凱米分析腳本
│   └── plumrain_analysis.py          # 梅雨分析腳本
└── outputs/
    ├── figures/                      # PNG 輸出圖表
    │   ├── gaemi_interpolation_2x2_comparison.png
    │   ├── gaemi_variogram_comparison.png
    │   ├── gaemi_kriging_sigma_map.png
    │   ├── gaemi_difference_kriging_rf.png
    │   └── plumrain_* (對應檔案)
    └── geotiff/                      # GeoTIFF 輸出
        ├── gaemi_kriging_rainfall.tif
        ├── gaemi_kriging_variance.tif
        └── gaemi_rf_rainfall.tif
```

---

## 內插方法比較

| 方法 | 優點 | 缺點 | 適用場景 |
|------|------|------|----------|
| **Nearest Neighbor** | 計算快速、保留原始值 | 階梯狀不連續 | 快速預覽 |
| **IDW** | 簡單直覺、平滑連續 | 受極端值影響、無誤差評估 | 一般內插 |
| **Kriging** | 最佳線性無偏估計、提供誤差圖 | 計算量大、需擬合變異函數 | 需要可靠性評估 |
| **Random Forest** | 可整合多源協變量、非線性關係 | 空間邊界生硬、無誤差資訊 | 多變量分析 |

---

## 使用方法

### 1. 環境需求
```bash
pip install numpy pandas geopandas matplotlib scipy pykrige scikit-learn rasterio
```

### 2. 執行分析

**方法一：直接在 Jupyter Notebook 執行**
```python
# 在 02_event1_gaemi.ipynb 或 03_event2_plumrain.ipynb 中執行
%run gaemi_analysis.py
```

**方法二：複製 CELL 到 Notebook**
將 `gaemi_analysis.py` 或 `plumrain_analysis.py` 中的各個 CELL 區塊複製到 Jupyter Notebook cells 中逐一執行。

**方法三：命令列執行**
```bash
cd notebooks
python gaemi_analysis.py
```

---

## 分析流程

1. **資料讀取與網格建立** - 讀取雨量站觀測資料，建立 1000m 解析度網格
2. **變異函數分析** - 擬合球狀/指數變異函數模型
3. **空間內插** - 執行 NN、IDW、Kriging、Random Forest 四種方法
4. **差異地圖** - 比較 Kriging 與 Random Forest 的預測差異
5. **不確定性分析** - 產生 Kriging Sigma Map 評估預測信心

---

## 輸出檔案說明

### 圖表 (outputs/figures/)
- `*_interpolation_2x2_comparison.png` - 四種方法比較圖
- `*_variogram_comparison.png` - 變異函數擬合比較
- `*_kriging_sigma_map.png` - Kriging 不確定性圖
- `*_difference_kriging_rf.png` - Kriging vs RF 差異圖

### 地理資料 (outputs/geotiff/)
- `gaemi_kriging_rainfall.tif` - Kriging 降雨預測結果
- `gaemi_kriging_variance.tif` - Kriging 預測變異數
- `gaemi_rf_rainfall.tif` - Random Forest 降雨預測結果

---

## 期末專案提案

本專案的期末專案提案位於 `docs/final_project_proposal.md`，主題為「都市地下停車場動態淹水預警與風險評估系統」，將結合：
- 即時雨量空間內插 (Kriging)
- 數值地形模型 (DEM)
- Google Earth Engine 遙測圖資
- Gemini SDK 智慧決策建議

---

## 資料來源

- 雨量觀測資料：中央氣象署 (CWA)
- 空間圖資：內政部地政司
- 座標系統：EPSG:3826 (TWD97)

---

## 作者

- 楊宥廷
- 林元駿
- 陳冠嘉

---

## 課程資訊

- **課程**：GIS 應用
- **作業**：Week 6 - Spatial Prediction Analysis
- **學期**：2024 春季班
