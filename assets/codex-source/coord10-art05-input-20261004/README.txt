ART05 input — three pictures above the wall cabinet

Scope: Left_Frame_17 / 18 / 19 only. These are not the ART02 UpperFrame group.
The 3 FBX files and 2 PNG atlases are byte-exact existing self-made inputs.
No original anime reference, screenshot, whole blend, Unity project or history is included.

Task boundary
- Produce an image-only PaintingAtlas_FUR06_ART05_candidate.png, RGB 2048 x 2048.
- Edit only drawing cells 16,17,18 of PaintingAtlas_FUR06.png. All other pixels must be exact.
- Preserve all meshes, UVs, units, pivots, poses, dimensions, FinishAtlas and material settings.
- Change only evidenced neutral gray foreground shape groupings. Keep the existing background color/texture, drawing borders and blank margins inside the frames unchanged. The current gray ellipses are placeholders; their presence is not evidence of the original subject.
- Supply a mandatory binary 2048 x 2048 shape-change mask (0/255). Every output pixel outside that mask must be byte-exact to the input, including within cells 16/17/18. The mask must be zero outside those cells.
- Limit mask=255 to old/new foreground shape footprints and immediately necessary transition pixels. Do not mask whole cells or unrelated blank margins. Contour changes may erase old foreground using the unchanged background color or occupy necessary new foreground pixels; this is not permission to change the background style or consume frame margins.
- Subjects and fine contours obscured/small in the reference remain HOLD. Do not invent faces, fruit, text or hidden details. Ask the directing reviewer for missing evidence rather than embellishing.
- No bake, AO, Play, Build, upload, integration or publication.

Exact painting cells, zero-based top-left XYXY with excluded maximum:
Frame_17 / tile16: [1364, 682, 1705, 1023]
Frame_18 / tile17: [1705, 682, 2046, 1023]
Frame_19 / tile18: [0, 1023, 341, 1364]
The drawing step is 341px while UVs divide 2048 by 6. Do not silently repack or change UVs.
target_mapping.json records actual material-slot UVs, sampled pixel bounds and padding.

Texture resolution
FBX files retain their original legacy absolute texture paths. Do not rewrite their binaries.
FinishAtlas_FUR06.png and PaintingAtlas_FUR06.png are supplied beside all three FBX files.
If an importer cannot resolve a legacy path, bind its existing image/material node to the exact supplied basename and verify MANIFEST.json SHA before previewing. Return only the new painting PNG and change evidence.
The preview FBX UV0 values match current native Unity slot UV0. Native UV2 belongs to the separate current Unity mesh and is not supplied or to be replaced.

Review
Technical input/UV agreement is not artistic approval. Compare under the same camera and lighting before any adoption; the director/root owns Unity comparison and integration.
Return the candidate PNG and required PaintingAtlas_FUR06_ART05_shape_change_mask.png, changed-pixel counts per cell, proof of zero pixel changes outside the mask, output SHA/decoded RGB hash and concise observed-versus-unresolved notes.
Input preparation does not itself authorize sharing; the directing agent verifies the package before any publication.
