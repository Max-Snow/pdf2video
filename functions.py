from pdf2image import convert_from_path
import numpy as np
import cv2
import os
from glob import glob

def extract_img(pdf_path, W=210*10, H=297*10, dpi=500):

    pages = convert_from_path(pdf_path, dpi=dpi)

    imgs = list()
    for i in range(len(pages)):
        img = np.array(pages[i].resize((W,H)).convert(mode='L').getdata()).reshape((H,W)).astype(np.int32)

        img = 255 - img
        img[img>0] = 255
        imgs.append(img)
    source = np.concatenate(imgs, axis=0)
    
    return source

def bbox_w(line):
    for w in range(line.shape[1]):
        if (line[:,w] == 255).any():
            w_l = w
            break
            
    for w in reversed(range(line.shape[1])):
        if (line[:,w] == 255).any():
            w_r = w
            break
            
    return w_l, w_r

def gen_bbox(source, thre=10):
    bbox = list()
    blank = True
    h_u = 0
    for h in range(source.shape[0]):
        if (source[h,:] == 255).any() and blank:
            blank = False
            h_u = h

        if not ((source[h,:] == 255).any() or blank or ((h-h_u) < thre)):
            blank = True
            h_d = h - 1

            w_l, w_r = bbox_w(source[h_u:h_d+1,:])
            bbox.append((h_u,h_d,w_l,w_r))
            
    return bbox

def gen_imgs(bbox, output_dir, source, W_c, H_c, h_speed = 60, v_num = 5, margin = 50):
    
    canvas = np.zeros((H_c, W_c)).astype(np.int32)
    
    frame = 0
    prev_h_d = 0
    for line_bbox in bbox:

        h_u,h_d,w_l,w_r = line_bbox
        h_num = int((w_r - w_l)/h_speed) 

        dis = (h_d - prev_h_d)
        ds = np.linspace(0, dis, v_num).astype(np.int)
        ds = [(ds[i+1] - ds[i]) for i in range(ds.shape[0]-1)]
        for v_step in ds:
            canvas = np.pad(canvas, ((0,v_step), (0,0)), 'constant', constant_values=((0,0),(0,0)))[v_step:,:]
            frame += 1
            cv2.imwrite(os.path.join(output_dir, 'frame_'+str(frame).zfill(6)+'.png'), canvas, [cv2.IMWRITE_PNG_COMPRESSION, 9])

        for w in list(np.linspace(w_l+1,w_r+1,h_num).astype(np.int)):
            canvas[-margin - (h_d - h_u + 1):-margin, w_l:w] = source[h_u:h_d+1, w_l:w]
            frame += 1
            cv2.imwrite(os.path.join(output_dir, 'frame_'+str(frame).zfill(6)+'.png'), canvas, [cv2.IMWRITE_PNG_COMPRESSION, 9])

        prev_h_d = h_d
        
    return
            
def render(img_dir, W_c, H_c, fps=15):
    images = sorted(glob(os.path.join(img_dir, '*.png')))

    video = cv2.VideoWriter('video.avi', fourcc=0, fps=fps, frameSize=(W_c,H_c))

    for image in images:
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()
    os.system('ffmpeg -i video.avi video.mp4')
    return