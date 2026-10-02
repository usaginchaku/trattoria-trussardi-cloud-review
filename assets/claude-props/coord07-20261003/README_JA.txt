COORD07 小物候補と検証（Claude / 2026-10-02 22:25〜 JST）
ブランチ: claude/coord07-props-20261003（main から新規作成）。dot/props-v02-20261002・claude/props-v02-review-20261002・claude/coord05-cloud-review・main は変更していない。
これは候補であり、本体への採用ではない。Unity import・VR/Quest 実機・ユーザーの見た目承認は未検証。
RI03 保存シーン同条件比較 14 枚は 0/14 未撮影（クラウド画像で代用していない）。Bake/AO、Play、Build & Test、SDK build、upload は実行していない。

■ 納品一覧（推奨 / 保留）
1. 花籠の高さ A（推奨）: basket_height/A/
   - 品質版 fbx/02_Flower_Basket.fbx、LOD1 fbx/LOD1/02_Flower_Basket_LOD1.fbx、各 .fbm（v02 と同一のアトラス 3 枚）、models/*.blend
   - 籠本体の高さ 0.1125→0.0843 m（×0.75）。全体 0.231→0.203 m。籠の高さ比 0.49→0.42
   - 推奨理由: 参考（DU_ep10-4.png の卓 2 つで約 0.35、Drive IMG_3827 で約 0.24、IMG_3724/3701/3666 でも籠が低く見える）に近づき、横桟の間隔も読める
2. 花籠の高さ B（代替）: basket_height/B/（×0.55、籠の高さ比 0.34。DU_ep10-4 の比に一致。横桟が密に見える）
   - A と B のどちらにするかはユーザーの目視で決める
3. 前回候補（claude/props-v02-review-20261002 @ 80deec1、今回は変更なし・再検証のみ）
   - 水グラス修正（推奨）、犬 LOD1（任意 LOD として推奨）、犬毛色・檻の色アトラス（ユーザー判断待ち）
4. 陰影・材質の検証計画: shading_plan_COORD07.txt（計画のみ）
5. 比較ページ: review_COORD07.html（自作レンダーのみ。原作画像はファイル名と観測記述だけ）

■ 使い方（花籠）
- Unity で v02 の 02_Flower_Basket.fbx と差し替える場合、同名ファイルと隣の .fbm を置き換える。オブジェクト名・材質スロット（Trussardi_Atlas 1 つ）・UV・原点（最下点 z=0、中心は v02 と同じ）・単位（m）は v02 と同じ
- 平面寸法（0.276×0.246 m）は不変なので、卓上の配置は変えなくてよい。高さだけが低くなる
- 差分: 籠の部品の高さ方向のみ（qa/basket_h.py）。葉・花は形を変えず平行移動のみ

■ 検証（クラウド Blender bpy 4.3.0 / Cycles CPU。Blender 5.2.2 は利用できず未実行）
- qa/fbx_verify_all_candidates.json、CHECKPOINT_03_verify.txt を参照（軸・単位一致、回転0・スケール1、z=0 接地、三角形数、UV 2 系統・LightmapUV 重なり 0、非多様体 0、面の反転 0、テクスチャ解決）
- 葉と籠の三角形交差: A・B・LOD1 A・B とも 0（qa/basket_build_*.json）

■ 参照資料（実際に表示したもの）
- Drive 分類済み資料 41 枚（ファイル名は CHECKPOINT_01_ledger.txt）。残りは未取得
- COORD04 アーカイブ: DU_ep10-4.png ほか
- 原作画像・切抜きはこのリポジトリに含めない

■ チェックポイント
CHECKPOINT_01_ledger.txt / CHECKPOINT_02_basket.txt / CHECKPOINT_03_verify.txt / REVIEW_STATUS.txt / remaining_work.txt / MANIFEST.json
