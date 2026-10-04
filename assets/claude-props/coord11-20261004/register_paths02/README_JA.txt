COORD11-REG03 レジ R1 の blend 画像参照と文書の修正(Claude cloud、2026-10-04 JST)。形状は作り直していない。RI16 へは自動統合しない。

■ 元にしたもの(読み取りのみ。上書きしていない)
- R1 blend:
  - commit 21c109ca3ac8a7a13fac6c79f5a207a51e316659
  - path: assets/claude-props/coord11-20261004/register_candidate/Register_FUR05_REG01_R1_candidate.blend
  - sha256 d3251a0e19d2d1ffec04e048984548f0b1e8c76cb74c7bfaf2855b00df81b7f2
- 4 PNG: commit 35e983d4 の assets/codex-source/coord11-register-input-20261004/ から、検証のときだけ scratch へ取り出した。この納品には複製していない。
- 既存の R1 FBX: 修正していない。FBX 側の 4 PNG 参照は、元Codex の確認で正常とされている。

■ 修正したもの
- Register_FUR05_REG03_R1_paths_fixed.blend(sha256 54001f6f9c2f3d5a939980dba55b35e704345bc32e717c742c65285fa5002d81)
- 変更点は、4 つの image.filepath だけ:
  - 前: '/keys_FUR05.png' など。先頭のスラッシュ 1 本の、ルートからの絶対パス。
  - 後: '//keys_FUR05.png' など。blend と同じフォルダを基準にした相対参照。
  - 4 件: keys_FUR05.png、panel_FUR05.png、register_FUR05.png、register_shadow_FUR05.png
- 原因:
  - R1 の build では、一時ライブラリを '/' に保存し、そこから object を取り込んだ。このとき '//名前.png' が '/' を基準に解決され、'/名前.png' として保存された。
  - R1 の README にあった「//basename で参照」という説明は、実際のファイルと合っていなかった(元Codex の指摘のとおり)。
- 保存の方法: save_as_mainfile(relative_remap=False, compress=False)
  - path を入れる固定長バッファは、一度埋め草で上書きしてから値を書いた。古い文字列の残りは書き込まれていない。
- relative_remap の注意(qa/probe_resave_relative_remap.json):
  - bpy 4.3.0 で、別のフォルダへ relative_remap=True(既定)で「名前を付けて保存」すると、'//../../名前.png' のように元の場所を指す相対パスに書き換わる。
  - これは Blender の仕様で、保存後も同じファイルを指し続けるための動作。
  - ファイルをコピーして運ぶ場合は、blend をそのままコピーすること。Blender から保存し直すなら relative_remap=False を使うこと。

■ 検証(すべて新しいプロセスで、scratch 内で実施)
- 手順: 保存したら終了し、blend を別のフォルダ(scratch の elsewhere_after/sub/)にバイト単位でコピーした。同じフォルダに元の 4 PNG を置き、新しいプロセスで開き直した。
- 修正後(qa/refs_after_reload_elsewhere.json):
  - 4 件とも、filepath が '//名前.png' で、abspath は blend と同じフォルダを指し、exists=True。
  - 画素を読み込めた(512x512)。PNG の sha256 は入力 MANIFEST と一致した。
- 修正前の R1 を同じ条件で開いた結果(qa/refs_before_reload_elsewhere.json):
  - 4 件とも filepath が '/名前.png' で exists=False。元Codex の報告と同じ結果になった。
- 形状などの保持(qa/channels_before_R1_blend.json と qa/channels_after_paths_fixed_blend.json):
  - 比べたチャンネル:
    - mesh: 頂点の座標、loop の頂点、ポリゴン、辺、material index、smooth、corner 法線(custom 法線あり)、UV 層(FurnitureUV)、属性の一覧
    - 三角形数(5372)
    - object: matrix_world、位置、回転、scale、material slot
    - material: 4 件の node、入力値、link、image の割り当て
    - scene の単位(METRIC、1.0、METERS)
  - 結果: 修正前と修正後の fingerprint は完全に一致した。違いは image の filepath だけ。17 部品の姿勢も頂点の座標に含まれており、変わっていない。

■ R1 README の説明の訂正(実測。qa/housing_top_measure.json)
- R1 README の「最高の高さ(芯 0.2431、外周 0.2454)は元のまま」という記述は誤りだった。
- 実測では、上部筐体の上端は、元が 0.2454226 m、R1 が 0.2451000 m で、R1 のほうが 0.3226 mm 低い。
  - build の値 0.2431 + bevel 0.002 = 0.2451 と一致する。
  - 元の丸みのある箱は 0.2454 に達していた。
- 全体の bbox の上端 0.25 は、変更していない上部キャップによるもので、保持されている。筐体の上端と全体の外寸は別物として扱う。
- この差は記録するだけにとどめ、geometry の修正では合わせていない。
- 既存の R1 の README や qa は上書きしていない。この README が訂正の記録になる。

■ 未実施と保持
- Cloud は pip bpy 4.3.0。Blender 5.2.2 での再検証と Unity は実施していない。指示役と元Codex がローカルで再検証したあとに採否を決める。
- 保持しているもの:
  - 原本、入力、R1 の blend / FBX / preview / qa
  - RI16
  - 倍率 0.7825509309768677
  - 仗助 180 cm / エク 160 cm
  - Water、プリンの皿 2 枚
- この納品では PNG を新しく作っていない。
- 実行していないこと: Bake、AO、Play、Build&Test、SDK、upload、認証・課金・インストールの変更。
