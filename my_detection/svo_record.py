import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import argparse
import os

cam = sl.Camera()

# Handler to deal with CTRL+C properly


def handler(signal_received, frame):
    cam.disable_recording()
    cam.close()
    sys.exit(0)


signal(SIGINT, handler)


def svo_record():
    output_svo_file = "./temp/video.svo2"

    init = sl.InitParameters()
    init.depth_mode = sl.DEPTH_MODE.NONE  # Set configuration parameters for the ZED
    init.camera_resolution = sl.RESOLUTION.HD1080

    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print("Camera Open", status, "Exit program.")
        exit(1)

    # Enable recording with the filename specified in argument
    recording_param = sl.RecordingParameters(
        output_svo_file, sl.SVO_COMPRESSION_MODE.H264)
    err = cam.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED : ", err)
        exit(1)

    runtime = sl.RuntimeParameters()
    # Start recording SVO, stop with Ctrl-C command
    print("SVO is Recording, use Ctrl-C to stop.")
    frames_recorded = 0

    if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS:
        frames_recorded += 1
        print("Frame count: " + str(frames_recorded), end="\r")
        data = sl.SVOData()
        data.key = "TEST"
        data.set_string_content(
            "Hello, SVO World >> " + str(cam.get_timestamp(sl.TIME_REFERENCE.IMAGE).data_ns))
        data.timestamp_ns = cam.get_timestamp(sl.TIME_REFERENCE.IMAGE)
        print('INGEST', cam.ingest_data_into_svo(data))
    # while frames_recorded < 100:
    #     # Check that a new image is successfully acquired

    cam.close()


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--output_svo_file', type=str,
#                         help='Path to the SVO file that will be written', required=True)
#     opt = parser.parse_args()
#     if not opt.output_svo_file.endswith(".svo") and not opt.output_svo_file.endswith(".svo2"):
#         print("--output_svo_file parameter should be a .svo file but is not : ",
#               opt.output_svo_file, "Exit program.")
#         exit()
#     main()
