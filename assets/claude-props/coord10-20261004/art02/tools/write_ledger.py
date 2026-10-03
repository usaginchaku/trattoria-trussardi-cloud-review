# ART02 reference ledger: observation / confidence / undetermined-or-inferred kept in separate columns; CSV fully quoted.
import csv,json,io
H=['ref_id','target','part','observation','confidence','undetermined_or_inferred','used_in_candidate']
R=[
['IMG_3638','wall layout','upper row','壁上部のレール(暗赤茶の帯)の上に額が並ぶ。画像上で左奥→右手前の順に「青赤の風景(オリーブ額)」「マルーン額(頭で遮蔽)」「紫の塊(オリーブ額、上端切れ)」','high','この3枚が LAY03_UpperFrame_1/2/3 であることは、額色の並び(olive/pink/olive = 入力 sourceSpec)からの推定。右上の額は窓間 F22/F23 の真上付近に見え、Frame2 の設計Z(3.717)にも近い。対応は確度中','1=左奥の風景、2=中央マルーン、3=右上の紫 として扱う'],
['IMG_3638','LAY03_UpperFrame_1','painting','横長。上端に白い帯(高さ約10%)。左上は青の面。左下(v約0.75-0.83)から右上(v約0.28-0.39)へ白い斜めの筋。その下〜右下は赤/ピンクの面','high(形と配色)','下中央(u0.35-0.65, v0.75-1)はナイフで隠れる → 赤が続くと推定。赤の縦縞は画面モアレで、柄ではないとして不採用。色は白バランス補正の推定値','A1: 白帯+青+白斜線+赤の平面構成を自作図形で描画(tile3のみ)'],
['IMG_3638','LAY03_UpperFrame_1','frame/mat','オリーブの額。マットは広く、壁とほぼ同じクリーム色(観測 211,210,185 / 壁 208,216,189)','medium','模型の青灰マット(186,199,210)との差は色相の差(露出だけでは説明できない)と判断。壁=模型クリーム色という白バランスの仮定に依存','A2 U1: 青マットセル(1,1)→クリーム(235,221,204)'],
['IMG_3638','LAY03_UpperFrame_2','frame','額の左上角と上辺だけが見える。茶寄りのマルーン(観測 110,81,76)','medium','模型のピンク(152,86,96)とは r/g 比が違う(1.77 vs 1.36)ので、露出だけの差ではないと判断。補正後の目標は推定値','A2 U2: ピンク額セル(3,0)→マルーン(123,85,84)'],
['IMG_3638','LAY03_UpperFrame_2','painting/mat','内側は淡い青灰色に見える','low','人物の頭で大部分が隠れ、マットか絵かも判別できない','A1 変更なし(入力の仮絵のまま)'],
['IMG_3638','LAY03_UpperFrame_3','frame/mat','オリーブ額(94,96,66)、クリームのマット(191,195,169)。どちらも模型とほぼ同じ','medium','—','A2 なし'],
['IMG_3638','LAY03_UpperFrame_3','inner border','マットと絵の間にラベンダーの細い縁(観測 155,160,186)','medium','模型では内側縁とマットが同じクリームセルを共有しているので、色だけ分けることはできない(UV変更が必要で範囲外)','未対応(残件)'],
['IMG_3638','LAY03_UpperFrame_3','painting','白地に紫/モーブの丸い房状の塊。見えるのは絵の下側およそ1/4だけ','low','上側は写真の上端より外で不明。全体の構図は判別できない','A1 変更なし(仮絵のまま)。観察のみ記録'],
['IMG_3669','upper row','-','上段は写っていない(窓間4額の上端で画像が切れる)','high','—','使用せず'],
['IMG_3638','all','occlusion/moire','人物(頭・ナイフ・腕)による遮蔽と画面モアレがある','high','遮蔽部は推定として扱い、モアレと人物の形は柄に写していない','—'],
]
buf=io.StringIO(); w=csv.writer(buf,quoting=csv.QUOTE_ALL,lineterminator='\n'); w.writerow(H); w.writerows(R)
open('reference_ledger_ART02.csv','w',encoding='utf-8').write(buf.getvalue())
rows=list(csv.reader(open('reference_ledger_ART02.csv',encoding='utf-8'))); assert rows[0]==H and all(len(r)==7 for r in rows)
recs=[dict(zip(H,r)) for r in rows[1:]]; assert all(None not in d and all(v is not None for v in d.values()) for d in recs)
json.dump({'note':'参考画像・切抜き・人物画像は含めない。画像IDと観察記述のみ。色値は IMG_3638 の25x25px中央値','columns':H,'rows':recs},open('reference_ledger_ART02.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('rows',len(recs),'cols',set(len(r) for r in rows))
