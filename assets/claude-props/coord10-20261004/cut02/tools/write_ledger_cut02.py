# CUT02 reference ledger (quoted CSV + JSON). Image IDs and observations only; no image is stored.
import csv,io,json
H=['ref_id','item','visible_part','observation','confidence','hidden_moire_or_inferred','used_in_CUT02_A1']
R=[
['IMG_3624','fork','頭・首・柄の上部(画面左端。2本目は一部)','4歯で長く細い。歯の根元から首へ、肩が丸く絞られる。頭の付け根に影があり、わずかに匙状。柄は細く首から連続','high','柄の端は画面外。斜めの遠近で頭が大きく見える。画面モアレあり(柄に写さない)','4歯(根元4.0→先2.6mm、間隔3mm、V字の歯底)、丸い肩(S字で24mmかけて絞る)、首幅7.4mm、頭を横方向にわずかに反らせる'],
['IMG_3624','knife','刃と首(画面右端)','刃は広く、先は穏やかに丸い。背は直線に近く、刃側が曲線。刃から細い首を経て柄へ連続','high','柄の大部分は画面外。厚みは読めない','刃幅20mm、先端を刃幅の半円で丸め、首9mmに絞ってから柄へ。刃は背1.9→刃先0.5mmのくさび'],
['IMG_3615','fork x2 / knife / spoon','卓上を真上から見た配置','フォークの柄は細く、端がわずかに広がり丸い。首は細い。スプーンの椀はほぼ楕円','medium','字幕と手でスプーンとナイフの一部が隠れる。小さく写るので寸法比は目安','柄の端を丸くし、端に向けてやや幅を広げる。スプーンの椀を楕円(38×71mm)に'],
['IMG_3651','fork','手持ちのフォーク(小さい)','薄い側面と反りが見える','low-medium','柄の端は手で隠れる。全形状は断定しない','横から見た緩い反り(柄の端は接地、頭は持ち上がる)'],
['IMG_3682','fork?','歯先のみ','先端以外はほぼ隠れる','low','このカットから全形状は断定しない','使用せず'],
['IMG_3755 / IMG_3756 / IMG_3824','spoon','プリン/コーヒーの卓','読めるスプーンは写っていない(カップと皿のみ)','high(写っていないこと)','スプーンの裏面・深さ・首の形は資料なし → 推測','スプーンの深さ6.2mm、肉厚1.3mm、首・柄は一般的な形の推測'],
['指示役のローカル観察','fork / knife / spoon','—','(指示文) フォーク4歯、丸い肩と首、頭がやや匙状に反る。ナイフは丸い先端と広い刃から首への連続。スプーンの裏面・深さは推測','—','観察した原画像は指示役側。クラウドで見た同じ画像と矛盾はない','上記の各項目に反映'],
]
buf=io.StringIO(); w=csv.writer(buf,quoting=csv.QUOTE_ALL,lineterminator='\n'); w.writerow(H); w.writerows(R); open('reference_ledger_CUT02.csv','w',encoding='utf-8').write(buf.getvalue())
rows=list(csv.reader(open('reference_ledger_CUT02.csv',encoding='utf-8'))); assert all(len(r)==len(H) for r in rows)
json.dump({'note':'原作写真・切抜きは含めない。画像IDと観察記述のみ','columns':H,'rows':[dict(zip(H,r)) for r in rows[1:]]},open('reference_ledger_CUT02.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(rows)-1,'rows')
