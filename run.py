from functions import *
import os

def main():
    
    W=210*10 
    H=297*10
    W_c = W
    H_c = int(W / 16 * 9)
    
    source = extract_img(os.path.join('quantum_mechanics.pdf'), W=W, H=H, dpi=500)
    bbox = gen_bbox(source, thre=10)
    gen_imgs(bbox, os.path.join('output'), source, W_c, H_c, h_speed = 60, v_num = 5, margin = 50)
    render(os.path.join('output'), W_c, H_c, fps=15)
    
        
if __name__ == "__main__":
    main()