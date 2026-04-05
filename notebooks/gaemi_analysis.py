"""
凱米颱風空間預測對決 - 完整分析腳本
Part A: 空間預測對決 (Event 1: Gaemi)

使用方式:
1. 在 Jupyter Notebook 中執行: %run gaemi_analysis.py
2. 或複製各個 CELL 區塊到 Notebook cells 中
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.interpolate import NearestNDInterpolator
from scipy.spatial.distance import cdist
from pykrige.ok import OrdinaryKriging
from pykrige.variogram_models import spherical_variogram_model, exponential_variogram_model
from sklearn.ensemble import RandomForestRegressor
import rasterio
from rasterio.transform import Affine
import os
import warnings
warnings.filterwarnings('ignore')

# 取得腳本所在目錄，確保相對路徑正確解析
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== CELL 1: 資料讀取與網格建立 ====================

print("="*60)
print("CELL 1: 資料讀取與網格建立")
print("="*60)

# 讀取 GeoJSON（使用絕對路徑避免工作目錄問題）
data_path = os.path.join(SCRIPT_DIR, "../data/processed/gaemi_rainfall.geojson")
print(f"讀取資料路徑: {os.path.abspath(data_path)}")
gdf = gpd.read_file(data_path)
print(f"讀取資料筆數: {len(gdf)}")

# 提取 X(easting), Y(northing), Z(Past1hr)
X = gdf['easting'].values
Y = gdf['northing'].values
Z = gdf['Past1hr'].values

print(f"X 範圍: {X.min():.0f} ~ {X.max():.0f}")
print(f"Y 範圍: {Y.min():.0f} ~ {Y.max():.0f}")
print(f"Z 範圍: {Z.min():.2f} ~ {Z.max():.2f} mm")

# 根據測站邊界向外延伸 5000 公尺，建立 1000m 解析度網格
buffer = 5000  # 公尺
resolution = 1000  # 公尺

x_min, x_max = X.min() - buffer, X.max() + buffer
y_min, y_max = Y.min() - buffer, Y.max() + buffer

# 建立網格
grid_x = np.arange(x_min, x_max + resolution, resolution)
grid_y = np.arange(y_min, y_max + resolution, resolution)
grid_X, grid_Y = np.meshgrid(grid_x, grid_y)

print(f"\n網格資訊:")
print(f"  X 網格點數: {len(grid_x)}")
print(f"  Y 網格點數: {len(grid_y)}")
print(f"  總網格點數: {grid_X.size}")
print(f"  解析度: {resolution}m")

# 儲存網格資訊供後續使用
cell1_data = {
    'X': X, 'Y': Y, 'Z': Z,
    'grid_x': grid_x, 'grid_y': grid_y,
    'grid_X': grid_X, 'grid_Y': grid_Y,
    'resolution': resolution, 'buffer': buffer
}

print("\n✓ CELL 1 完成\n")


# ==================== CELL 2: A1 Variogram 分析與擬合 ====================

print("="*60)
print("CELL 2: A1 Variogram 分析與擬合")
print("="*60)

# 計算實驗變異圖
from pykrige.uk import UniversalKriging

# 使用 OrdinaryKriging 計算變異圖
OK_temp = OrdinaryKriging(X, Y, Z, variogram_model='spherical', verbose=False)
lags = OK_temp.lags
semivariance = OK_temp.semivariance

print(f"實驗變異圖計算完成，共 {len(lags)} 個 lag bins")

# 擬合 Spherical 模型
OK_spherical = OrdinaryKriging(X, Y, Z, variogram_model='spherical', verbose=False)
spherical_params = OK_spherical.variogram_model_parameters

# 擬合 Exponential 模型
OK_exponential = OrdinaryKriging(X, Y, Z, variogram_model='exponential', verbose=False)
exponential_params = OK_exponential.variogram_model_parameters

print("\n擬合參數:")
print(f"  Spherical - Sill: {spherical_params[0]:.4f}, Range: {spherical_params[1]:.0f}m, Nugget: {spherical_params[2]:.4f}")
print(f"  Exponential - Sill: {exponential_params[0]:.4f}, Range: {exponential_params[1]:.0f}m, Nugget: {exponential_params[2]:.4f}")

# 繪製變異圖比較
fig, ax = plt.subplots(figsize=(10, 6))

# 實驗變異點
ax.scatter(lags, semivariance, c='black', s=30, label='Experimental Variogram', zorder=5)

# 擬合曲線
lags_fine = np.linspace(0, max(lags), 200)
spherical_curve = spherical_variogram_model(spherical_params, lags_fine)
exponential_curve = exponential_variogram_model(exponential_params, lags_fine)

ax.plot(lags_fine, spherical_curve, 'r-', linewidth=2, label=f'Spherical (R={spherical_params[1]:.0f}m)')
ax.plot(lags_fine, exponential_curve, 'b--', linewidth=2, label=f'Exponential (R={exponential_params[1]:.0f}m)')

ax.set_xlabel('Lag Distance (m)', fontsize=12)
ax.set_ylabel('Semivariance', fontsize=12)
ax.set_title('Gaemi Typhoon - Variogram Analysis', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(SCRIPT_DIR, '../outputs/figures/gaemi_variogram_comparison.png'), dpi=300, bbox_inches='tight')
plt.show()

# 選擇較佳模型 (這裡簡單選擇 Spherical，實際應根據交叉驗證)
selected_model = 'spherical'
selected_params = spherical_params

print(f"\n✓ 選定模型: {selected_model.upper()}")
print(f"  Sill: {selected_params[0]:.4f}")
print(f"  Range: {selected_params[1]:.0f} m")
print(f"  Nugget: {selected_params[2]:.4f}")
print("\n✓ CELL 2 完成\n")


cell2_data = {
    'selected_model': selected_model,
    'spherical_params': spherical_params,
    'exponential_params': exponential_params,
    'lags': lags, 'semivariance': semivariance
}


# ==================== CELL 3: A2 四種內插法實作與 2x2 比較圖 ====================

print("="*60)
print("CELL 3: A2 四種內插法實作")
print("="*60)

# 準備預測點座標 (展平網格)
points_to_predict = np.column_stack([grid_X.ravel(), grid_Y.ravel()])
training_points = np.column_stack([X, Y])

# 1. Nearest Neighbor
print("\n[1/4] Nearest Neighbor 內插...")
nn_interp = NearestNDInterpolator(training_points, Z)
Z_nn = nn_interp(points_to_predict).reshape(grid_X.shape)
print(f"  完成 - 範圍: {Z_nn.min():.2f} ~ {Z_nn.max():.2f} mm")

# 2. IDW (power=2)
print("\n[2/4] IDW (power=2) 內插...")
def idw_interpolation(points, values, grid_points, power=2):
    """IDW 內插實作"""
    distances = cdist(grid_points, points, metric='euclidean')
    # 避免除以零
    distances = np.where(distances < 1e-10, 1e-10, distances)
    weights = 1.0 / (distances ** power)
    weights_sum = np.sum(weights, axis=1)
    weighted_values = np.sum(weights * values, axis=1)
    return weighted_values / weights_sum

Z_idw = idw_interpolation(training_points, Z, points_to_predict, power=2).reshape(grid_X.shape)
print(f"  完成 - 範圍: {Z_idw.min():.2f} ~ {Z_idw.max():.2f} mm")

# 3. Ordinary Kriging
print(f"\n[3/4] Ordinary Kriging ({selected_model}) 內插...")
OK = OrdinaryKriging(X, Y, Z, variogram_model=selected_model, verbose=False)
Z_kriging, sigma_squared = OK.execute('grid', grid_x, grid_y)
Z_kriging = Z_kriging.reshape(grid_X.shape)
kriging_variance = sigma_squared.reshape(grid_X.shape)
print(f"  完成 - 範圍: {Z_kriging.min():.2f} ~ {Z_kriging.max():.2f} mm")

# 4. Random Forest
print(f"\n[4/4] Random Forest 內插...")
rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42, n_jobs=-1)
rf.fit(training_points, Z)
Z_rf = rf.predict(points_to_predict).reshape(grid_X.shape)
print(f"  完成 - 範圍: {Z_rf.min():.2f} ~ {Z_rf.max():.2f} mm")

# 繪製 2x2 比較圖
print("\n繪製 2x2 比較圖...")

# 統一 colormap 範圍
vmin = min(Z_nn.min(), Z_idw.min(), Z_kriging.min(), Z_rf.min())
vmax = max(Z_nn.max(), Z_idw.max(), Z_kriging.max(), Z_rf.max())
vmin = max(0, vmin)  # 雨量不低於 0

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# NN
im1 = axes[0, 0].imshow(Z_nn, extent=[x_min, x_max, y_min, y_max], 
                        origin='lower', cmap='viridis', vmin=vmin, vmax=vmax)
axes[0, 0].scatter(X, Y, c=Z, cmap='viridis', edgecolors='white', 
                   linewidths=0.5, s=20, vmin=vmin, vmax=vmax)
axes[0, 0].set_title('(A) Nearest Neighbor', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Easting (m)')
axes[0, 0].set_ylabel('Northing (m)')

# IDW
im2 = axes[0, 1].imshow(Z_idw, extent=[x_min, x_max, y_min, y_max], 
                        origin='lower', cmap='viridis', vmin=vmin, vmax=vmax)
axes[0, 1].scatter(X, Y, c=Z, cmap='viridis', edgecolors='white', 
                   linewidths=0.5, s=20, vmin=vmin, vmax=vmax)
axes[0, 1].set_title('(B) IDW (power=2)', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('Easting (m)')

# Kriging
im3 = axes[1, 0].imshow(Z_kriging, extent=[x_min, x_max, y_min, y_max], 
                        origin='lower', cmap='viridis', vmin=vmin, vmax=vmax)
axes[1, 0].scatter(X, Y, c=Z, cmap='viridis', edgecolors='white', 
                   linewidths=0.5, s=20, vmin=vmin, vmax=vmax)
axes[1, 0].set_title(f'(C) Ordinary Kriging ({selected_model})', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('Easting (m)')
axes[1, 0].set_ylabel('Northing (m)')

# Random Forest
im4 = axes[1, 1].imshow(Z_rf, extent=[x_min, x_max, y_min, y_max], 
                        origin='lower', cmap='viridis', vmin=vmin, vmax=vmax)
axes[1, 1].scatter(X, Y, c=Z, cmap='viridis', edgecolors='white', 
                   linewidths=0.5, s=20, vmin=vmin, vmax=vmax)
axes[1, 1].set_title('(D) Random Forest', fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('Easting (m)')

# 共用 colorbar
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
cbar = fig.colorbar(im1, cax=cbar_ax)
cbar.set_label('Rainfall (mm)', rotation=270, labelpad=20, fontsize=12)

plt.suptitle('Gaemi Typhoon - Spatial Interpolation Comparison (2x2)', 
             fontsize=14, fontweight='bold', y=0.98)
plt.savefig(os.path.join(SCRIPT_DIR, '../outputs/figures/gaemi_interpolation_2x2_comparison.png'), dpi=300, bbox_inches='tight')
plt.show()

print("✓ 2x2 比較圖已儲存")
print("\n✓ CELL 3 完成\n")

cell3_data = {
    'Z_nn': Z_nn, 'Z_idw': Z_idw, 
    'Z_kriging': Z_kriging, 'Z_rf': Z_rf,
    'kriging_variance': kriging_variance,
    'vmin': vmin, 'vmax': vmax
}


# ==================== CELL 4: A3 差異圖與不確定性分析 ====================

print("="*60)
print("CELL 4: A3 差異圖與不確定性分析")
print("="*60)

# 差異圖 (Kriging - RF)
print("\n計算 Kriging 與 RF 差異...")
diff_kriging_rf = Z_kriging - Z_rf

# 繪製差異圖
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(diff_kriging_rf, extent=[x_min, x_max, y_min, y_max], 
               origin='lower', cmap='RdBu_r')
ax.scatter(X, Y, c='black', s=10, alpha=0.5)
ax.set_xlabel('Easting (m)', fontsize=12)
ax.set_ylabel('Northing (m)', fontsize=12)
ax.set_title('Gaemi Typhoon - Difference Map (Kriging - Random Forest)', 
             fontsize=14, fontweight='bold')
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Difference (mm)', rotation=270, labelpad=20, fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(SCRIPT_DIR, '../outputs/figures/gaemi_difference_kriging_rf.png'), dpi=300, bbox_inches='tight')
plt.show()

print(f"  差異範圍: {diff_kriging_rf.min():.2f} ~ {diff_kriging_rf.max():.2f} mm")
print("  ✓ 差異圖已儲存")

# Sigma Map (Kriging Variance)
print("\n繪製 Kriging Sigma Map (不確定性地圖)...")
sigma = np.sqrt(kriging_variance)  # 標準差

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(sigma, extent=[x_min, x_max, y_min, y_max], 
               origin='lower', cmap='Blues')
ax.scatter(X, Y, c='red', s=15, edgecolors='black', linewidths=0.5, 
           label='Observation Stations')
ax.set_xlabel('Easting (m)', fontsize=12)
ax.set_ylabel('Northing (m)', fontsize=12)
ax.set_title('Gaemi Typhoon - Kriging Sigma Map (Uncertainty)', 
             fontsize=14, fontweight='bold')
ax.legend(loc='upper right')
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Sigma (mm)', rotation=270, labelpad=20, fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(SCRIPT_DIR, '../outputs/figures/gaemi_kriging_sigma_map.png'), dpi=300, bbox_inches='tight')
plt.show()

print(f"  Sigma 範圍: {sigma.min():.2f} ~ {sigma.max():.2f} mm")
print("  ✓ Sigma Map 已儲存")
print("\n✓ CELL 4 完成\n")

cell4_data = {
    'diff_kriging_rf': diff_kriging_rf,
    'sigma': sigma
}


# ==================== CELL 5: A4 GeoTIFF 網格輸出 ====================

print("="*60)
print("CELL 5: A4 GeoTIFF 網格輸出")
print("="*60)

# 確保輸出目錄存在
output_dir = os.path.join(SCRIPT_DIR, "../outputs/geotiff")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"建立輸出目錄: {output_dir}")

# 定義 CRS 與 Transform (EPSG:3826, 解析度 1000m)
crs = "EPSG:3826"
transform = Affine.translation(x_min, y_min) * Affine.scale(resolution, resolution)

print(f"\n輸出資訊:")
print(f"  CRS: {crs}")
print(f"  解析度: {resolution}m")
print(f"  網格大小: {grid_X.shape[1]} x {grid_X.shape[0]}")
print(f"  原點: ({x_min:.0f}, {y_min:.0f})")

# 準備輸出資料 (使用 np.flipud 確保 Y 軸方向正確)
Z_kriging_export = np.flipud(Z_kriging)
variance_export = np.flipud(kriging_variance)
Z_rf_export = np.flipud(Z_rf)

# 1. 輸出 Kriging Rainfall
output_path1 = os.path.join(output_dir, "gaemi_kriging_rainfall.tif")
with rasterio.open(
    output_path1,
    'w',
    driver='GTiff',
    height=Z_kriging_export.shape[0],
    width=Z_kriging_export.shape[1],
    count=1,
    dtype=Z_kriging_export.dtype,
    crs=crs,
    transform=transform,
    nodata=-9999
) as dst:
    dst.write(Z_kriging_export, 1)
print(f"\n✓ 已輸出: {output_path1}")

# 2. 輸出 Kriging Variance
output_path2 = os.path.join(output_dir, "gaemi_kriging_variance.tif")
with rasterio.open(
    output_path2,
    'w',
    driver='GTiff',
    height=variance_export.shape[0],
    width=variance_export.shape[1],
    count=1,
    dtype=variance_export.dtype,
    crs=crs,
    transform=transform,
    nodata=-9999
) as dst:
    dst.write(variance_export, 1)
print(f"✓ 已輸出: {output_path2}")

# 3. 輸出 Random Forest Rainfall
output_path3 = os.path.join(output_dir, "gaemi_rf_rainfall.tif")
with rasterio.open(
    output_path3,
    'w',
    driver='GTiff',
    height=Z_rf_export.shape[0],
    width=Z_rf_export.shape[1],
    count=1,
    dtype=Z_rf_export.dtype,
    crs=crs,
    transform=transform,
    nodata=-9999
) as dst:
    dst.write(Z_rf_export, 1)
print(f"✓ 已輸出: {output_path3}")

print("\n" + "="*60)
print("所有 GeoTIFF 輸出完成!")
print("="*60)
print("\n輸出檔案清單:")
print(f"  1. {output_path1}")
print(f"  2. {output_path2}")
print(f"  3. {output_path3}")
print("\n✓ CELL 5 完成 - 凱米颱風分析全部完成!")


# 儲存所有結果供後續使用
cell5_data = {
    'output_files': [output_path1, output_path2, output_path3]
}

# 合併所有 cell 資料
gaemi_results = {**cell1_data, **cell2_data, **cell3_data, **cell4_data, **cell5_data}
print(f"\n所有分析結果已儲存於 gaemi_results 字典中")
