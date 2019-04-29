from PIL import Image
import numpy as np
import cv2

class ColorShades:

    def __int__(self):
        pass

    def create_color_shades_rgb(self, color_value=(255, 0, 0), step=1, color_list=[]):
        total_shades_list = np.array([0,0,0])
        for color_value in color_list:
            black_img = np.zeros((100, 100, 3))
            white_img = black_img.copy()+255
            final_array = np.zeros((21, 100, 3))
            main_color = white_img.copy()
            main_color[:, :, 0] = color_value[0]
            main_color[:, :, 1] = color_value[1]
            main_color[:, :, 2] = color_value[2]
            for i in range(0, 10):
                white_blended_img = cv2.addWeighted(main_color, i/10, white_img, (10-i)/10, 0)
                black_blended_img = cv2.addWeighted(main_color, i/10, black_img, (10-i)/10, 0)
                final_array[i,:,0] = white_blended_img[1,:,0]
                final_array[i,:,1] = white_blended_img[1,:,1]
                final_array[i,:,2] = white_blended_img[1,:,2]

                final_array[20-i,:,0] = black_blended_img[1,:,0]
                final_array[20-i,:,1] = black_blended_img[1,:,1]
                final_array[20-i,:,2] = black_blended_img[1,:,2]
            shades_array = final_array[:,0]
            total_shades_list = np.vstack((total_shades_list, shades_array))
            i = Image.fromarray(final_array.astype('uint8'))
            i.save(str(color_value)+'.png')

        total_img = Image.fromarray(total_shades_list.astype('uint8'))
        # total_img.save('total.png')
        return np.hstack((total_shades_list,total_shades_list,total_shades_list,total_shades_list,total_shades_list)), total_shades_list

    def create_shades_of_color(self, color_value_list, steps):
        final_array = np.zeros((1, 3))
        for each in color_value_list:
            each = np.array(each)

            shades_img = Image.new('HSV', (30, 256))
            pixmap = shades_img.load()
            for i in range(0, shades_img.height):
                for j in range(0, shades_img.width):
                    pixmap[j, i] = (each[0], each[1], i)
            shades_array = np.asarray(shades_img)[:,0]
            final_array = np.vstack((final_array, shades_array))
            # shades_img = shades_img.convert('RGB')
            # shades_img.save(str(each)+'.png')

        hue_diff = max(color_value_list[0][0], color_value_list[1][0]) - min(color_value_list[0][0], color_value_list[1][0])
        sat_diff = max(color_value_list[0][1], color_value_list[1][1]) - min(color_value_list[0][1], color_value_list[1][1])

        for i in range(1, hue_diff):
            if color_value_list[0][0] < color_value_list[1][0]:
                interpolated_color = np.array([color_value_list[0][0]+i, color_value_list[0][1], color_value_list[0][2]])
                final_array = np.vstack((final_array, interpolated_color))
            else:
                interpolated_color = np.array([color_value_list[1][0]+i, color_value_list[1][1], color_value_list[1][2]])
                final_array = np.vstack((final_array, interpolated_color))

        for i in range(1, sat_diff):
            if color_value_list[0][1] < color_value_list[1][1]:
                interpolated_color = np.array([color_value_list[0][0], color_value_list[0][1]+i, color_value_list[0][2]])
                final_array = np.vstack((final_array, interpolated_color))
            else:
                interpolated_color = np.array([color_value_list[1][0], color_value_list[1][1]+i, color_value_list[1][2]])
                final_array = np.vstack((final_array, interpolated_color))
        print(final_array.shape)
        final_shades_img = Image.new('HSV', (30, final_array.shape[0]))
        final_shades_pixmap = final_shades_img.load()
        for i in range(0, final_shades_img.height):
            for j in range(0, final_shades_img.width):
                final_shades_pixmap[j, i] = tuple(final_array[i].astype('uint8'))
        final_shades_img = final_shades_img.convert('RGB')
        final_shades_img.save('usedshades.png')
        return np.asarray(shades_img.convert('RGB')), final_array

    def replicate_image_with_new_shades(self, shades_array, img):
        image = Image.fromarray(img).convert('RGB')
        new_image = Image.new('RGB', image.size)

        image_pixmap = image.load()
        new_image_pixmap = new_image.load()

        for i in range(0, image.width):
            for j in range(0, image.height):
                current_pixel = image_pixmap[i, j]
                new_image_pixmap[i, j] = self.compute_distance_and_return(shades_array, current_pixel)

        # new_image = new_image.convert('RGB')
        new_image.save('replaced.png')
        return np.asarray(new_image)

    def compute_distance_and_return(self, shades_array, target_color):
        copy_array = shades_array.copy()
        copy_array[:, 0] = target_color[0]
        copy_array[:, 1] = target_color[1]
        copy_array[:, 2] = target_color[2]
        distance = np.linalg.norm(shades_array - copy_array, axis=1)
        index = np.where(distance == distance.min())
        most_nearest_color = shades_array[index, :][0][0]
        return tuple(most_nearest_color.astype('uint8'))

# if __name__ == "__main__":
#     colorShades = ColorShades()
    # a, shades_array = colorShades.create_shades_of_color((17, 144, 50), 'a')
    # colorShades.compute_distance_and_return(shades_array, (17, 144, 50))

    # colorShades.create_color_shades_rgb()