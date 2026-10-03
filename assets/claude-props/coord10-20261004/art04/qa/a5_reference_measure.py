# ART04: Frame_22 reference measurement (IMG_3669, Drive; image not stored) vs current / A5.
# Pixel positions from intensity profiles through the UL frame: a row through the picture middle (horizontal)
# and a column through the frame centre (vertical). The photo is an oblique, upward screen shot: horizontal
# distances are foreshortened, so only same-axis ratios are compared. The top bar is outside the photo.
import json
row={'outer_left':27,'bar_left_inner':105,'pic_left_line':138,'pic_right_line':294,'mat_right_outer':300,'bar_right_inner':320,'outer_right':382}
col={'pic_top':'outside photo (frame top cut by image edge)','pic_bottom_line':264,'bar_bottom_inner':302,'outer_bottom':435}
bar_h=((row['bar_left_inner']-row['outer_left'])+(row['outer_right']-row['bar_right_inner']))/2
mat_h=((row['pic_left_line']-row['bar_left_inner'])+(row['bar_right_inner']-row['pic_right_line']))/2
pic_w=row['pic_right_line']-row['pic_left_line']
bar_v=col['outer_bottom']-col['bar_bottom_inner']; mat_v=col['bar_bottom_inner']-col['pic_bottom_line']
ref={'horizontal_px':{'bar_avg':bar_h,'mat_avg':mat_h,'picture_w':pic_w,'bar_over_mat':bar_h/mat_h,'bar_over_picture_w':bar_h/pic_w,'mat_over_picture_w':mat_h/pic_w},
     'vertical_bottom_px':{'bar':bar_v,'mat':mat_v,'bar_over_mat':bar_v/mat_v,'bar_over_picture_h':'undetermined (picture top outside photo)'},
     'grooves_px':{'left_bar_spacing':53,'bottom_bar_spacing':30,'bottom_spacing_over_picture_w':30/pic_w,
                   'direction':'across each bar (radial from the picture): near-horizontal on side bars, near-vertical on the bottom bar, fan/diagonal lines at the bottom mitres'},
     'confidence':{'bar_and_mat_widths':'medium (screen photo, anti-aliased edges, +-3 px)','left/right asymmetry':'perspective (left 78 px, right 61 px)','top bar':'not visible -> undetermined','IMG_3638':'person occludes the frames; not used for measurement'}}
def model(bar,light,pw=0.2395,ph=0.4095,W=0.35):
    return {'bar_m':bar,'light_zone_m(cream rim + visible mat strip)':light,'bar_over_light':bar/light,'bar_over_picture_w':bar/pw,'light_over_picture_w':light/pw,'picture_m':[pw,ph],'outer_m':[W,0.52]}
out={'reference_IMG_3669':ref,'current_source':model(0.027,0.0283),'A5':model(0.042,0.0133),
 'notes':['outer size and picture size are fixed, so the reference bar/picture-width ratio (0.45) cannot be reached (it would need a 0.11 m bar); A5 matches the bar:mat RATIO instead (ref 2.4 horizontal / 3.5 bottom bar, A5 3.2 = inside that range).',
          'bar = olive wood region from outer edge to its inner bevel; light zone = cream rim + visible mat-panel strip up to the painting edge.',
          'A6 bottom/top groove spacing 0.048 m = 0.20 x picture width (same horizontal ratio as the reference). Side-bar spacing in the reference is denser (about 0.4-0.8 x bar width depending on the unknown foreshortening); A6 uses 0.0925 m (5 per side) to keep the grooves few and avoid a grid look - deliberate deviation.']}
json.dump(out,open('a5_reference_measure.json','w'),indent=1)
print(json.dumps({k:out['reference_IMG_3669'][k] for k in ('horizontal_px','vertical_bottom_px')}))
