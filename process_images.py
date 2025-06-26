import cv2
import numpy as np
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

class ImageProcessor:
    def __init__(self):
        self.cropping = False
        self.x_start, self.y_start, self.x_end, self.y_end = 0, 0, 0, 0
        self.crop_roi = None  # [x_start, y_start, x_end, y_end] relative to original image
        self.drawing_bbox = False
        self.bboxes = [] # BBoxes relative to the displayed (scaled) cropped image
        self.current_bbox = []
        self.image = None # The image currently displayed (scaled)
        self.original_image = None # The full, original image
        self.scale_factor = 0.5  # 缩放因子
        self.window_name = "Image Processing - Crop"
        self.bbox_window_name = "BBox Selection"
        
    def scale_coordinates(self, x, y, to_original=False):
        """坐标转换函数：在显示尺寸和图片原始尺寸之间转换"""
        if to_original:
            return int(x / self.scale_factor), int(y / self.scale_factor)
        else:
            return int(x * self.scale_factor), int(y * self.scale_factor)
    
    def resize_image(self, image):
        """根据scale_factor缩放图片用于显示"""
        height, width = image.shape[:2]
        new_height = int(height * self.scale_factor)
        new_width = int(width * self.scale_factor)
        return cv2.resize(image, (new_width, new_height))

    def mouse_crop(self, event, x, y, flags, param):
        """用于裁剪原始大图的鼠标回调"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.cropping = True
            self.x_start, self.y_start = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.cropping:
                img_copy = self.image.copy()
                cv2.rectangle(img_copy, (self.x_start, self.y_start), (x, y), (0, 255, 0), 2)
                cv2.imshow(self.window_name, img_copy)
        elif event == cv2.EVENT_LBUTTONUP:
            self.cropping = False
            self.x_end, self.y_end = x, y
            # 确保 start < end
            if self.x_end < self.x_start:
                self.x_start, self.x_end = self.x_end, self.x_start
            if self.y_end < self.y_start:
                self.y_start, self.y_end = self.y_end, self.y_start
            
            # 将显示坐标转换回原始大图的坐标并保存
            x_start_orig, y_start_orig = self.scale_coordinates(self.x_start, self.y_start, to_original=True)
            x_end_orig, y_end_orig = self.scale_coordinates(self.x_end, self.y_end, to_original=True)
            self.crop_roi = [x_start_orig, y_start_orig, x_end_orig, y_end_orig]

    def mouse_bbox(self, event, x, y, flags, param):
        """用于在裁剪后的图片上标注BBox的鼠标回调"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing_bbox = True
            self.current_bbox = [x, y]
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing_bbox:
                img_copy = self.image.copy()
                # 绘制已保存的框
                for bbox in self.bboxes:
                    cv2.rectangle(img_copy, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)  # 红色，线宽3
                # 绘制当前正在画的框
                cv2.rectangle(img_copy, (self.current_bbox[0], self.current_bbox[1]), (x, y), (0, 255, 0), 2)
                cv2.imshow(self.bbox_window_name, img_copy)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing_bbox = False
            x_end, y_end = x, y
            # 确保 start < end
            if x_end < self.current_bbox[0]:
                self.current_bbox[0], x_end = x_end, self.current_bbox[0]
            if y_end < self.current_bbox[1]:
                self.current_bbox[1], y_end = y_end, self.current_bbox[1]
            
            # 保存相对于显示图像的坐标
            self.bboxes.append([self.current_bbox[0], self.current_bbox[1], x_end, y_end])
            
            # 更新显示
            img_copy = self.image.copy()
            for bbox in self.bboxes:
                cv2.rectangle(img_copy, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)  # 红色，线宽3
            cv2.imshow(self.bbox_window_name, img_copy)

    def crop_image(self, image_path, output_path):
        """让用户在第一张图上选择裁剪区域"""
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            print(f"无法读取图片: {image_path}")
            return False

        self.image = self.resize_image(self.original_image)
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_crop)
        
        while True:
            display_img = self.image.copy()
            # 如果已有选区，在显示图上画出来
            if self.crop_roi:
                x1_display, y1_display = self.scale_coordinates(self.crop_roi[0], self.crop_roi[1])
                x2_display, y2_display = self.scale_coordinates(self.crop_roi[2], self.crop_roi[3])
                cv2.rectangle(display_img, (x1_display, y1_display), (x2_display, y2_display), (0, 255, 0), 2)
            cv2.imshow(self.window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') and self.crop_roi:  # 按c确认裁剪
                cropped = self.original_image[self.crop_roi[1]:self.crop_roi[3], self.crop_roi[0]:self.crop_roi[2]]
                cv2.imwrite(output_path, cropped)
                print(f"裁剪区域已设定并保存第一张裁剪图: {os.path.basename(output_path)}")
                cv2.destroyWindow(self.window_name)
                return True
            elif key == ord('q'):  # 按q退出
                cv2.destroyWindow(self.window_name)
                return False

    def draw_bboxes(self, images_paths, output_dir, subdirs_map):
        """让用户在裁剪后的图片上画BBox，并将带框的图片保存"""
        self.bboxes = []
        if not images_paths:
            return
            
        # 使用第一张裁剪后的图片作为BBox标注的模板
        template_image_path = images_paths[0]
        template_image = cv2.imread(template_image_path)
        if template_image is None:
            print(f"无法读取图片: {template_image_path}")
            return

        # self.image 是用于显示的缩放图
        self.image = self.resize_image(template_image)

        cv2.namedWindow(self.bbox_window_name)
        cv2.setMouseCallback(self.bbox_window_name, self.mouse_bbox)
        
        print("\n在模板图上框选目标区域. 按's'保存所有框选结果, 'r'重置, 'q'退出.")
        
        while True:
            display_img = self.image.copy()
            # 绘制所有已确定的BBox
            for bbox in self.bboxes:
                cv2.rectangle(display_img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 3)  # 红色，线宽3
            cv2.imshow(self.bbox_window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # 保存结果
                if not self.bboxes:
                    print("没有框选任何区域，操作取消。")
                    cv2.destroyWindow(self.bbox_window_name)
                    return

                # BBox是在裁剪后的图片上画的，所以只需将坐标从显示尺寸转换回裁剪后图片的原始尺寸
                final_bboxes = []
                for bbox in self.bboxes:
                    x1, y1 = self.scale_coordinates(bbox[0], bbox[1], to_original=True)
                    x2, y2 = self.scale_coordinates(bbox[2], bbox[3], to_original=True)
                    final_bboxes.append([x1, y1, x2, y2])
                
                print("\n正在保存带BBox标注的图片...")

                # 遍历所有需要处理的(已裁剪的)图片
                for i, img_path in enumerate(images_paths):
                    # 读取对应的已裁剪图片
                    img = cv2.imread(img_path)
                    if img is None:
                        print(f"警告: 无法读取 {img_path}, 跳过。")
                        continue
                    
                    # 获取该图片对应的子目录名
                    subdir = subdirs_map[img_path]
                    # 获取该子目录在bbox输出目录下的路径
                    subdir_bbox_dir = os.path.join(output_dir, subdir)
                    
                    # 在图片上画出所有BBox
                    img_with_bbox = img.copy()
                    for bbox in final_bboxes:
                        cv2.rectangle(img_with_bbox, 
                                    (bbox[0], bbox[1]), 
                                    (bbox[2], bbox[3]), 
                                    (0, 0, 255),  # 红色 (BGR格式)
                                    3)  # 线宽增加到3
                    
                    # 获取原始文件名中的数字部分
                    original_filename = os.path.basename(img_path)
                    file_number = int(os.path.splitext(original_filename)[0].split('_')[-1])
                    # 生成新的文件名 (70-79)
                    new_filename = f"{file_number:05d}.png"
                    output_path = os.path.join(subdir_bbox_dir, new_filename)
                    
                    cv2.imwrite(output_path, img_with_bbox)
                    print(f"已保存: {output_path}")
                
                print("所有带BBox标注的图片保存完毕！")
                cv2.destroyWindow(self.bbox_window_name)
                return
            elif key == ord('r'):  # 重置所有框
                self.bboxes = []
                print("所有框已重置。")
            elif key == ord('q'):  # 退出
                cv2.destroyWindow(self.bbox_window_name)
                return

def process_directory():
    root = tk.Tk()
    root.withdraw()
    main_dir = filedialog.askdirectory(title="选择要处理的主目录")
    if not main_dir:
        return
    
    # 过滤掉我们自己创建的目录
    subdirs = [d for d in os.listdir(main_dir) 
              if os.path.isdir(os.path.join(main_dir, d)) 
              and d not in ['processed']]
    
    if not subdirs:
        messagebox.showinfo("提示", "在所选目录中没有找到有效的子目录。")
        return
        
    # 创建processed目录用于存放裁剪后的大图
    processed_dir = os.path.join(main_dir, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    # 创建bbox目录用于存放最终的小图
    bbox_dir = os.path.join(processed_dir, 'bbox')
    os.makedirs(bbox_dir, exist_ok=True)
    
    processor = ImageProcessor()
    
    # 收集所有需要处理的图片信息
    all_images = []
    print("\n正在收集图片...")
    for subdir in subdirs:
        subdir_path = os.path.join(main_dir, subdir)
        images = [f for f in os.listdir(subdir_path) 
                 if os.path.isfile(os.path.join(subdir_path, f)) 
                 and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if not images:
            continue
            
        # 为当前子目录创建对应的processed目录
        subdir_processed = os.path.join(processed_dir, subdir)
        os.makedirs(subdir_processed, exist_ok=True)
        
        for img in images:
            img_path = os.path.join(subdir_path, img)
            output_path = os.path.join(subdir_processed, f"cropped_{Path(img).stem}.png") # 统一保存为png
            all_images.append({'original_path': img_path, 'cropped_path': output_path, 'subdir': subdir})
    
    if not all_images:
        messagebox.showinfo("提示", "未找到任何支持的图片文件。")
        return
    
    # 使用第一张图片设置统一的裁剪区域
    print("\n--- 步骤 1: 设置统一裁剪区域 ---")
    print("在弹出的窗口中用鼠标拖拽一个矩形区域。")
    print("按 'c' 键确认区域并继续, 按 'q' 键退出程序。")
    
    first_img_info = all_images[0]
    if not processor.crop_image(first_img_info['original_path'], first_img_info['cropped_path']):
        print("用户取消或未能设置裁剪区域，程序退出。")
        return
    
    # 对所有其他图片应用相同的裁剪区域
    print("\n正在使用相同的区域裁剪所有图片...")
    crop_roi = processor.crop_roi
    for img_info in all_images[1:]:
        img = cv2.imread(img_info['original_path'])
        if img is not None:
            try:
                # 使用已确定的 crop_roi 进行裁剪
                cropped = img[crop_roi[1]:crop_roi[3], crop_roi[0]:crop_roi[2]]
                cv2.imwrite(img_info['cropped_path'], cropped)
                # print(f"已裁剪: {os.path.basename(img_info['cropped_path'])}")
            except Exception as e:
                print(f"裁剪失败: {os.path.basename(img_info['original_path'])} - {e}")
    print("所有图片裁剪完成！")

    # 询问哪些子目录需要进行BBox标注
    print("\n--- 步骤 2: 选择需要标注BBox的目录 ---")
    dirs_for_bbox = []
    for subdir in subdirs:
        # 确保该子目录有图片被处理了
        if any(img['subdir'] == subdir for img in all_images):
            if messagebox.askyesno("BBox标注确认", f"是否需要对 '{subdir}' 目录的图片进行BBox标注？"):
                dirs_for_bbox.append(subdir)
    
    if not dirs_for_bbox:
        print("\n没有选择任何目录进行BBox标注。")
    else:
        print(f"\n将对以下目录进行BBox标注: {', '.join(dirs_for_bbox)}")
        print("\n--- 步骤 3: 标注BBox ---")
        print("将在第一张裁剪后的图片上设置统一的BBox模板。")
        print("这些BBox模板将应用到所有选中目录的图片上。")
        
        # 收集需要添加bbox的图片（已裁剪的图片）
        bbox_images_paths = []
        subdirs_map = {} # 映射：cropped_path -> subdir
        
        # 找到第一个属于待处理目录的图片作为模板
        first_image_for_bbox_found = False
        for img_info in all_images:
            if img_info['subdir'] in dirs_for_bbox:
                if not first_image_for_bbox_found:
                    # 将它移到列表开头，作为模板
                    bbox_images_paths.insert(0, img_info['cropped_path'])
                    first_image_for_bbox_found = True
                else:
                    bbox_images_paths.append(img_info['cropped_path'])
                subdirs_map[img_info['cropped_path']] = img_info['subdir']
        
        if bbox_images_paths:
            # 为需要bbox的目录创建对应的输出子目录
            for subdir in dirs_for_bbox:
                os.makedirs(os.path.join(bbox_dir, subdir), exist_ok=True)
            
            processor.draw_bboxes(bbox_images_paths, bbox_dir, subdirs_map)
    
    print("\n处理完成！结果已保存在 'processed' 目录中。")
    messagebox.showinfo("完成", "所有处理已完成！")

if __name__ == "__main__":
    process_directory()