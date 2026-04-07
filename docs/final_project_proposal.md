# 遙測與空間資訊之分析與應用 期末專案提案大綱

## 一、期末專案提案：臺北市地下停車場淹水風險分析

**組員**
* 陳冠嘉（D14622003）— Spatial Architect
* 林元駿（R11622028）— Data Captain
* 楊宥廷（B13501044）— AI UX Lead

## 二、研究問題
根據 CWA 即時降雨資料，分析台北市哪些區域的地下停車場因為地形和降雨的雙重風險最需要優先撤離車輛？

## 三、資料來源
1. **CWA即時降雨資料** — [O-A0002-001](https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001) — JSON
2. **內政部 20m DEM** — [政府資料開放平臺](https://data.gov.tw/dataset/176927) — GeoTIFF
3. **全臺土地利用資料** — GeoTIFF

## 四、分析方法
1. **地形水文分析 (Terrain & Hydrological Analysis)**：利用 20m DEM 計算「坡度 (Slope)」與「地形濕度指數 (TWI, Topographic Wetness Index)」，這能幫助我們識別臺北市哪些區域屬於「匯水窪地」，這類地區即使降雨量相同，地下室受災風險也顯著高於坡地。
2. **空間加權疊合 (Spatial Weighted Overlay)**：將 Kriging 產出的「即時雨量面資料」、DEM 的「低窪程度」以及土地利用中的「不透水層比例 (Impervious Surface)」進行多準則評估。建立一個地下淹水風險指標 (Underground Flood Risk Index, UFRI)，量化各區的威脅程度。

## 五、內插策略
本專案將採用 Kriging 方法進行空間插值，因為 Kriging 方法具有統計意義，可以產出不確定性等相關統計資訊，使內插數據具有可解釋性。

## 六、Gemini SDK 使用計畫
我們預計在獲取 CWA 的即時降雨資料後，將台北市的各鄉鎮市區的即時降雨資料、土地利用資料以及 20m DEM 等數據傳給 Gemini，使其分別給予相關決策建議（分析各區地下停車場的淹水風險）。

## 七、預期產出
* [ ] `main.ipynb` Jupyter Notebook
* [ ] `bsmt_flood_risk.html` Folium 互動地圖 / 分析圖表
* [ ] 互動地圖涵蓋 Gemini SDK 防災決策建議

## 八、風險評估
* **技術困難 1：API 存取與即時更新延遲**
    * **備案**：預先下載一組歷史極端降雨事件（如 2024 凱米颱風）的完整 CSV 資料集作為離線開發使用，若 API 失靈則切換為「歷史模擬模式」進行演練。
* **技術困難 2：Gemini SDK 處理空間資料量限制 (Token 限制)**
    * **備案**：先在 Python 內部完成「分區統計 (Zonal Stats)」，僅將各區的極值、平均風險、高風險網格百分比等統計指標傳遞給 Gemini，確保 AI 能在短時間內產出精準的決策摘要。