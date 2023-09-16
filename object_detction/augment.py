import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, save_img

def augment_images(directory, output_dir, prefix, total_images=400):
    datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

    image_list = os.listdir(directory)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    images_to_generate = total_images // len(image_list)

    for image_name in image_list:
        image_path = os.path.join(directory, image_name)
        image = load_img(image_path)
        x = img_to_array(image)
        x = x.reshape((1,) + x.shape)

        i = 0
        for batch in datagen.flow(x, batch_size=1,
                                  save_to_dir=output_dir,
                                  save_prefix=prefix,
                                  save_format='jpeg'):
            i += 1
            if i > images_to_generate:
                break

if __name__ == "__main__":
    augment_images('/home/mkopcz/Desktop/wno10/driver', '/home/mkopcz/Desktop/wno10/augmented', 'aug', 400)
