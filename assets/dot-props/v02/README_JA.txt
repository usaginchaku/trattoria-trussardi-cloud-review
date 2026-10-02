トラサルディー 参照モデル候補 v02
2026-10-02 / Blender 4.3.2


v02での変更
・花かごの外周18枚の葉を持ち上げて縁との貫通を修正。品質版・LOD1とも葉と籠の三角形交差は0組です
・ワイングラスは飲み口・上部壁を半径方向0.7 mmに変更。脚と底を薄くし、飲み口の内外面と上端の法線を分離して黒く太く見える陰影も修正しました
・子犬は目と瞳を少し大きく、突出を弱め、口と舌を小さめにして優しい表情に調整しました
・承認済みのパールジャム、カトラリー、ナプキンは形状・UVを変更していません
・v01は別に保持しています。この版のポリゴン数はv01と同じです
・Unityでワイングラスのインポート法線を再計算すると、飲み口の陰影が変わります。NormalsはImportとして確認してください

公開用内容
オリジナルのアニメ画像、非公開Driveへのリンク、作業ログ、個人的なメモは含めていません。参照作品に基づくファン制作の候補モデルで、公式アセットではありません。

内容
13種類の静的な小物・キャラクターモデルです。編集用の .blend、個別FBX、外部テクスチャ、実際のモデルから出力した画像を同梱しています。
models/Trussardi_Reference_Props_v02.blend はテクスチャを内蔵しています。
fbx/ 内は個別配置用です。隣接する .fbm フォルダを残してください。
Coreにはモデルと使用説明、QA_Previewsには実レンダーと検査画像を収録しています。
GitHub向けReviewには選択した実レンダーを収録しています。
比較画像の BEFORE は修正前、AFTER はv02です。
qa/ のJSONには計測と再インポート検証を記録しています。

単位・配置
・メートル、Unit Scale = 1
・各単品FBXの実形状の最下点を z=0 に揃えています
・ケージ扉は独立メッシュで、右側の蝶番位置を原点にしています
・.blendでは全体を見渡せるように並べています。単品FBXは配置用の原点に戻しています
・ナプキンは皿の内側形状に合わせ、29,862点のサンプルで接触を確認しました。許容隙間は0.1 mmです
・スプーンは柄とボウルが連続した1つの閉じた形状です。柄の後端とボウル下面が同じ支持面に接します
・実寸は参照写真から確定できないため、日用品として妥当な大きさを仮定しています
・配置先ワールド全体のスケール変更は形状に焼き込んでいません

モデルと三角形数（各1点）
・01_Spiral_Candle: 7,314 tris / 0.098 × 0.098 × 0.710 m
・02_Flower_Basket: 17,382 tris / 0.276 × 0.246 × 0.231 m
・03_Dinner_Plate: 2,176 tris / 0.280 × 0.280 × 0.027 m
・04_Rolled_Napkin: 4,266 tris / 0.199 × 0.050 × 0.050 m
・05_Wine_Glass: 2,400 tris / 0.074 × 0.074 × 0.196 m
・06_Water_Glass: 2,400 tris / 0.061 × 0.061 × 0.161 m
・07_Dinner_Fork: 618 tris / 0.026 × 0.206 × 0.014 m
・08_Dinner_Spoon: 2,076 tris / 0.038 × 0.212 × 0.022 m
・09_Dinner_Knife: 406 tris / 0.022 × 0.236 × 0.003 m
・10_Stamped_Soap: 188 tris / 0.103 × 0.067 × 0.036 m
・11_Teal_Dog_Cage: 5,576 tris / 1.004 × 1.383 × 0.686 m
・12_Healthy_Puppy: 23,234 tris / 0.444 × 0.606 × 0.529 m
・13_Pearl_Jam: 11,676 tris / 0.153 × 0.098 × 0.194 m

合計 79,712 tris、14メッシュ、3種類の共通マテリアルです。
ケージ寸法は開いた扉を含むバウンディングボックスです。本体は約0.80 × 0.64 × 0.68 mです。

任意の軽量版（LOD1）
・品質版はそのまま保持しています。追加の2種類は遠景・複数テーブル向けの代替候補です
・models/Trussardi_Centerpieces_LOD1_v02.blend と fbx/LOD1/ に格納しています
・燭台＋ろうそく: 7,314 → 2,632 tris（64%削減）
・花かご: 17,382 → 7,300 tris（58%削減）
・この2点を軽量版へ置き換えると、食卓一式は39,038 → 24,274 tris（約38%削減）になります
・全セットも79,712 → 64,948 trisになります。品質版と軽量版を両方同時に置く数値ではありません
・輪郭を並べて確認し、頂点から相手の表面への双方向サンプリングでは最大約1.31 mmの差でした。これは全表面の厳密な誤差上限ではありません
・どちらも閉じた形状、2つのUVチャンネル、ライトマップUVの重なりなしを検証しています
・UnityのLODGroupや切替距離は設定していません。配置後のVR実測は必要です
・主な負荷は犬23,234 trisと品質版花かご17,382 trisで、品質版全体の約51%です。対象端末によっては犬なども追加の遠景用モデルを検討してください

テクスチャとUV
・主要部分は1024×1024の共有カラーアトラス、Roughness、Metallic
・色を共有する部品ではUV0を意図的に重ねています。写実的な写真投影ではなく、参照の配色に合わせたスタイライズ用アトラスです
・石けんの薬用スタンプは専用1024×1024のBaseColor/Height/Normal
・全メッシュに別の LightmapUV チャンネルを付けています。UVの範囲と三角形の重なりを数値検証しています。UV0をそのままライトマップ用途に使わないでください
・色アトラスはsRGB、Roughness/Metallic/Height/パック済みマップはNon-Color扱いです
・Unity_Atlas_MetallicSmoothness.png は R=Metallic / A=1−Roughness です
・Soap_Stamp_Normal.png はNormal Mapとしてインポートしてください

VRChatへの持ち込み前に
・このフォルダは既存Unityプロジェクトとは分けた候補ファイルです。Unity統合・実機/VR内確認は未実施です
・FBXを使用し、Trussardi_Atlas を1つの共有マテリアルへ再割り当てすると、重複したマテリアルの増殖を避けやすくなります。マテリアルの共有だけで1 draw callになるわけではありません
・Blenderのノード構成はFBXで完全には再現されません。とくにガラスの透明度・反射・描画順は、ワールドで使うシェーダーに合わせて設定と確認が必要です
・6方向検査画像のグラスだけは内壁を確認しやすい不透明表示です。配布モデルのグラスは透明材質です
・コライダーを付ける場合は、必要なものだけに単純なBox/Capsule/複合形状を使う方針を推奨します。犬の描画メッシュ全体をそのまま衝突判定に使う前提ではありません
・本モデルにはボーン、アニメーション、物理、コライダー、Unity Prefabを追加していません
・Android/Quest向けには、シーン全体での軽量化と実測が必要です。VRChat公式の「ワールド全体で約250k tris」という推奨に対して、このセット1組は約32%です。これは1小物ごとの上限やPC向けの固定上限ではありません

参照確認と再構成の範囲
・食卓: アニメ参照画像。花かご、ねじれたろうそく、燭台、皿、丸めたナプキン、大小グラス、カトラリーを比較しました
・燭台の段と輪郭: アニメ参照画像。
・石けん: アニメ参照画像。ピンクの角丸形状と「薬用」の楕円スタンプ
・ケージ: アニメ参照画像。青緑の枠と縦格子、天井格子、右側開きの扉
・子犬: アニメ参照画像。大きめの角丸頭、外側へ垂れる耳、白い口ひげ・胸・足先、赤い首輪、上向きの尾
・パール・ジャム: アニメ参照画像。赤い球形の本体、クリーム色の垂れた上部、緑の細長い頭頂部と短い腕
・参照で見えない後面・下面・厚みは、矛盾しないよう補完した形状です。厳密な三面図由来ではありません
・写真の画面モアレや反射はテクスチャに写していません

実施した確認
・実際のBlenderレンダーで形状と配色を参照画像と比較し、複数回修正
・全13種類を前・後・左・右・上・下から検査
・ナプキン/皿およびスプーンを低い側面カメラで接地確認
・フォーク/ナイフ下面の重なりを結合して解消
・犬の胸模様は本体表面へ統合し、顎・耳・足先の側面/下面も修正
・全FBXを新規Blenderシーンへ読み直し、三角形数・寸法・UVを照合
・法線の一貫性、意図しない開いた境界、ゼロ面積、座標/UVの有限値を検査

調査した公式資料
VRChat Android/Quest最適化: https://creators.vrchat.com/platforms/android/quest-content-optimization/
VRChat ワールド提出ガイド（FBX推奨）: https://creators.vrchat.com/worlds/submitting-a-world-to-be-made-public/
Blender 4.3 FBX: https://docs.blender.org/manual/en/4.3/addons/import_export/scene_fbx.html
Blender 単位: https://docs.blender.org/manual/en/4.3/scene_layout/scene/properties.html
Blender 原点: https://docs.blender.org/manual/en/4.1/scene_layout/object/origin.html
Unity Lightmap UV: https://docs.unity3d.com/2022.3/Documentation/Manual/LightingGiUvs-GeneratingLightmappingUVs.html
Unity Metallic/Smoothness: https://docs.unity3d.com/cn/2022.3/Manual/StandardShaderMaterialParameterMetallic.html
Unity 透明材質: https://docs.unity3d.com/2022.3/Documentation/Manual/StandardShaderMaterialParameterRenderingMode.html
Unity MeshCollider: https://docs.unity3d.com/2022.3/Documentation/Manual/mesh-colliders-introduction.html
