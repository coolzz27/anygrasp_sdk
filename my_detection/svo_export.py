import sys
import pyzed.sl as sl
import numpy as np
import cv2
from pathlib import Path
import enum
import argparse
import os


class AppType(enum.Enum):
    LEFT_AND_RIGHT = 1
    LEFT_AND_DEPTH = 2
    LEFT_AND_DEPTH_16 = 3


def progress_bar(percent_done, bar_length=50):
    # Display a progress bar
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %i%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()


def svo_export():
    mode = 4
    # Get input parameters
    svo_input_path = "temp/video.svo2"
    output_dir = "data"
    avi_output_path = "data"
    output_as_video = False
    app_type = AppType.LEFT_AND_RIGHT
    if mode == 1 or mode == 3:
        app_type = AppType.LEFT_AND_DEPTH
    if mode == 4:
        app_type = AppType.LEFT_AND_DEPTH_16

    # Check if exporting to AVI or SEQUENCE
    if mode != 0 and mode != 1:
        output_as_video = False

    if not output_as_video and not os.path.isdir(output_dir):
        sys.stdout.write("Input directory doesn't exist. Check permissions or create it.\n",
                         output_dir, "\n")
        exit()

    # Specify SVO path parameter
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.QUALITY
    init_params.set_from_svo_file(svo_input_path)
    init_params.svo_real_time_mode = False  # Don't convert in realtime
    # Use milliliter units (for depth measurements)
    init_params.coordinate_units = sl.UNIT.MILLIMETER

    # Create ZED objects
    zed = sl.Camera()

    # Open the SVO file specified as a parameter
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        sys.stdout.write(repr(err))
        zed.close()
        exit()

    # Get image size
    image_size = zed.get_camera_information().camera_configuration.resolution
    width = image_size.width
    height = image_size.height
    width_sbs = width * 2

    # Prepare side by side image container equivalent to CV_8UC4
    svo_image_sbs_rgba = np.zeros((height, width_sbs, 4), dtype=np.uint8)

    # Prepare single image containers
    left_image = sl.Mat()
    right_image = sl.Mat()
    depth_image = sl.Mat()

    video_writer = None
    if output_as_video:
        # Create video writer with MPEG-4 part 2 codec
        video_writer = cv2.VideoWriter(avi_output_path,
                                       cv2.VideoWriter_fourcc(
                                           'M', '4', 'S', '2'),
                                       max(zed.get_camera_information(
                                       ).camera_configuration.fps, 25),
                                       (width_sbs, height))
        if not video_writer.isOpened():
            sys.stdout.write("OpenCV video writer cannot be opened. Please check the .avi file path and write "
                             "permissions.\n")
            zed.close()
            exit()

    rt_param = sl.RuntimeParameters()

    # Start SVO conversion to AVI/SEQUENCE
    sys.stdout.write("Converting SVO... Use Ctrl-C to interrupt conversion.\n")

    nb_frames = zed.get_svo_number_of_frames()

    while True:
        err = zed.grab(rt_param)
        if err == sl.ERROR_CODE.SUCCESS:
            svo_position = zed.get_svo_position()

            # Retrieve SVO images
            zed.retrieve_image(left_image, sl.VIEW.LEFT)

            if app_type == AppType.LEFT_AND_RIGHT:
                zed.retrieve_image(right_image, sl.VIEW.RIGHT)
            elif app_type == AppType.LEFT_AND_DEPTH:
                zed.retrieve_image(right_image, sl.VIEW.DEPTH)
            elif app_type == AppType.LEFT_AND_DEPTH_16:
                zed.retrieve_measure(depth_image, sl.MEASURE.DEPTH)

            # Generate file names
            filename1 = output_dir + "/color.png"
            if app_type == AppType.LEFT_AND_DEPTH_16:
                filename2 = output_dir + "/depth.png"
            else:
                filename2 = output_dir + "/" + (("right%s.png" if app_type == AppType.LEFT_AND_RIGHT
                                                 else "depth%s.png") % str(svo_position).zfill(3))
            # Save Left images
            cv2.imwrite(str(filename1), left_image.get_data())

            if app_type != AppType.LEFT_AND_DEPTH_16:
                # Save right images
                cv2.imwrite(str(filename2), right_image.get_data())
            else:
                # Save depth images (convert to uint16)
                cv2.imwrite(str(filename2),
                            depth_image.get_data().astype(np.uint16))
                # np.save(str(filename2), depth_image.get_data())

            # Display progress
            progress_bar((svo_position + 1) / nb_frames * 100, 30)
        if err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            progress_bar(100, 30)
            sys.stdout.write("\nSVO end has been reached. Exiting now.\n")
            break
    if output_as_video:
        # Close the video writer
        video_writer.release()

    zed.close()
    return 0


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         formatter_class=argparse.RawTextHelpFormatter)
#     parser.add_argument('--mode', type=int, required=True, help=" Mode 0 is to export LEFT+RIGHT AVI. \n Mode 1 is to export LEFT+DEPTH_VIEW Avi. \n Mode 2 is to export LEFT+RIGHT image sequence. \n Mode 3 is to export LEFT+DEPTH_View image sequence. \n Mode 4 is to export LEFT+DEPTH_16BIT image sequence.")
#     parser.add_argument('--input_svo_file', type=str,
#                         required=True, help='Path to the .svo file')
#     parser.add_argument('--output_avi_file', type=str,
#                         help='Path to the output .avi file, if mode includes a .avi export', default='')
#     parser.add_argument('--output_path_dir', type=str,
#                         help='Path to a directory, where .png will be written, if mode includes image sequence export', default='')
#     opt = parser.parse_args()
#     if opt.mode > 4 or opt.mode < 0:
#         print("Mode shoud be between 0 and 4 included. \n Mode 0 is to export LEFT+RIGHT AVI. \n Mode 1 is to export LEFT+DEPTH_VIEW Avi. \n Mode 2 is to export LEFT+RIGHT image sequence. \n Mode 3 is to export LEFT+DEPTH_View image sequence. \n Mode 4 is to export LEFT+DEPTH_16BIT image sequence.")
#         exit()
#     if not opt.input_svo_file.endswith(".svo") and not opt.input_svo_file.endswith(".svo2"):
#         print("--input_svo_file parameter should be a .svo file but is not : ",
#               opt.input_svo_file, "Exit program.")
#         exit()
#     if not os.path.isfile(opt.input_svo_file):
#         print("--input_svo_file parameter should be an existing file but is not : ",
#               opt.input_svo_file, "Exit program.")
#         exit()
#     if opt.mode < 2 and len(opt.output_avi_file) == 0:
#         print("In mode ", opt.mode,
#               ", output_avi_file parameter needs to be specified.")
#         exit()
#     if opt.mode < 2 and not opt.output_avi_file.endswith(".avi"):
#         print("--output_avi_file parameter should be a .avi file but is not : ",
#               opt.output_avi_file, "Exit program.")
#         exit()
#     if opt.mode >= 2 and len(opt.output_path_dir) == 0:
#         print("In mode ", opt.mode,
#               ", output_path_dir parameter needs to be specified.")
#         exit()
#     if opt.mode >= 2 and not os.path.isdir(opt.output_path_dir):
#         print("--output_path_dir parameter should be an existing folder but is not : ",
#               opt.output_path_dir, "Exit program.")
#         exit()
#     main()
