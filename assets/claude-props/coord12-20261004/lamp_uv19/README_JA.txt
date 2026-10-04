COORD12-LAMP19 J 字の腕の端面の UV0 だけを局所修復(Claude cloud、2026-10-04 JST)
新しい組を 2 つ作った(既存のファイルは置き換えていない。採用は Root の検証のあと):
- A_UVFIX(入力 A = LAMP11 r2 の ARM_C1r2)
  - A_UVFIX/models/StraightLamp_ARCH01_ARM_C1r2_UVFIX.blend 70e7d132…
  - A_UVFIX/fbx/StraightLamp_ARCH01_ARM_C1r2_UVFIX.fbx 8a2624b0…
  - A_UVFIX/fbx/Shade_ARCH01.png ea737420…
- B_UVFIX(入力 B = LAMP15 の PLATE_C1)
  - B_UVFIX/models/StraightLamp_ARCH01_PLATE_C1_UVFIX.blend 42b0a0dd…
  - B_UVFIX/fbx/StraightLamp_ARCH01_PLATE_C1_UVFIX.fbx e4ec1f6c…
  - B_UVFIX/fbx/Shade_ARCH01.png ea737420…
- B の板の変更(LAMP15)は混ぜていない。それぞれ自分の入力と、UV 以外のすべてが一致する。
- B は板の底 z 0.0225、旧原点のまま。接地や原点の付け直しはしていない。

■ 原因(独立に確認)
- 旧ツール lamp_support11/revision02/tools/r2_build_support_c1.py(sha256 cbe25c9d…)の 55 行目で、端面の UV を (x, v.y if 壁端 else v.z) にしていた。
- 上端(リング 0 の 16 頂点 1070〜1085)は z が一定なのに (x, z)、壁端(最後のリングの 16 頂点 1390〜1405)は y が一定なのに (x, y) を使っていた。そのため、どちらも V が一定になり、線に潰れていた。
- 3D の形の問題ではない。端面の 3D 面積は正常。
- Root の報告と一致した(qa/diagnose_input_*.json、raw_fbx_uv_corners_*.json):
  - 上端の 14 面は 2444、2766〜2778、壁端の 14 面は 2445、2779〜2791。
  - raw FBX の 0 始まりのコーナー番号は 7332〜7337 と 8298〜8375、計 84 個。
  - UV0 の面積 0 が 28 面。3D 面積の合計は 0.0018899999984。
  - 側面の 640 三角形と、腕以外の 2124 三角形は健全。
  - blend と FBX の再 import の面番号も同じだった(番号が同じことを確かめてから使った)。

■ 修復(tools/fix_cap_uv0.py)
- 端面 28 面の 84 コーナーについて、U(= x)はそのままにし、V だけを直した: 上端は y、壁端は z(面の中で正しい投影)。
- qa/changed_corners.json に、変更した集合(面、コーナー、頂点、修正前と修正後の UV)を記録した。

■ 検証(qa/verify_{A,B}_{blend,fbx}.json。入力と UVFIX を新しいプロセスで読み込んで比較)
- 4 通り(A と B、blend と FBX の再 import)とも、次の結果だった:
  - 頂点の位置、loop の頂点、ポリゴンの開始位置と数、辺、material、smooth、corner 法線(custom): ビット一致。
  - object の変換、単位(METRIC 1.0)、材質、UV 層名(ArchitectureUV)、custom 法線あり: 同じ。
  - UV0: 端面以外(側面の 640 三角形、腕以外の 2124 三角形)はビット一致。U は全コーナーでビット一致。
  - 変わったコーナーは 84 で、すべて端面の中。
  - 端面 28 面の UV 面積: 0 が 28 面 → 0 が 0 面。すべて有限の値。UV 面積の合計 0.00189 は 3D 面積と同じ(相対差 0)。V と投影の差は 0。
  - 非多様体 0、境界の辺 0。
- raw FBX(qa/raw_fbx_uv_corners_*.json、raw_fbx_A/B.json):
  - 頂点とコーナーの順番は同じ。
  - 法線の配列(NormalsIndex で展開)と material は同じ。
  - UV の表は並びが変わるが、コーナーごとに展開して比べると、変わったのはコーナー 7332〜7337 と 8298〜8375(三角形 2444、2445、2766〜2791)の 84 個だけ。U はすべて同じ。
- 外部画像: 'models/' と 'fbx/' の構成ごと別の場所にコピーし、新しいプロセスで開いて Shade_ARCH01.png を解決できた(A と B の両方)。
- 入力の SHA(A、B、Shade、旧ツール)は、開始時と納品時で一致した。出力は作成時の SHA のまま。

■ 診断画像(previews/。自作のモデルだけで、写真はない。数値と実際に作った画像だけ)
- uv_caps_input_vs_uvfix.png: A の両端の UV。赤が入力(線に潰れている)、灰色が UVFIX の三角形。B の端面の UV は A とビット一致なので、図は A だけ。
- arm_caps_checker_A_input.png / arm_caps_checker_A_UVFIX.png: 腕だけを残し(カラー、シェード、板はメモリ上で削除)、描画のときだけ UV のチェッカー材質を貼って、同じカメラ・光・描画で撮った近接の 2 枚。入力では端面が縞模様、UVFIX ではチェッカーになる。
- 通常、端面はカラーと板の中に埋まっていて見えない。UV の面積が直ったことだけで、Unity での見た目の採用を決めてはいけない。

■ 未実施と保留
- Cloud は pip bpy 4.3.0。Root のローカル Blender 5.2.2、native UV2、Unity での確認は実施していない。
- Root の LAMP12 / LAMP16 は、この納品の受領に依存する部分だけが保留。
- 実行していないこと: Bake、AO、Play、Build、SDK、upload、インストール、認証・課金の変更。旧ツール、原モデル、旧候補、旧監査は変更していない。
