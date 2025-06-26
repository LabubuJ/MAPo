from pdf2image import convert_from_path
import os

def convert_pdf_to_png(pdf_path, output_dir, poppler_path=None, dpi=300):
    """
    将PDF文件转换为PNG图片
    :param pdf_path: PDF文件路径
    :param output_dir: 输出目录
    :param poppler_path: poppler的bin目录路径
    :param dpi: 输出图片的DPI(默认300,质量较好)
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 转换PDF为图片
        images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
        
        # 获取PDF文件名(不含扩展名)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # 如果PDF只有一页,直接使用文件名
        if len(images) == 1:
            output_path = os.path.join(output_dir, f"{pdf_name}.png")
            images[0].save(output_path, "PNG")
            print(f"转换成功! 已保存到: {output_path}")
        else:
            # 如果PDF有多页,为每页添加页码
            for i, image in enumerate(images):
                output_path = os.path.join(output_dir, f"{pdf_name}_page_{i+1}.png")
                image.save(output_path, "PNG")
            print(f"转换成功! 共转换{len(images)}页,已保存到: {output_dir}")
            
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        print("\n请确保已正确安装poppler:")
        print("1. 下载poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("2. 解压到某个目录(比如 C:\\poppler)")
        print("3. 将poppler的bin目录(比如 C:\\poppler\\Library\\bin)设置为poppler_path")

if __name__ == "__main__":
    # 设置路径
    pdf_path = "D:\\AAAI2026\\anonymous_github\\MAPo\\static\\images\\MAPo\\quanlitative_cmp.pdf"
    output_dir = "D:\\AAAI2026\\anonymous_github\\MAPo\\static\\images\\MAPo"
    
    # 设置poppler路径 - 使用实际安装路径
    poppler_path = "D:\\AAAI2026\\anonymous_github\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin"
    
    # 执行转换
    convert_pdf_to_png(pdf_path, output_dir, poppler_path=poppler_path) 