ART01 提案入力 / まだClaudeへ送信していません
対象は窓間4額 Left_Frame_22～25 のみ。窓上不足3額や奥壁額の拡大、帯・窓の関係はRoot担当で別工程。
入力4FBXはsourceとUnity原FBXのSHA一致確認済み。使用中Unity UV2 meshの画像UV範囲とinstanceをframe_scope.jsonに記録。
A1：PaintingAtlasのtile21/22/23/24だけを資料の絵柄に沿って修正した候補PNG。元2048×2048、4矩形外は展開画素完全一致。
上左：橙の段状／斜め形。上右：薄紫の大きい塊。下左：青い縦の塊＋黄土色。下右：紫の枝／珊瑚状。これらは指示の補助で、実資料を見ずに推測で描かない。
A2：必要なら4額の枠・マット幅の別案。外寸・原点・軸・奥行・取り付け面を保持。建物との配置は触らない。A1と混ぜず比較可能な出力にする。
FinishAtlasは他の多数の家具も使う。原本の色やUVを一括変更しない。枠色変更は候補専用atlas/materialに限り、Rootが4対象rendererだけに適用する。
特にFrame22/24/25は第一窓前のLAY02_GapFrameへ複製されている。同名置換・既存共有材質変更では意図しない別位置まで変わるため禁止。
出力提案：新規 Claude/Candidates/REVIEW01/ART01/ 内の候補PNG、必要なFBX+blend、変更対象表、プレビュー、生成／編集方法、manifest。クラウド側の対応パスは指示役が指定する。
UV0画像領域、材質slot順、単位、原点、axesを維持。Blender5.2.2互換性と実UnityインポートはRootが独立検証。
既存source、Assets、UnityProject、Reports、CoordinationはClaude編集禁止。ベイク・Build & Test・アップロード禁止。
同梱は既存自作モデルとatlasのみ。元アニメ写真は含まない。資料をClaudeがまだ見られない場合、指示役が私的な添付で渡してから着手。
