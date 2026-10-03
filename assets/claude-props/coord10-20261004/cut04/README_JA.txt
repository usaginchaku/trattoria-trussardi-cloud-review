COORD10-CUT04  新候補 Fork / Spoon の UV0 だけを修正 — Claude cloud
=================================================================
入力 : claude/coord09-model-review-20261003 @ 91bbcff の cut02/CUT02_A1/fbx/
         07_Dinner_Fork.fbx  sha256 acb7eb95d32241833de7…
         08_Dinner_Spoon.fbx sha256 10783c9b2421c1890e85…
       完全な値は uv0_corner_mapping/*_uv0_stats.json と TARGETS.json。読み取りのみ。
       Knife(CUT03)・原本・CUT02/CUT03 の README は変更していない。
実行 : クラウド pip bpy 4.3.0(Blender 4.3 の Python モジュール。FBX は Blender 同梱の parse_fbx / encode_bin で直接読み書き)。
       Blender 5.2.2 / Unity は未実施 → 元Codex。Bake/AO/Normal/MatCap/シェーダー変更なし。

■ 第一納品: UV0 の角ごとの対応表(uv0_corner_mapping/)
 *_uv0_corner_mapping.csv / .npz: FBX の角順に、角番号、面番号、頂点番号、CUT02 の UV0、新しい UV0。
   Fork 3792 角 / 1264 面 / 634 頂点、Spoon 4968 角 / 1656 面 / 830 頂点
 *_uv0_stats.json:
   入出力の SHA、mesh 名、角・面・頂点の数
   不変チャネルの値ハッシュ(Vertices / PolygonVertexIndex / Edges / Smoothing / Normals / NormalsIndex / LightmapUV / Materials)。いずれも CUT02 と同一
   新しい UV0 の統計
 TARGETS.json: native mesh へ適用するときの対応方法。UV0 は角ごとで、投影の継ぎ目で分かれるので、頂点番号だけで合わせないこと。

■ 新しい UV0 の作り方と数値
 方法: 面ごとのボックス投影。面の法線の主軸で投影面を選ぶ(x → (z,y)、y → (x,z)、z → (x,y))。
       全ての面に共通の一様な縮尺(Fork 0.462、Spoon 0.449 UV/m)で、
       原本が使う均一な銀色の領域(u 0.140〜0.185、v 0.140〜0.235)へ配置。atlas の画像は複製のみで、画素は不変。
 面積 0 の三角形(<1e-12): Fork 220 → 0、Spoon 184 → 0
   旧値は元Codex の測定(220 面・3D 面積の 21.143%、184 面・11.703%)と一致。
 最小 UV 面積: Fork 1.49e-8、Spoon 3.50e-8(UV²)
   一様縮尺のもとで、3D 面積との比は最悪 0.714 / 0.748(主軸に対して斜めの面)。
 伸縮: 各面で縮尺は s 以下、最悪の異方性 0.714 / 0.748(1 が理想)。
 重なり: 投影面の違う面どうしは重なる(均一な銀色なので許容。一意な UV ではない)。
 余白: 配置領域の端には接するが、原本の銀色の領域の境界まではさらに 0.0067 以上の余白がある(stats の margin)。
 LightmapUV(UV2)の packing には触れていない。

■ 新 FBX(CUT04_UV0/fbx/)と、UV 以外の同一性
 FBX の要素を全て比較した(qa/*_fbx_tree_diff_cut02_vs_cut04.json)。CUT02 との差は次の 3 つだけ:
   (1) UVMap の UV 配列
   (2) UVMap の UVIndex 配列
   (3) Model の Shading プロパティの型コードを 'B' → 'C' に修復(値は同じ真)
 頂点・面順・法線・UV2・材質・スムージングは、値として完全に同一。
 新 FBX は再エクスポートではなく配列の書き換えなので、法線や頂点順のずれは起きていない。
 (3) の背景: 以前の私のツール fbx_strip_paths.py が、真偽値の型を FBX 標準の 'C' ではなく 'B' で書き戻していた。
   Blender は読めるが、Autodesk FBX SDK / Unity での読み込みは未検証。
   これまでの納品 FBX 30 個のうち 11 個が該当(各 1 か所、qa/fbx_typecode_audit_all_claude_props.json)。
   既存の納品は読み取り専用なので変更していない。修正版の出し直しは指示待ち。
 名前: CUT02/CUT03/CUT04 のカトラリー FBX のオブジェクト名は「…_Mesh.001」になっている(原本は「…_Mesh」)。
   CUT02 README の「名前は原本と同じ」は誤り。UV0 だけの範囲を守るため CUT04 では名前を変えていない。Unity 側での名前合わせが必要。

■ 編集可能 blend(CUT04_UV0/models/)
 新 FBX を読み込んで保存。画像は //../fbx/ の相対パスで解決を確認。
 blend は Blender の読み込みを経ているので、採用には対応表または新 FBX を使うこと。

■ 比較
 無地の銀(qa/preview_material_both.json、両側同一)、同じカメラ・光・露出。
   上面 / 側面(Fork、Spoon)/ 斜めで、A1 と CUT04 の画像は展開した RGBA が完全一致(qa/plain_silver_render_rgba_compare.txt)。
   → 今の無地の銀では見た目は変わらない。この UV 問題が今の見た目の不具合の原因だとは断定しない。
 診断専用(previews_diagnostic_only/): UV0 で手続き的なチェッカー柄を描画。採用する材質/atlas ではない。
   A1 は縦横で縮尺が違い、側壁が縞状に潰れる。CUT04 は全面がほぼ正方形の格子になる。

■ 未検証として保留
 - Tangent: UV0 に依存する。旧 tangent を保持するか新たに算出するかで、将来の Normal に適合するかは未検証。
   原本の tangent は変更していない。FBX に tangent は書かれていない(Unity が読み込み時に計算する設定かどうかは元Codex が確認)。
 - Blender 5.2.2 / Unity での読み込みと、native mesh への UV0 適用 → 元Codex。
 - 負荷: tri は不変。scene 24 個(Fork 12 / Spoon 6 / Knife 6)は、CUT02_A1 で 30576、ナイフを A2 にすると 31728(qa/scene_triangle_load.json)。
