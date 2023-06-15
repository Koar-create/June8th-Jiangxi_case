from PIL import Image

def crop_image(image_path):
    # 打开图像
    image = Image.open(image_path)

    # 获取图像宽度和高度
    width, height = image.size

    # 计算裁剪后的宽度
    new_width = int(width * 0.75)

    # 创建一个新的图像对象，尺寸为裁剪后的尺寸
    new_image = Image.new("RGB", (new_width, height))

    # 裁剪图像
    new_image.paste(image.crop((0, 0, new_width, height)), (0, 0))

    # 保存裁剪后的图像
    new_image.save("D:\\Desktop\\cropped_Image_1.png")

    # 关闭图像
    image.close()
    new_image.close()

# 调用函数进行图像裁剪
crop_image("D:\\Desktop\\Figure_1.png")