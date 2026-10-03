COORD10-ART01  窓間4額の絵(Left_Frame_22/23/24/25)  Claude cloud 候補
================================================================
入力: codex/coord10-art01-input-20261003 @ 2adac80eb5036e698322f61fa48499cbf9681a17
      assets/codex-source/coord10-art01-20261003/ (9 files, 読取のみ。source branchへはpushしていない)
実行環境: クラウド pip bpy 4.3.0 (Cycles CPU)。Blender 5.2.2 / Unity は実行していない。
          Bake/AO/Play/Build&Test/SDK/upload は未実行。

■ 構成
 A1/PaintingAtlas_FUR06_A1.png        … A1: tile21-24 の絵だけを描き替えた PaintingAtlas (2048², RGB)
 A2/FinishAtlas_FUR06_A2_F22..F25.png … A2(任意): 額色・マット/内リム色だけ変えた額ごとの Finish atlas コピー
 previews/baseline_A1_A2_same_camera.png … 同一カメラ/ライト/ワールドで baseline | A1 | A1+A2 (正面ortho+斜め)
 previews/atlas_tiles_21_24_before_after.png … atlas tile21-24 の前後(自作部分のみ)
 reference_ledger_ART01.csv/.json     … 参考画像IDごとの 観察/確度/未確定・推測/対応
 external_image_dependencies.json     … マテリアル/テクスチャ差替の対応表(対象4 rendererのみ)
 qa/                                  … 生成スクリプト、検証JSON (verification_ART01.json ほか)
 MANIFEST.json                        … PNG=幅高+decoded RGBA sha256、他=sha256

■ A1 (テクスチャのみ・推奨)
 - 各額の editablePixelRectExclusive 内だけ変更。rect外は decoded RGBA で完全一致(変更画素0)。
 - UVは1/6格子(painter cellの341pxと不一致)のため repack/reindex はせず、既存UV boxへ実面アスペクトで描いた絵を再標本化。
 - 柄(すべて自作の手続き描画。参考画像の転写・トレースなし、モアレ・人物遮蔽は写していない):
   UL F22: 淡い空色+青斑、橙/テラコッタの塊が右下へ段状に斜行
   UR F23: 白い上部、中央が最も高いラベンダーの丸い山4つ
   LL F24: 白地、左に青の縦積み塊、右に黄土の縦塊
   LR F25: 紫の珊瑚/角状Y字分岐、下部に淡ラベンダー塊
 - 額・mesh・UV/法線・配置・マテリアル設定・ライトは不変。

■ A2 (任意・A1と独立)
 - 額色とマット/内リム色だけ。外寸・奥行・原点・軸・取付面は不変(形状は出力していない)。
 - Finish atlas の色セルは他の額や LAY02_GapFrame と共有のため、額ごとのコピー(F22..F25)を用意。
   共有 FinishAtlas_FUR06 原本は変更しない。各コピーは対応1額のみに割り当てる。
 - 変更内容: F22 マット青→クリーム/額オリーブ暗め、F23 額→暗緑/内リム→青灰、F24 額ピンク→マルーン、
   F25 マット青→淡ラベンダー白/額オリーブ暗め。セル内の明度ムラは保持。
 - 色は画面撮影写真からの推定(露出補正約1.2倍)。確度は中。

■ 割当(Root作業)
 - 新規マテリアル PaintingAtlas_FUR06_A1 を作り、Left_Frame_22..25 の Painting slot のみに割当。
 - A2採用時は FinishAtlas_FUR06_A2_F{n} を Left_Frame_{n} の Finish slot のみに割当。
 - LAY02_GapFrame_22/24/25 は mesh 共有のため元マテリアルのまま。同名置換・atlas一括上書きは禁止。

■ 残差(未対応・理由)
 - 実物はマットが広く絵が小さい(特にF23)。窓幅/マット幅の変更は形状変更が必要で A1/A2 範囲外 → 必要なら A3 として別指示。
 - F22 額の放射状彫り溝は未表現(形状/法線の追加が必要)。
 - F23 の山の分離は実物より弱め。UL上部は 3669 で額ごと画像外のため推測。
 - 3638 は人物遮蔽と斜め視点のため補助確認のみ。user_layout_reference_1.jpg はクラウド未提供で未閲覧。

■ 採用推奨
 - A1: 採用推奨(rect外不変を証明済み、形状無変更)。
 - A2: 指示役判断の任意ステップ。色寄せは参考に近づくが推定色のため、Unity/lilToon 実ライトでの確認後に判断を推奨。
 - 本候補は額4枚の絵のみ。ワールド全体の完了を意味しない。

■ 次担当
 - 元Codex(Root): マテリアル新規作成と4 rendererへの割当、Unity/Blender 5.2.2 での表示確認、mip/圧縮時の滲み確認。
 - 指示役: A1採用可否、A2採否、A3(マット幅形状)を出すかの判断。
