# ART03 A3: frame : mat : picture ratios. Reference values are pixel measurements on IMG_3669 (Drive, not stored here),
# taken from intensity profiles across Left_Frame_23 (row through picture centre, column through picture centre).
import json
ref_px={'horizontal_row250':{'outer_left':13,'frame_inner_left':45,'pic_left':77,'pic_right':213,'frame_inner_right':241,'outer_right':268},
        'vertical_col140':{'outer_top':29,'frame_inner_top':60,'pic_top':155,'pic_bottom':343,'frame_inner_bottom':453,'outer_bottom':492}}
h=ref_px['horizontal_row250']; v=ref_px['vertical_col140']
W=h['outer_right']-h['outer_left']; H=v['outer_bottom']-v['outer_top']
ref={'W_fractions':{'frame_left':(h['frame_inner_left']-h['outer_left'])/W,'mat_left':(h['pic_left']-h['frame_inner_left'])/W,'picture':(h['pic_right']-h['pic_left'])/W,
                    'mat_right':(h['frame_inner_right']-h['pic_right'])/W,'frame_right':(h['outer_right']-h['frame_inner_right'])/W},
     'H_fractions':{'frame_top':(v['frame_inner_top']-v['outer_top'])/H,'mat_top':(v['pic_top']-v['frame_inner_top'])/H,'picture':(v['pic_bottom']-v['pic_top'])/H,
                    'mat_bottom':(v['frame_inner_bottom']-v['pic_bottom'])/H,'frame_bottom':(v['outer_bottom']-v['frame_inner_bottom'])/H}}
ref['picture_area_fraction']=ref['W_fractions']['picture']*ref['H_fractions']['picture']
ref['in_image_outer_aspect']=W/H; ref['in_image_picture_aspect']=(h['pic_right']-h['pic_left'])/(v['pic_bottom']-v['pic_top'])
def model(pw,ph,OW=0.40,OH=0.48,frame_inner_x=0.1692,frame_inner_z0=0.0308,frame_inner_z1=0.4492,zc=0.24):
    fw=OW/2-frame_inner_x; mw=frame_inner_x-pw/2; fh=frame_inner_z0; mt=frame_inner_z1-(zc+ph/2); mb=(zc-ph/2)-frame_inner_z0
    return {'picture_m':[round(pw,4),round(ph,4)],'W_fractions':{'frame':fw/OW,'mat':mw/OW,'picture':pw/OW},'H_fractions':{'frame_bottom':fh/OH,'mat_bottom':mb/OH,'picture':ph/OH,'mat_top':mt/OH,'frame_top':(OH-frame_inner_z1)/OH},
            'picture_area_fraction':pw*ph/(OW*OH),'mat_width_m':{'side':round(mw,4),'top':round(mt,4),'bottom':round(mb,4)},'picture_aspect':pw/ph}
cur=model(0.27372,0.35372); A3s=model(0.27372*0.654,0.35372*0.654); A3c=model(0.27372*0.80,0.35372*0.80)
out={'reference_IMG_3669':ref,'reference_px':ref_px,'current_source':cur,'A3s_standard_scale_0.654':A3s,'A3c_conservative_scale_0.80':A3c,
 'notes':['frame = outer edge to the inner edge of the frame-colour region (|x|=0.1692 / z=0.0308,0.4492 in the model); mat = from there to the painting edge (includes the existing inner lip bevel and the flat backing panel).',
  'IMG_3669 is an oblique, slightly upward screen photo: horizontal sizes are foreshortened (in-image outer aspect 0.55 vs model 0.833), so only per-axis fractions and the area fraction are used. The real picture aspect is undetermined.',
  'A3 keeps the current painting aspect (0.774) so the ART01 A1 art and the existing painting UVs stay undistorted; scale 0.654 matches the reference picture AREA fraction (0.216); 0.80 is a conservative step.',
  'reference bottom mat (0.238 H) is slightly larger than top mat (0.205 H); this may be perspective (camera below), so the candidate keeps the picture centred (undetermined, not applied).',
  'reference frame bar is wider than the model (0.12 W vs 0.077 W); frame width change is outside A3 scope and was not applied.']}
out['A3s_standard_scale_0.654']['scale_rule']='sqrt(ref_area_fraction / current_area_fraction) = %.3f'%((ref['picture_area_fraction']/cur['picture_area_fraction'])**0.5)
json.dump(out,open('a3_ratios.json','w'),indent=1)
for k in ('current_source','A3c_conservative_scale_0.80','A3s_standard_scale_0.654'): print(k,{a:{b:round(c,3) for b,c in out[k][a].items()} for a in ('W_fractions','H_fractions')},round(out[k]['picture_area_fraction'],3))
print('ref',{a:{b:round(c,3) for b,c in ref[a].items()} for a in ('W_fractions','H_fractions')},round(ref['picture_area_fraction'],3),out['A3s_standard_scale_0.654']['scale_rule'])
