COORD10-ART03 / NIGHT01  窓間4額の限定モデリング候補 (Claude cloud)
====================================================================
入力 : codex/coord10-art01-input-20261003 @ 2adac80eb5036e698322f61fa48499cbf9681a17 (9 files, 読取のみ)
       + ART01 成果 claude/coord09-model-review-20261003 @ 5994d36 (A1/A2 テクスチャを textures/ にバイト同一でコピー)
参考 : IMG_3669(主)、IMG_3638(補助・人物遮蔽あり)。画像・切抜きは repo に含めない。IMG_3659-3661 は不使用。
実行 : クラウド pip bpy 4.3.0 (Cycles CPU)。Blender 5.2.2 と Unity はローカル未検証。Bake/AO/Play/Build/SDK/upload は未実行。
旧ART01・入力・他候補・Unity本体は上書きしていない。source branch へは push していない。

■ 構成
 ledger_fix/  ART01 参考台帳の訂正版(正しくクォートしたCSV / 構造化JSON / 訂正記録)。旧台帳は保持。
 A3/          Frame_23 マット幅候補 A3s(標準寄り・推奨) / A3c(控えめ)。FBX・編集blend・比率記録・比較・検証。
 A4/          Frame_22 外枠の放射状浅彫り溝候補 A4(1案・推奨保留)。FBX・編集blend・比較(key/graze)・検証。
 textures/    blend が相対参照する ART01 A1/A2 テクスチャ(F22/F23分)。
 tools/       自作コード(build_a3/build_a4/render_one/sheet/verify_art03/check_a4/pen/fbx_strip_paths)。
 external_image_dependencies.json  FBX/blend のテクスチャ参照と Unity 割当ルール。
 MANIFEST.json  PNG=幅高+展開RGBA sha256、その他=bytes sha256。

■ 共通の保持事項
 外寸・厚み・原点・軸(FBX UnitScaleFactor 100 / Up Y / Front Z はソースと一致)・取付面(y=0背面)・スケール1・回転0。
 FBX 出力規約は Codex 家具ソースと同じ(apply_unit_scale, FBX_SCALE_UNITS, mesh_smooth_type FACE)。
 FBX 内のテクスチャパスはファイル名のみ(Blender STRIP が書くコンテナ絶対パスを tools/fbx_strip_paths.py で除去し、再読込で形状同一を確認)。

■ A3 (Frame_23)  詳細: A3/README_A3_JA.txt
 参考の絵の面積比 0.217 に対し、現状は 0.504。独立した絵の板(8頂点)だけを中心基準で縮小し、既存の裏板を広いマットとして見せた。
 A3s 0.654倍(面積比0.216) / A3c 0.80倍(0.323)。UV・法線・トポロジ・他の頂点は不変。
 正面の差分は元の絵の範囲内だけ → 差の原因は絵/マット幅だけ。

■ A4 (Frame_22)  詳細: A4/README_A4_JA.txt
 バーを横切る向きのV溝を左右13本・上下9本(上バーと本数・深さは推定)。オリーブ額面のみ変更。tris 2444→7228。
 既存UVは額の各面がセル全体に重なっているため、限定Normal案は既存UVでは成立しない(作成せず)。

■ 推奨
 A3s: 推奨(参考の面積比と一致し、変更は8頂点だけ)。A3c: 控えめに寄せる場合の代替。
 A4 : 推奨保留。向きは参考と一致するが、模型の額バーが細いため格子状に見え、三角形も約3倍になる。
 いずれも額単体の候補で、ワールド全体の完了ではない。

■ ART01 から継続している残件(今回は混ぜていない)
 F23 の絵の山の分離、UL 上部(画像外)、額バーの太さ(F22/F23 とも参考より細い)。
