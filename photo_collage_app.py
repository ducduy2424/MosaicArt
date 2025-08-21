
import io
from typing import List, Tuple, Optional
from PIL import Image, ImageOps, ImageColor, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Photo Collage App", page_icon="🖼️", layout="wide")

st.title("🖼️ Photo Collage App (Python + Streamlit)")
st.write("Ghép nhiều ảnh thành một ảnh duy nhất. Tải ảnh lên, chọn bố cục, rồi **Create Collage** để tải về.")

# Sidebar controls
st.sidebar.header("⚙️ Cài đặt")
layout = st.sidebar.selectbox("Bố cục", ["Grid", "Horizontal strip", "Vertical strip"])
bg_color = st.sidebar.color_picker("Màu nền", "#FFFFFF")
gap = st.sidebar.slider("Khoảng cách giữa ảnh (px)", 0, 40, 8, step=1)
padding = st.sidebar.slider("Lề ngoài (padding) (px)", 0, 100, 24, step=2)
keep_aspect = st.sidebar.checkbox("Giữ tỉ lệ ảnh trong ô (letterbox)", value=True)
add_border = st.sidebar.checkbox("Viền ảnh", value=False)
border_px = st.sidebar.slider("Độ dày viền (px)", 1, 20, 4) if add_border else 0

if layout == "Grid":
    cols = st.sidebar.number_input("Số cột", min_value=1, max_value=10, value=3, step=1)
    rows = st.sidebar.number_input("Số hàng (0 = tự tính)", min_value=0, max_value=10, value=0, step=1)
else:
    cols, rows = None, None

max_w = st.sidebar.number_input("Chiều rộng tối đa đầu ra (px, 0 = auto)", min_value=0, max_value=10000, value=0, step=50)
max_h = st.sidebar.number_input("Chiều cao tối đa đầu ra (px, 0 = auto)", min_value=0, max_value=10000, value=0, step=50)

st.sidebar.caption("Gợi ý: bật *Giữ tỉ lệ* để ảnh không bị méo; tắt để ảnh vừa khít ô.")

uploaded = st.file_uploader("Tải lên nhiều ảnh (PNG/JPG/WebP)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

def parse_color(c: str) -> Tuple[int,int,int, int]:
    # Convert hex or CSS color to RGBA
    try:
        rgb = ImageColor.getrgb(c)
        return (*rgb, 255)
    except Exception:
        return (255,255,255,255)

def thumbs_from_images(images: List[Image.Image], target_size: Tuple[int, int], keep_ar: bool, bg=(255,255,255,0), border=0) -> List[Image.Image]:
    out = []
    for im in images:
        if keep_ar:
            thumb = ImageOps.contain(im, (target_size[0]-2*border, target_size[1]-2*border), Image.LANCZOS)
            canvas = Image.new("RGBA", target_size, bg)
            x = (target_size[0] - thumb.width)//2
            y = (target_size[1] - thumb.height)//2
            canvas.paste(thumb, (x, y))
            if border > 0:
                draw = ImageDraw.Draw(canvas)
                # draw rectangle border inside
                draw.rectangle([0,0,target_size[0]-1,target_size[1]-1], outline=(0,0,0,255), width=border)
            out.append(canvas)
        else:
            thumb = im.resize((target_size[0], target_size[1]), Image.LANCZOS)
            if border > 0:
                canvas = Image.new("RGBA", target_size, bg)
                canvas.paste(thumb, (0,0))
                draw = ImageDraw.Draw(canvas)
                draw.rectangle([0,0,target_size[0]-1,target_size[1]-1], outline=(0,0,0,255), width=border)
                out.append(canvas)
            else:
                out.append(thumb.convert("RGBA"))
    return out

def make_collage(images: List[Image.Image]) -> Optional[Image.Image]:
    if not images:
        return None

    # Determine layout
    if layout == "Horizontal strip":
        # height equals max of images resized to same height cell
        # choose a cell height based on first image width-scale
        base_h = max(im.height for im in images)
        cell_h = min(base_h, 600)
        # compute cell widths proportional
        ratioed = [im.width / im.height for im in images]
        # temp cells width = r * cell_h
        cell_ws = [int(r * cell_h) for r in ratioed]
        W = sum(cell_ws) + gap*(len(images)-1) + 2*padding
        H = cell_h + 2*padding
        if max_w and W > max_w:
            scale = max_w / W
            cell_ws = [int(w*scale) for w in cell_ws]
            cell_h = int(cell_h*scale)
            W = sum(cell_ws) + gap*(len(images)-1) + 2*padding
            H = cell_h + 2*padding
        if max_h and H > max_h:
            scale = max_h / H
            cell_ws = [int(w*scale) for w in cell_ws]
            cell_h = int(cell_h*scale)
            W = sum(cell_ws) + gap*(len(images)-1) + 2*padding
            H = cell_h + 2*padding

        canvas = Image.new("RGBA", (max(1, W), max(1, H)), parse_color(bg_color))
        x = padding
        thumbs = []
        for im, cw in zip(images, cell_ws):
            thumbs.append(thumbs_from_images([im], (cw, cell_h), keep_aspect, parse_color(bg_color), border_px)[0])
        for th in thumbs:
            canvas.paste(th, (x, padding), th)
            x += th.width + gap
        return canvas.convert("RGB")

    elif layout == "Vertical strip":
        base_w = max(im.width for im in images)
        cell_w = min(base_w, 1000)
        ratioed = [im.height / im.width for im in images]
        cell_hs = [int(r * cell_w) for r in ratioed]
        W = cell_w + 2*padding
        H = sum(cell_hs) + gap*(len(images)-1) + 2*padding
        if max_w and W > max_w:
            scale = max_w / W
            cell_w = int(cell_w*scale)
            cell_hs = [int(h*scale) for h in cell_hs]
            W = cell_w + 2*padding
            H = sum(cell_hs) + gap*(len(images)-1) + 2*padding
        if max_h and H > max_h:
            scale = max_h / H
            cell_w = int(cell_w*scale)
            cell_hs = [int(h*scale) for h in cell_hs]
            W = cell_w + 2*padding
            H = sum(cell_hs) + gap*(len(images)-1) + 2*padding

        canvas = Image.new("RGBA", (max(1, W), max(1, H)), parse_color(bg_color))
        y = padding
        thumbs = []
        for im, ch in zip(images, cell_hs):
            thumbs.append(thumbs_from_images([im], (cell_w, ch), keep_aspect, parse_color(bg_color), border_px)[0])
        for th in thumbs:
            canvas.paste(th, (padding, y), th)
            y += th.height + gap
        return canvas.convert("RGB")

    else:  # Grid
        n = len(images)
        if rows == 0:
            # auto rows
            r = (n + int(cols) - 1) // int(cols)
        else:
            r = int(rows)
        c = int(cols)
        # pick a reasonable cell size
        # start from average aspect
        avg_w = int(sum(im.width for im in images) / n)
        avg_h = int(sum(im.height for im in images) / n)
        target_cell_w = min(400, avg_w)
        target_cell_h = min(400, avg_h)

        # compute canvas size
        W = c*target_cell_w + (c-1)*gap + 2*padding
        H = r*target_cell_h + (r-1)*gap + 2*padding
        # scale to fit constraints
        if max_w and W > max_w:
            scale = max_w / W
            target_cell_w = int(target_cell_w * scale)
            target_cell_h = int(target_cell_h * scale)
            W = c*target_cell_w + (c-1)*gap + 2*padding
            H = r*target_cell_h + (r-1)*gap + 2*padding
        if max_h and H > max_h:
            scale = max_h / H
            target_cell_w = int(target_cell_w * scale)
            target_cell_h = int(target_cell_h * scale)
            W = c*target_cell_w + (c-1)*gap + 2*padding
            H = r*target_cell_h + (r-1)*gap + 2*padding

        canvas = Image.new("RGBA", (max(1,W), max(1,H)), parse_color(bg_color))

        thumbs = thumbs_from_images(images, (target_cell_w, target_cell_h), keep_aspect, parse_color(bg_color), border_px)

        # paste row-major
        i = 0
        for rr in range(r):
            for cc in range(c):
                if i >= n: break
                x = padding + cc*(target_cell_w + gap)
                y = padding + rr*(target_cell_h + gap)
                th = thumbs[i]
                canvas.paste(th, (x, y), th)
                i += 1
        return canvas.convert("RGB")

if uploaded:
    # Load images with PIL
    images = []
    for file in uploaded:
        try:
            im = Image.open(file).convert("RGB")
            images.append(im)
        except Exception as e:
            st.error(f"Không mở được ảnh {file.name}: {e}")
    st.success(f"Đã tải {len(images)} ảnh.")
    if st.button("✅ Create Collage"):
        out = make_collage(images)
        if out is None:
            st.warning("Chưa có ảnh.")
        else:
            st.image(out, caption="Kết quả ghép", use_column_width=True)
            buf = io.BytesIO()
            out.save(buf, format="JPEG", quality=95, optimize=True)
            st.download_button("⬇️ Tải ảnh (.jpg)", data=buf.getvalue(), file_name="collage.jpg", mime="image/jpeg")
else:
    st.info("Hãy tải lên ít nhất 2 ảnh để bắt đầu.")
