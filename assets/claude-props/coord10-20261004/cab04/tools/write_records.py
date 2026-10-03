# CAB04 records: reference profile (IMG_3591, numbers only), ledger (quoted CSV/JSON), native vertex correspondence CSV.
import csv,io,json
prof={'image':'IMG_3591 (Drive; not stored). Cabinet crop origin = full-image pixel (1220,430), scale 1:1.',
 'left_silhouette_rows_px':{'note':'first dark column per row on the cabinet left end (dark = luminance<90)',
   'cap':{'rows':[162,178],'height_px':16,'x_px':18.5,'overhang_vs_carcass_px':25.5},
   'step2':{'rows':[182,206],'height_px':24,'x_px':23.5,'overhang_vs_carcass_px':20.5},
   'step3':{'rows':[210,222],'height_px':14,'x_px':29.5,'overhang_vs_carcass_px':14.5},
   'cove_transition':{'rows':[226,230],'height_px':8,'x_px':'36->43'},
   'carcass_side':{'rows':'234+','x_px':44.5}},
 'front_shadow_lines':{'note':'column x=100 (crop) through the crown front: darker rows at 156-164 and 184-192 = two shadow lines under the upper tiers',
   'col100_luminance':{'144-152':46,'156-164':36,'168-180':42,'184-192':35,'196+':40}},
 'ratios_used':{'overhang cap:step2:step3':'25.5:20.5:14.5 ~ 25:21:15','height cap:step2:(step3+cove)':'16:24:22'},
 'model_mapping':{'band':'existing C3m top band z 0.7182-0.80 (top plate 0.74-0.80 + mould 0.7182-0.7395); overhang limit = existing top plate (x +-0.44, front y -0.28)',
   'cap':'overhang 16.0 mm (x 0.44), front -0.28, height 22 mm','middle':'overhang 13.4 mm (= 16 x 21/25), front -0.2771, height 32 mm (0.5 mm embedded into the cap)',
   'lower':'overhang 9.6 mm (= 16 x 15/25), front -0.2728, height 29 mm (0.5 mm embedded into the middle tier)'},
 'distinguished':{'step/outline':'the three x-plateaus of the left silhouette (cap, step2, step3) and the carcass side','shadow':'the two darker horizontal rows in the front band (under cap and step2)',
   'moire':'fine vertical/horizontal mesh over the whole screen photo; ignored','occluded':'right end and right side of the cabinet hidden by the person; crown depth (front-back) not visible',
   'perspective':'seen from lower left: the top surface recedes (rows 130-160 sloped edge); horizontal and vertical px scales differ, so only ratios within one axis are used'},
 'confidence':{'number of tiers (3)':'medium-high (three plateaus + two shadow lines agree)','overhang ratios':'medium (+-2 px on 15-25 px)','tier heights':'medium (silhouette blur +-2 px)','front projection depth':'not measurable (front faces seen nearly edge-on; depth hidden)'},
 'not_made':['cove/ogee curve of the lowest transition (8 px, too small to read the curve) -> merged into the lower tier as a flat step','right-side return and depth details (occluded)']}
json.dump(prof,open('qa/reference_profile_IMG3591.json','w'),ensure_ascii=False,indent=1)
H=['ref_id','part','observation','confidence','undetermined_or_inferred','used_in_C4']
R=[['IMG_3591','crown tiers','左端のシルエットに3つの段(張り出し 25.5 / 20.5 / 14.5 px、高さ 16 / 24 / 14+8 px)。正面には上2段の下に影の線が2本','medium-high','最下段と本体の間の8 pxは曲線(cove)に見えるが、形は読めない','3段の水平な段(笠木・中段・下段)'],
   ['IMG_3591','overhang','張り出しの比は 25:21:15','medium','張り出しの絶対量は不明(横の縮尺が未校正)','既存天板の張り出し16 mmを上限とし、比で配分(16 / 13.4 / 9.6 mm)'],
   ['IMG_3591','front depth','正面は真横に近い角度で見え、段の前後の出は読めない','low','前方への出は推定。扉の前面(-0.281)と天板の前面(-0.28)より前へは出さない','前方の出 18 / 15.1 / 10.8 mm(側面と同じ比)'],
   ['IMG_3591','right end / depth','右端と右側面は人物で隠れる','high(遮蔽の事実)','隠れた部分は作らない。左右対称と仮定','左右対称'],
   ['IMG_3591','moire','画面全体の細かい網目は撮影モアレ','high','—','形と色に使わない']]
buf=io.StringIO(); w=csv.writer(buf,quoting=csv.QUOTE_ALL,lineterminator='\n'); w.writerow(H); w.writerows(R); open('reference_ledger_CAB04.csv','w',encoding='utf-8').write(buf.getvalue())
rows=list(csv.reader(open('reference_ledger_CAB04.csv',encoding='utf-8'))); assert all(len(r)==len(H) for r in rows)
json.dump({'columns':H,'rows':[dict(zip(H,r)) for r in rows[1:]]},open('reference_ledger_CAB04.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
b=json.load(open('C4/build_C4.json'))
with open('C4/native_correspondence_C4.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,quoting=csv.QUOTE_ALL); w.writerow(['C4_vertex_range','source_in_C3m','change','uv','normals','note'])
    w.writerow(['0-383','0-383 (same index)','none','same','same',''])
    w.writerow(['384-479','384-479 top plate','bottom-end verts moved up (z 0.74 -> 0.7779); top verts unchanged','same','directions unchanged (rigid bevel move)','becomes the cap tier'])
    w.writerow(['480-575','480-575 (same index)','none','same','same',''])
    w.writerow(['576-671','576-671 mould','x/front/top ends moved (x +-0.4181 -> +-0.4336, front -0.268 -> -0.2728, top 0.7395 -> 0.7467)','same','directions unchanged','becomes the lower tier'])
    w.writerow(['672-2131','672-2131 (same index)','none','same','same','doors, panes, knobs, base mould untouched'])
    w.writerow(['2132-2227','copy of 384-479 (new = 2132 + (src-384))','NEW middle tier, reshaped (x +-0.4374, front -0.2771, z 0.7462-0.7784)','copied from top plate loops','copied from top plate loops','faces 4220-4407 (188 tris) appended after all original faces'])
print('ok')
