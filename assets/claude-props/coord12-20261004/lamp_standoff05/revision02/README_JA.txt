COORD12-LAMP05 revision02 README(Claude cloud、2026-10-04 JST)
最上位の README_JA.txt / REVIEW_STATUS.txt / MANIFEST.json(commit f0b8778)は、この revision02 版で置き換える。最上位の 3 件は変更せずに残している。

■ 最終候補(1 組だけ)
- revision02/models/StraightLamp_ARCH01_C1.blend
- revision02/fbx/StraightLamp_ARCH01_C1.fbx
- revision02/fbx/Shade_ARCH01.png(入力とバイトが同じ。blend の '//../fbx/' が参照する先)
- 採用はしていない。数値の PASS だけで採用や完成扱いにはしない。

■ 消失の事実(そのまま記録)
- このフォルダで作った初回ビルドについて:
  - 初回ビルドの次のファイルは失われた。git には一度もコミットされていなかったので、履歴にも残っていない。
    - fbx/StraightLamp_ARCH01_C1.fbx
    - models/StraightLamp_ARCH01_C1.blend
    - qa/build_log.json、qa/verify_blend.json、qa/verify_fbx.json
    - tools/build_standoff_c1.py(normals_split_custom_set で法線を設定し直す版)
  - 初回の出力と SHA は記録していない。
  - 経緯: 削除を含むコマンドが拒否されたあと、削除なしで同じ場所に 2 回目のビルドを実行し、上書きした。保持の指示を受け取る前の操作だった。
- 現在の最上位の fbx/、models/StraightLamp_ARCH01_C1.blend、qa/、tools/build_standoff_c1.py は、2 回目のビルドの実在する出力で、候補ではない。
- models/StraightLamp_ARCH01_C1.blend1 は、2 回目の保存のときに Blender が自動で作ったバックアップ。
  - Blender の保存の仕様から、初回の blend だと推定している。
  - ただし、初回の時点の hash の記録がないので、初回のバイトと同じだとは証明できない。「初回版を保持済み」とは言わない。
- 初回で起きた問題(法線を設定し直したことによる、シェードの法線の再量子化 最大 4.9e-4)の根拠は、次の 2 つ:
  - (a) 当時のセッション出力の数値
  - (b) .blend1 を読み取りで測った値(qa/normal_uv_diff_detail.json: シェードで最大 4.89e-4、1e-4 を超える loop は 152)
  - 失われた初回の qa ファイルを再現したものではない。
- 再現として作ったもの(scratch だけ。納品していない):
  - 法線を設定し直さない版の試作
  - DY=0 での baseline の再 export
  - これらは比較のための再構成で、失われたファイルの代わりではない。
- 影響の範囲:
  - LAMP03 の commit 56eaa0f から f0b8778 までの git の変更は、lamp_standoff05/ の追加(A)37 件だけ。それ以外のパスの変更は 0。
  - 入力の L1 の 3 件は、納品の時点で SHA を確認し直し、一致した(qa/input_sha_recheck.txt)。
  - 他の旧成果物は変わっていない。

■ 変更と保持
- 内容は最上位の README_JA と同じ。
- カップ一式(カラー、シェード、diffuser)を -Y へ 0.050 m 動かし、腕の前側の 48 頂点だけを同じ量延長した。
- 板、原点、Y=0、トポロジー、順番、material index、UV0(負の座標も含む)は保持。
- 板以外の最大 Y: +0.044 → -0.006 m。

■ 法線の差を発生源ごとに分けた結果(qa/normal_diff_sources.json。成分の最大絶対差)
- blend を再読込するだけで出る差: 0
- 元の FBX と、変更していない baseline の再 export(scratch)の比較: raw の配列 0、読み込み後 0
- 板(変更していない部品): blend、raw FBX、読み込み後のどれでも 0。一致。
- カラー / シェード / diffuser(平行移動だけ):
  - blend で 1.9e-6 / 5.6e-6 / 2.4e-6
  - raw FBX でも同じ程度
  - 小さいが実際にある差。完全一致の条件は満たさないので、そのまま記録する。
- シェードの読み込み後の 5.87e-4: 動かした形状を Blender で FBX 読み込みしたときにだけ出る。ファイルの値の差は 1.15e-5 以下。
- 腕(変更した領域): 1.15e-5(1e-5 を超える loop は 6)
- UV0: 全 loop で差 0。

■ 検証と引き継ぎ
- 実施した検証(qa/):
  - verify_blend.json、verify_fbx_reimport.json
  - fbx_raw_arrays_and_header.json('B' 型 0、UnitScaleFactor 100、Lcl Rotation -90 X)
  - reload_elsewhere_check.json(別ディレクトリへのコピーと新しいプロセスで、画像を解決)
  - render_conditions.json と previews の 6 枚(Y=0 の壁の板を入れた、同じ条件の baseline と C1)
- 未実施: ローカルの Blender 5.2.2、native UV2、Unity での壁接触と配置。元Codex が検証したあと、指示役が選択する。Cloud は pip bpy 4.3.0。
