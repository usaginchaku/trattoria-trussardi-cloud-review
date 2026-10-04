COORD12-LAMP05 Straight L1 の壁への食い込みだけを直す造形候補 C1(Claude cloud、2026-10-04 JST)
最終候補は revision02/ の 1 組だけ(revision02/models/StraightLamp_ARCH01_C1.blend と revision02/fbx/StraightLamp_ARCH01_C1.fbx、同梱の revision02/fbx/Shade_ARCH01.png)。
採用はしていない。数値の PASS だけで採用や完成扱いにはしない。

■ 入力(読み取りのみ。SHA 一致を確認)
assets/claude-props/coord09-20261003/furniture/lamp_shade/L1/ の次の 3 件:
- models/StraightLamp_ARCH01.blend 6ed3f6d3…
- fbx/StraightLamp_ARCH01.fbx 60dfa698…
- fbx/Shade_ARCH01.png ea737420…
L0 / L2、原作の画素、Unity、履歴は扱っていない。

■ 変更(要因は 1 つ: 取付け板に対する、カップ一式の壁からの距離)
- 動かした部品(位置だけ):
  - カラー/ソケット(122 頂点)、シェード(706)、diffuser(146)を Y 方向に -0.050 m(室内側へ)平行移動した。
  - 接続の腕(96 頂点の角丸の柱)は、前側の 48 頂点(y ≤ -0.060)だけを同じ -0.050 m 動かして延長した。奥行きは 0.050 → 0.100 m。
- 保持したもの:
  - 腕の背面側の 48 頂点。腕の高さ z 0.035〜0.205 と、幅 x ±0.0155。
  - 取付け板(96 頂点): 位置、形、寸法、背面 Y=0 は完全に同じ(差 0)。
- 結果:
  - 板以外で最も奥(+Y)にある点の Y: +0.044 → -0.006 m(シェードの最奥)。
  - Y>0 の頂点の数: シェード 151 → 0、diffuser 23 → 0。blend の頂点数で数えた値。Unity の 299 頂点は、UV や法線で分割された後の数。
- 接続の実測:
  - 腕の背面 y=-0.015 は、板の前面 y=-0.028 より奥にあり、板に 13 mm 重なる(元と同じ)。
  - 腕の前面 y=-0.115 は、新しいカラーの中心 y=-0.117 付近にある。元は前面 -0.065 と中心 -0.067 で、同じ関係を保っている。
  - カラーは y -0.170〜-0.064、z 0.145〜0.190。腕は z 0.035〜0.205 で、カラーを貫く関係は元と同じ。
  - シェードの、板の前面より奥(y > -0.028)の部分の最低 z は 0.238 で、板の上端 z 0.18 より上にある。板とシェードは交差していない。
- 保持したもの:
  - 高さ、幅、厚さ、カップの比率、腕の上下の出口、材質、texture、照明、原点、全体のスケール、向き、単位(METRIC 1.0)
  - object の変換(位置 0、回転は -1.6e-7 rad の浮動小数点の値のまま、scale 1)
- bbox: Y の範囲が -0.178〜+0.044 から -0.228〜0.000 に変わった。X と Z は同じ。接地(z min)は 0。

■ トポロジー、UV、法線(revision02/qa)
- 頂点 1166、面と三角形 2312、loop の頂点 index、polygon の loop_start と loop_total、辺、material index はすべて同じ。順番も同じ。
- UV0(ArchitectureUV): 全 6936 loop で差は 0。Repeat 用の負の座標(6958 成分)も同じ。unwrap はしていない。
  - 腕の側面は Y 方向に伸びたが、UV は元のまま。Metal_ARCH01 は texture を使っていないので、見た目への影響はないと見ている(Unity では未確認)。
- 法線(normal_uv_diff_detail.json)。一括の再計算や設定し直しはしていない。
  - 再読込だけで出る差(baseline を 2 回開いた比較): 全部位で 0。
  - baseline と revision02 の差(corner 法線、成分の絶対差):
    - 板(slot0): 0(564 loop すべて同じ)
    - 腕(slot0、変更した領域): 最大 1.15e-5(x 成分)。1e-5 を超える loop は 6、1e-6 を超える loop は 168。
    - カラー(slot0、平行移動): 最大 1.9e-6
    - シェード(slot1、平行移動): 最大 5.6e-6(1e-6 を超える loop は 473)
    - diffuser(slot1、平行移動): 最大 2.4e-6
    - 平行移動した部品の差は、移動後の座標で保存済みの custom 法線を解き直したときの浮動小数点の差と見ている。完全一致とは言わない。
  - FBX のファイルに書かれた法線(NormalsIndex で展開して比較): 最大 1.15e-5。
    - Blender で読み込み直して比べると、シェードで最大 5.87e-4 になる。これは読み込み側で法線を設定し直すときの量子化の差で、ファイルの中身の差ではない。
    - 根拠: 変更していない baseline を同じ設定で export し直したものは、元の FBX と読み込み比較で 0 になる。
- 品質: 非多様体の辺 0、境界の辺 0、面積 0 の面 0、長さ 0 の法線 0(前後とも)。

■ 改善前の証拠(初回のビルド。候補ではない)
- 初回は normals_split_custom_set で全 loop の法線を設定し直していた。そのため、シェード(slot1)の法線が最大 4.89e-4(z 成分)再量子化された。1e-4 を超える loop は 152、1e-5 を超える loop は 490。
- この初回ビルドの blend は、Blender が自動で作ったバックアップ models/StraightLamp_ARCH01_C1.blend1 として残っている。上の数値は、これを読み取りで測った値。
- 最上位の fbx/、models/StraightLamp_ARCH01_C1.blend、qa/、tools/build_standoff_c1.py について:
  - 削除を含むコマンドが拒否されたあと、削除なしで同じ場所に 2 回目のビルド(法線を設定し直さない版)を実行し、上書きした。
  - これは保持の指示を受け取る前の操作だった。
  - 初回の FBX と qa のバイトは残っていない。
  - 現在の最上位は 2 回目のビルドの出力で、形状と法線は revision02 と同じ方法。FBX は日時と path の文字列が異なるので、バイトは別。
  - 最上位は「旧出力(上書き済み)」として保持し、移動も削除もしていない。

■ 外部画像と形式
- blend の image.filepath は '//../fbx/Shade_ARCH01.png'。revision02/models と revision02/fbx の相対構成で、同梱の PNG(入力とバイトが同じ)を参照する。
- 解決の確認: blend をバイト単位で同じまま別の深いディレクトリへ、models/ と fbx/ の構成ごとコピーした。新しいプロセスで開き、exists、読み込み(1024x1024)、SHA 一致、コピー内で解決していることを確認した(qa/reload_elsewhere_check.json)。
- FBX: 入力と同じ export 設定(coord09 の exp_furn.py と同じ)。
  - UnitScaleFactor 100、Lcl Rotation -90 X、Lcl Scaling 1、FBX 7400。'B' 型の property は 0。
  - texture は RelativeFilename 'Shade_ARCH01.png' と、cloud repo の絶対 FileName を持つ。入力の FBX と同じ形式。
  - UV2 は FBX にはない。Unity の native UV2 の保持と移行は元Codex が検証する。Cloud で UV2 が成功したとは言わない。

■ 比較画像(revision02/previews。モデルだけで、原作の画素はない)
- baseline L1 と C1 を、正面、側面、目の高さからの斜め下で、同じカメラ、光、材質、描画で撮った(計 6 枚)。条件は revision02/qa/render_conditions.json。
- 壁は厚さ 6 cm の板で、室内側の面が Y=0(+0.0002)。側面では、baseline のカップの奥が壁に隠れ、C1 では壁の手前に収まっていることが見える。

■ 未実施と引き継ぎ
- Cloud は pip bpy 4.3.0。ローカルの Blender 5.2.2 と Unity は実行していない。
- 元Codex に残すこと: 受領の照合、5.2.2 での確認、native UV2、Unity で同じ条件での壁の接触と配置の検証。そのあと指示役が選択する。
- 実寸と最終スケールは後工程。倍率 0.7825509309768677 はモデルに焼き込んでいない。
- 実行していないこと: Bake、AO、Play、Build、SDK、upload、インストール、認証・課金の変更。原本と過去の候補は上書きしていない。
