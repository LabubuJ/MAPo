import os
import shutil

def rename_images():
    # 基础目录
    base_dir = "D:/AAAI2026/anonymous_github/MAPo/static/images/MAPo/ablation_show/jitter_show/flame_salmon_frag3/processed/bbox"
    
    # 需要处理的子目录
    subdirs = ['jitter', '+cur', 'dejitter_3']
    
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir).replace('\\', '/')
        if not os.path.exists(dir_path):
            print(f"目录不存在: {dir_path}")
            continue
            
        print(f"\n处理目录: {dir_path}")
        
        # 遍历0-9的文件
        for i in range(10):
            old_name = f"{i:05d}.png"  # 00000.png to 00009.png
            new_name = f"{i+70:05d}.png"  # 00070.png to 00079.png
            
            old_path = os.path.join(dir_path, old_name).replace('\\', '/')
            new_path = os.path.join(dir_path, new_name).replace('\\', '/')
            
            if os.path.exists(old_path):
                try:
                    # 使用copy2保留文件元数据
                    shutil.copy2(old_path, new_path)
                    os.remove(old_path)
                    print(f"已重命名: {old_name} -> {new_name}")
                except Exception as e:
                    print(f"重命名失败 {old_name}: {str(e)}")
            else:
                print(f"文件不存在: {old_path}")

if __name__ == "__main__":
    rename_images() 