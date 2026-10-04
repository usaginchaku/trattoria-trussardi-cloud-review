COORD12-FOOD24 桃色の皿の上面リムを限定修正した候補(Claude cloud、2026-10-05 JST)
最終候補は revision02/C1r2/ の 1 組だけ:
- revision02/C1r2/PinkPlate_FOOD24_C1r2.blend
- revision02/C1r2/PinkPlate_FOOD24_C1r2.fbx
- revision02/C1r2/textures/
採用はしていない。原作の画像は Claude は表示しておらず、公開出力に原作の画素はない。残差の観察は Root と指示役によるもの。

■ 入力(確定 commit 069eb4de14c09263adbe59799576f66e96eefb80 の assets/codex-inputs/coord12-food24/ の 8 件だけを git archive で取り出した。merge はしていない)
- 8 件の完全な SHA は指定と一致した。開始時(qa/input_sha_at_start.txt)と納品時(qa/input_sha_at_delivery.txt)で同じ。
- 入力の PinkPlate_FOOD23.blend は Blender 5.2.2 の新しいファイル形式で、Cloud の pip bpy 4.3.0 では開けなかった(incomplete header)。入力の不具合ではなく、版の違い。
- そのため、正本の pink_plate_native.json と入力 FBX から作業した。検証済みの点:
  - FBX と native JSON は、頂点 1647 の並びと位置、三角形 2880 の順番、UV0 が一致し、法線の差は最大 0.032°。
  - 軸の変換は native (x, y, z) → Blender (x, -y, -z)。行列式は +1 で、巻き方向は変わらない。単位は設計メートル。物体の変換は恒等。倍率 0.7825509309768677 は焼き込んでいない(Root が保持)。
- B0(PinkPlate_FOOD24_B0_rebuilt): C1 と同じ手順で作り直した基準。入力 FBX と再 import で比べ、位置・UV0・三角形がビット一致、法線の差は 0(qa/verify_inputFBX_vs_B0_fbx.json)。
- 入力の blend の材質ノードや属性名は Cloud では読めないので、blend の材質は FBX から読み込んだプレビュー用の BSDF(Normal 画像)になっている。lilToon や MatCap と同じではない。
- 追加した属性: sourceNativeVertexId(native JSON と一致を確認)、nativeTangentXYZ / nativeTangentW。名前は入力の blend とは照合していない。

■ 形状の変更(編集を許された 194 頂点だけ。revision02/qa/upper_profile は ../qa/upper_profile_B0_C1.json を参照。C1 と C1r2 で位置は同じ)
上面の断面(Blender の z、r は半径、単位 m):

| r | B0 | C1 / C1r2 |
|---|---|---|
| 0〜0.0513(中心の接地面) | 0.0222 | 0.0222(不変) |
| 0.0612 のリング | 0.0228 | r 0.0560 へ移動、z 0.0285 |
| 0.0738 のリング | 0.0260 | r は不変、z 0.0298 |
| 0.085 以上(外周の唇) | 0.0305〜0.031 | 不変 |

区間ごとの勾配:
- B0 は 3.5° → 14.3° → 21.9° と次第に急になる、広い斜面。
- C1 は 0.0513〜0.056 が 53.3°(幅 4.7 mm の狭い内側の段差)、0.056〜0.085 が 4.2° と 3.6°(幅 29 mm のほぼ平坦なリム)。
- 数値は自作の候補の値で、原作の寸法を回復したものではない。

- 保持したもの:
  - 1453 頂点の位置
  - 中心の接地面(r ≤ 0.0513 で上向き、193 頂点)、下面(native の法線 z > 0、969 頂点)、外周の唇(r ≥ 0.08505、485 頂点)。どれもビット一致。
  - 外径 0.09、bbox、原点、軸、単位、変換
  - トポロジー、コーナーの順番、UV0(コーナー単位でビット一致)、material
- UV2: 入力の native では空。出力にも UV2 はない。Root で別に検証してほしい。
- 法線:
  - 未編集の loop は native の法線をそのまま設定した。B0 との差は最大 0.0198°(隣接リングの 5 loop、FBX では 48 loop)。
  - 編集した 194 頂点(1152 loop)だけを、局所的に更新した。
  - 隣接する固定リング(r 0.0513 と 0.085)の法線は、native のまま残した。
    - r 0.0513 は上向きで、平らな中心の縁になる。
    - r 0.085 は外周の唇の帯なので変えていない。ここは新しいリムの勾配と比べて約 10° 外へ傾いていて、外周近くの陰影の移り変わりとして残る。
- 接線: 編集した頂点だけ、native の接線を新しい法線へ射影して直交化した(w は保持)。FBX の接線は export していない(use_tspace=False)。
- 閉鎖性:
  - そのままでは非多様体の辺 412。native の UV や法線の継ぎ目の重複頂点による見かけの境界。
  - 位置で結合した診断だけで測ると 1442 頂点で、非多様体 0、境界 0(閉じている)。候補では結合していない。
  - 面積 0 の面は 0。

■ C1(初回、不採用、保持)と revision02(修正)
- C1(C1/): 編集した頂点の法線を、位置で結合した上面の面法線を面積で重み付け平均して作った。三角形の並び方に左右され、リムに放射状の筋が出た。
- 初回の側面の断面図は、手前の半分を残していたため、切り口が写っていなかった(previews/plate_*_side_section.png)。
- C1 と初回の画像は、作成時の SHA のまま保持している(qa/output_sha_at_creation.txt、first_previews_sha_at_creation.txt)。
- revision02 で直したこと:
  - 法線: 編集した 2 つのリングの法線を、回転体の断面の勾配(隣り合う区間の角度の平均)から決めた。loop 法線と面法線の角度は最大 41.8° → 24.6°。
  - 断面図: 奥の半分を残すようにした。
  - 形状は C1 と同じ。

■ 検証(revision02/qa。B0 と C1r2 を、blend と FBX の再 import で新しいプロセスで比較)
- 動いた頂点は 194 で、すべて編集してよい集合の中。
- 3 つの帯域とその他の位置は、ビット一致。
- UV0、トポロジー、material はビット一致。
- sourceNativeVertexId は一致。
- 外部画像: blend を別の場所にコピーして新しいプロセスで開き、'//textures/Normal_CeramicMicro_MAT01.png' を解決した。512 px で、SHA は入力と一致。
- 同梱の 2 つの PNG は、入力とバイト一致。
- 比較画像(revision02/previews。自作の皿だけで計 6 枚):
  - B0 と C1r2 を、低めの正面、側面の断面、斜めの 3 視点で、同じカメラ・光・材質・描画で撮った。
  - 描画は Blender の BSDF のプレビューで、lilToon ではない。原作と完全に一致するとは言わない。
- revision02/qa/C1r2_native_position_patch.json: Root が元の 5.2.2 の blend に適用するための、194 頂点の native 座標(他の頂点は不変)。

■ 実行環境と未実施
- pip bpy 4.3.0(Cycles CPU)。
- Blender 5.2.2、native、lilToon、Unity、Bake での検証は実施していない。
- 実行していないこと: Bake、AO、Play、Build&Test、SDK、world upload、認証・課金の変更。
