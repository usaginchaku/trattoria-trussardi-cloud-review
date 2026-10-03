# ART01 reference ledger correction: rebuild rows with proper CSV quoting (colour values contain commas).
import csv, json, io, hashlib
H=['ref_id','target','part','observation','confidence','undetermined_or_speculation','mapping_in_candidate']
R=[
['IMG_3669','Left_Frame_22(UL)','painting','淡い空色地に青い斑、テラコッタ/橙の塊が右下へ段状・斜めに下る','high(4枚とも正面に近く明瞭)','上辺付近は画像端で額ごと切れ不明。3638で上部が淡色と確認するが細部は推測','A1 tile21: 淡空色地+青斑+橙の段状斜め塊(自作手描き)'],
['IMG_3669','Left_Frame_22(UL)','frame/mat','太いオリーブ額に放射状の彫り溝、クリーム色マット、細い暗色内線','medium(画面撮影で色は露出補正x1.2の推定値)','彫り溝の本数/深さは解像度不足で不明','A2 F22: olive暗め(84,88,60)+青マット→クリーム(226,221,198)。彫り溝は未対応(形状変更要)'],
['IMG_3669','Left_Frame_23(UR)','painting','白い上部、ラベンダーの丸い山が3〜4個、中央が最も高い','high','山の境目の細部は画面モアレで不明。モアレは柄に写していない','A1 tile22: 白地+中央高のラベンダー丸山4個(基部連結)'],
['IMG_3669','Left_Frame_23(UR)','frame/mat','細い暗オリーブ額、広い青灰マット、絵は小さい','medium','マット幅は実物の方が広い(=絵が小さい)。幅変更は形状変更要でA1/A2範囲外','A2 F23: 額 青→暗緑(66,70,54)、内リム クリーム→青灰(200,214,214)'],
['IMG_3669','Left_Frame_24(LL)','painting','左に青い縦積みの塊、右に黄土色の縦塊、白い地','high','塊の内部筆致は不明','A1 tile23: 白地+左青縦積み楕円群+右黄土縦塊'],
['IMG_3669','Left_Frame_24(LL)','frame/mat','マルーン額、クリームマット','medium','なし','A2 F24: pink→maroon(112,58,62)'],
['IMG_3669','Left_Frame_25(LR)','painting','紫の角/珊瑚状のY字分岐、下部に明るいラベンダーの塊','high','枝先の本数は推定(3〜5)','A1 tile24: 淡地+紫Y字分岐(太線丸端)+下部淡ラベンダー塊'],
['IMG_3669','Left_Frame_25(LR)','frame/mat','オリーブ額、淡いラベンダー白マット','medium','なし','A2 F25: olive暗め+青マット→淡ラベンダー白(228,228,240)'],
['IMG_3638','Left_Frame_22..25','all','反対側からの視点。人物で一部遮蔽。UL上部が淡色である補助確認','low-medium(遮蔽・斜め)','遮蔽部は判定に使わず人物形状は柄に写していない','補助確認のみ'],
['user_layout_reference_1.jpg','-','-','クラウドに未提供のため未閲覧','-','未閲覧','使用せず'],
]
buf=io.StringIO(); w=csv.writer(buf,quoting=csv.QUOTE_ALL,lineterminator='\n'); w.writerow(H); w.writerows(R)
open('reference_ledger_ART01_fixed.csv','w',encoding='utf-8').write(buf.getvalue())
# verify by re-parsing
rows=list(csv.reader(open('reference_ledger_ART01_fixed.csv',encoding='utf-8')))
assert rows[0]==H and len(rows)==11 and all(len(r)==7 for r in rows), 'column count'
recs=[dict(zip(H,r)) for r in rows[1:]]
assert all(None not in d and all(v is not None for v in d.values()) for d in recs)
json.dump({'note':'参考画像・切抜き・スクリーンショットは含めない。Drive画像ID(ファイル名)と観察記述のみ。IMG_3659-3661は不使用。',
 'columns':H,'rows':recs},open('reference_ledger_ART01_fixed.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
# diagnose old files
old='../../../coord10-20261003/art01/reference_ledger_ART01'
oc=list(csv.reader(open(old+'.csv',encoding='utf-8'))); oj=json.load(open(old+'.json',encoding='utf-8'))
diag={'old_csv_column_counts':[len(r) for r in oc],'old_csv_rows_with_wrong_count':[i for i,r in enumerate(oc) if len(r)!=7],
 'old_json_rows_with_null_key_or_extra':[i for i,d in enumerate(oj['rows']) if 'null' in json.dumps(list(d.keys())) or None in d or len(d)!=7 or any(v is None for v in d.values())],
 'old_json_bad_rows_mapping_values':[oj['rows'][i].get('mapping_in_candidate') for i in (1,3,5,7)],
 'new_csv_column_counts':[len(r) for r in rows],'new_json_rows':len(recs),'new_json_null_or_extra':0,
 'old_files_kept':'coord10-20261003/art01/reference_ledger_ART01.csv/.json は変更せず保持',
 'cause':'旧CSVは色値 (r,g,b) のカンマを無クォートで書いたため列が分断。旧JSONは旧CSVをDictReaderで読んだため、余剰列が null キーに入り mapping_in_candidate が途中で切れた。'}
json.dump(diag,open('ledger_correction_record.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(json.dumps(diag,ensure_ascii=False,indent=0)[:1500])
