COORD09 家具の形状候補（Claude クラウド）
入力: codex/coord09-source-20261003 @ 6b8c26fc21203e068352437e0d16ed5751282b50 の assets/codex-source/coord09-20261003/
- 5 つの FBX、自作 texture 7 枚、MANIFEST、README（SHA は MANIFEST と一致を確認）
- 入力の branch と FBX は変更していない。この folder には、形状を変えた候補と、参照用に複製したバイト同一の texture だけを置く
- 検証環境: pip の bpy 4.3.0（Cycles CPU）。Blender 5.2.2 は実行していない。Unity は触っていない

■ 共通の書き出し規約（source と同じ形式であることを確認済み）
- FBX: apply_unit_scale=True、apply_scale_options='FBX_SCALE_UNITS'、bake_space_transform=False、mesh_smooth_type='FACE'
- 書き出し結果
  - UnitScaleFactor 100、Y-up
  - モデルの Lcl Rotation は X 軸 −90°、Lcl Scaling は 1
  - 頂点はメートル値（source と同じ）
- 無変更で書き出した T0 を source と比較: 頂点の移動 0、corner 法線の変化 0、UV 同一、GlobalSettings 一致
- 配置（MANIFEST.objects）と共通倍率 0.7825509309768677 には触れていない。二重に適用もしていない
- 原点、接地（zmin 0）、FurnitureUV、材質、texture の参照は保持している

■ テーブルクロスの裾（table_hem/）: 形状の一要因だけを変更。色・材質・UV・木部は不変
参考で見えるもの（3664・3695・3594・3755・3756）
- 布が 6〜8 か所ほどで大きく垂れる
- 裾の赤帯は、垂れた点で深く下がり、その間は弧を描いて上がる
- 人物に隠れた部分は推定していない
source の現状（bpy で計測）
- 放射方向のひだ 12 本（振幅 3.6 cm）
- 裾の高さに 4 つの山（±4〜5 cm）
- 裾の高さは 0.228〜0.337 m（8 次までのフーリエで滑らかにした値）
- カスタム法線は既定のスムーズ法線と一致していた（dot=1.0）
T1（推奨）: 裾の高さの変動だけを 2 倍にした
- 山の位置と数（4）はそのまま
- 変形は、天板の縁からの垂れ下がり割合 s の 1.5 乗で重み付けし、天板と縁は不動
- 裾の高さ: 0.169〜0.386 m。床からの余裕は 0.17 m 以上
- 外寸 1.533×1.533×0.72 m は不変
T2（代替・効果は弱い）: ひだの谷だけを内側へ 1.6 倍に深くした
- 外周の半径はそのまま。外寸は 1.524 m で、0.9 cm 小さくなる
- 赤帯の曲線はほとんど変わらない
共通事項
- 布と木部の三角形の交差 0
- 非多様体 0、境界 0、ゼロ面積 0、ゼロ長の法線 0、面の反転 0
- 法線: 動いた布の corner だけを新しい形のスムーズ法線にした（source と同じ作り方）。木部の法線は 0 corner 変更
- 比較画像: previews/table_hem_T0_T1_T2.png（同じカメラ: 正面・側面・低い視点・斜め上）
