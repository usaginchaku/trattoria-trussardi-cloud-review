COORD10-CUT05  FBX 型コード修正コピー(4 点)— Claude cloud
=========================================================
対象(読み取り専用の元ファイル → 修正コピー。完全な SHA は TARGETS.json):
  CUT02 @ 91bbcff  CUT02_A1/fbx/07_Dinner_Fork.fbx  (acb7eb95…) → fbx_A1/07_Dinner_Fork.fbx
  CUT02 @ 91bbcff  CUT02_A1/fbx/08_Dinner_Spoon.fbx (10783c9b…) → fbx_A1/08_Dinner_Spoon.fbx
  CUT02 @ 91bbcff  CUT02_A1/fbx/09_Dinner_Knife.fbx (30ff436f…) → fbx_A1/09_Dinner_Knife.fbx
  CUT03 @ 0dce019  CUT03_A2/fbx/09_Dinner_Knife.fbx (72259337…) → fbx_A2knife/09_Dinner_Knife.fbx
  - 新しい UV0 の CUT04 は修正済みなので対象外。
  - 比較が混ざらないよう、旧 UV0 のまま型だけを直した。
  - 修正が必要だった旧 FBX 11 個のうち、他の 7 個(ART03/ART04/CAB04/CAB04BASE)は依頼範囲外なので触っていない。過去の証拠として保持。
実行: クラウド pip bpy 4.3.0(Blender 同梱の io_scene_fbx parse_fbx / encode_bin で、FBX の木構造を直接読み書き)。
      再エクスポートではない。blend は再保存していない。Blender 5.2.2 / Unity / Autodesk FBX SDK での互換性確認は未実施 → 元Codex。

■ 変更(tools/fbx_bool_typecode_repair.py)
 'B' 型のプロパティだけを、FBX 標準の 'C'(1 バイト)で同じ値に書き戻した。それ以外の型は対応する同じ型で書き戻し、暗黙の変換はしない。
 4 ファイルとも、該当は /Objects/Model/Shading の 1 か所だけ(True → b'\x01')。

■ 検証(qa/)
 tree_diff_*.json: 全要素・全プロパティの値と型を比較。差は 4 ファイルとも Shading の 1 か所(型 B → C)だけ。
 array_hashes_and_reimport.json:
   FBX 内の全配列 11 本(頂点、面順、辺、スムージング、法線・法線 index、UV0・UV2 と index、材質)の値ハッシュは新旧で同一
   Blender で再読込しても同一: 頂点、ループ順、corner 法線、UVMap / LightmapUV、材質、画像、変換。bbox も同じ
 typecode_audit_cut05.json: 修正コピーに 'B' 型は 0。
 plain_silver_top_rgba_compare.txt: 無地の銀の上面(Fork A1 + Spoon A1 + Knife A2)で、新旧の展開 RGBA が完全一致(1 組のみ撮影)。
 atlas(fbx_A1/、fbx_A2knife/ の Trussardi_Atlas_*.png): 元のコミットとバイト一致の複製。FBX はファイル名だけで参照。

■ 名前(変更していない)
 オブジェクト名は元のまま「07_Dinner_Fork_Mesh.001 / 08_Dinner_Spoon_Mesh.001 / 09_Dinner_Knife_Mesh.001」。
 v02 原本の「…_Mesh」とは一致しない。元Codex が kind/path の対応を記録して扱う前提で、無断で合わせない。
