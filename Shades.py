from PIL import Image
import numpy as np


class ColorShades:

    def __int__(self):
        pass

    def create_shades_of_color(self, color_value, steps):
        color_value = np.array(color_value)

        shades_img = Image.new('HSV', (30, 256))
        pixmap = shades_img.load()
        for i in range(0, shades_img.height):
            for j in range(0, shades_img.width):
                pixmap[j, i] = (color_value[0], color_value[1], i)
        shades_array = np.asarray(shades_img)[:,0]
        shades_img = shades_img.convert('RGB')
        return np.asarray(shades_img), shades_array

    def replicate_image_with_new_shades(self, shades_array, img):
        image = Image.fromarray(img).convert('HSV')
        new_image = Image.new('HSV', image.size)

        image_pixmap = image.load()
        new_image_pixmap = new_image.load()

        for i in range(0, image.width):
            for j in range(0, image.height):
                current_pixel = image_pixmap[i, j]
                new_image_pixmap[i, j] = self.compute_distance_and_return(shades_array, current_pixel)

        new_image = new_image.convert('RGB')
        new_image.save('replaced.png')

    def compute_distance_and_return(self, shades_array, target_color):
        copy_array = shades_array.copy()
        copy_array[:, 0] = target_color[0]
        copy_array[:, 1] = target_color[1]
        copy_array[:, 2] = target_color[2]
        distance = np.linalg.norm(shades_array - copy_array, axis=1)
        index = np.where(distance == distance.min())
        most_nearest_color = shades_array[index, :][0][0]
        return tuple(most_nearest_color)

# if __name__ == "__main__":
#     colorShades = ColorShades()
#     a, shades_array = colorShades.create_shades_of_color((17, 144, 50), 'a')
#     colorShades.compute_distance_and_return(shades_array, (17, 144, 50))