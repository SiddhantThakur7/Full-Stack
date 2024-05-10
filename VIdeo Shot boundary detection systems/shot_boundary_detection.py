import cv2
import os
from PIL import Image, ImageTk
import PySimpleGUI as sg
import tempfile
import threading
import time
import re
import numpy as np


# CustomPhotoImage class inherits from ImageTk.PhotoImage and has a __del__ method for cleanup
class CustomPhotoImage(ImageTk.PhotoImage):
    def __del__(self):
        try:
            # Attempt to access the __photo attribute
            name = self.__photo.name
        except AttributeError:
            # Ignore AttributeError if __photo attribute is not present
            pass
        except Exception as e:
            # Handle other exceptions as needed
            print(f"Exception in CustomPhotoImage __del__: {e}")


# VideoPlayerApp class for creating and managing the video player application
class VideoPlayerApp:
    def __init__(self):
        # Layout
        # PySimpleGUI layout for the application
        # Contains buttons, an image viewer, and other UI elements
        # Buttons for selecting video, play/pause, executing functions, and navigation
        # Also includes a grid of buttons for displaying video frames
        # Elements are organized using PySimpleGUI's layout structure
        image_element = sg.Image(filename="", key="image")
        timestamp_label = sg.Text(
            "", key="timestamp_label", size=(20, 1), justification="center"
        )
        button_size = (10, 3)
        button_font = ("Helvetica", 8)

        # Update the number of buttons per row and columns
        self.buttons_per_row = 8
        self.columns = 4  # Number of columns
        self.visibility = False
        self.total_buttons = self.buttons_per_row * self.columns

        layout = [
            [sg.Column([], size=(550, 1)), sg.Image(filename="", key="image")],
            [sg.Column([], size=(650, 1)), timestamp_label],
            [
                sg.Column([], size=(575, 1)),
                sg.Button("Select Video", key="select_video"),
                sg.Button("Play/Pause", key="play_pause"),
                sg.Button("Execute", key="execute"),
                sg.Button("Close", key="close"),
            ],
            *[
                [
                    sg.Column(
                        [
                            [
                                sg.Button(
                                    "",
                                    key=f"button_{i}_{j}",
                                    size=(0, 0),
                                    pad=(2, 2),
                                    border_width=5,
                                    visible=self.visibility,
                                    button_color=("white", sg.theme_text_color()),
                                ),
                                sg.Text(
                                    "",
                                    size=(10, 1),
                                    key=f"frame_text_{i}_{j}",
                                    visible=self.visibility,
                                    justification="center",
                                    font=("Helvetica", 8),
                                ),
                            ]
                        ]
                    )
                    for j in range(self.buttons_per_row)
                ]
                for i in range(self.columns)
            ],
            [
                sg.Button("<< Prev", key="prev_page"),
                sg.Button("Next >>", key="next_page"),
            ],
        ]

        self.window = sg.Window(
            "Video Player App", layout, resizable=True, finalize=True
        )
        self.video_viewer = self.window["image"]
        self.timestamp_label = self.window["timestamp_label"]
        self.endframe = 5000
        self.startframe = 1000
        self.select_video_button = self.window["select_video"]
        self.play_pause_button = self.window["play_pause"]
        self.execute_button = self.window["execute"]
        self.close_button = self.window["close"]
        self.prev_page_button = self.window["prev_page"]
        self.next_page_button = self.window["next_page"]

        self.image_buttons = [
            [self.window[f"button_{i}_{j}"] for j in range(self.buttons_per_row)]
            for i in range(self.columns)
        ]

        self.frame_text = [
            [self.window[f"frame_text_{i}_{j}"] for j in range(self.buttons_per_row)]
            for i in range(self.columns)
        ]

        self.current_page = 1
        self.images_per_page = self.total_buttons
        self.total_images = 30
        self.total_pages = (
            self.total_images + self.images_per_page - 1
        ) // self.images_per_page

        self.cap = None
        self.is_paused = False
        self.video_thread = None
        self.stop_video_thread = threading.Event()

        # Temporary directory to save images
        self.temp_dir = tempfile.TemporaryDirectory()

        # Add lock for threading
        self.cap_lock = threading.Lock()

        # Store the path of the initially selected video
        self.initial_video_path = None

        # Set the 'Execute' button initially to be hidden
        self.execute_button.update(visible=False)

    # Method to update a specific button with frame information
    def update_video_frame(self, button_row, button_col, frame_number):
        if frame_number is not None:
            self.image_buttons[button_row][button_col].update(image_filename=None)
            self.frame_text[button_row][button_col].update(
                value=f"Frame {frame_number}"
            )
        else:
            self.image_buttons[button_row][button_col].update(image_filename="")
            self.frame_text[button_row][button_col].update(value="")

    # Method to load a video for a specific button
    def load_video_for_button(
        self,
        file_path=None,
        frame_number=None,
        button_row=None,
        button_col=None,
        frame_index_new=None,
    ):
        # Stop and close the existing video player
        self.stop_and_close_video_player()

        if file_path is None:
            file_path = self.initial_video_path
        if file_path:
            self.cap = cv2.VideoCapture(file_path)
            if frame_number is not None:
                # Set the frame number for the video player
                with self.cap_lock:
                    if 0 <= frame_index_new < len(frame_number):
                        self.cap.set(
                            cv2.CAP_PROP_POS_FRAMES, frame_number[frame_index_new]
                        )
                        self.endframe = (
                            frame_number[frame_index_new + 1]
                            if frame_index_new + 1 < len(frame_number)
                            else 5000
                        )
                        self.startframe = frame_number[frame_index_new]

                        # Introduce a small delay to allow the video player to start
                        time.sleep(0.5)

                        self.play_video()
                    else:
                        print(
                            f"frame_index_new {frame_index_new} is out of range. Setting self.endframe = 5000"
                        )
                        self.endframe = 5000

    def run(self):
        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED or event == "close":
                self.stop_and_close_video_player()
                break
            elif event == "select_video":
                self.load_video()
            elif event == "play_pause":
                self.play_pause_video()
            elif event == "execute":
                self.execute_function()
            elif event == "prev_page":
                self.prev_page()
            elif event == "next_page":
                self.next_page()
            elif event == "_UPDATE_IMAGE_":
                self.video_viewer.update(data=values[event])
                timestamp = self.get_current_video_timestamp()
                self.timestamp_label.update(value=f"Timestamp: {timestamp}")
            elif event.startswith("button_"):
                button_info = event.split("_")[1:]
                if len(button_info) == 2:
                    button_row, button_col = map(int, button_info)
                    frame_index = (
                        (self.current_page - 1) * self.images_per_page
                        + button_row * self.buttons_per_row
                        + button_col
                    )
                    frames_file_path = os.path.abspath("merged.txt")
                    if os.path.exists(frames_file_path):
                        with open(frames_file_path, "r") as file:
                            frame_numbers = [int(line.strip()) for line in file]

                        if 0 <= frame_index < len(frame_numbers):
                            actual_frame_number = frame_numbers
                            # Load the video player with the selected frame using the initially selected video path
                            self.load_video_for_button(
                                frame_number=actual_frame_number,
                                file_path=self.initial_video_path,
                                button_row=button_row,
                                button_col=button_col,
                                frame_index_new=frame_index,
                            )
                        else:
                            print(
                                f"Button ({button_row}, {button_col}) does not have a corresponding frame number."
                            )
                    else:
                        print(f"File not found: {frames_file_path}")
                else:
                    print(f"Invalid button event: {event}")

        self.temp_dir.cleanup()
        self.window.close()

    def load_video(self):
        file_path = sg.popup_get_file(
            "Select Video", file_types=(("Video files", "*.mp4;*.avi;*.mkv"),)
        )
        if file_path:
            self.initial_video_path = file_path
            self.cap = cv2.VideoCapture(file_path)

            # Show the 'Execute' button after a video is loaded
            self.execute_button.update(visible=True)

            self.play_video()

    def play_video_thread(self):
        print("This is self.endframe", self.endframe)
        video_lock = threading.Lock()
        f = self.startframe
        retry_after_delay = False  # Flag to retry after a delay

        while not self.stop_video_thread.is_set():
            if not self.is_paused and hasattr(self, "cap") and self.cap.isOpened():
                with video_lock:
                    try:
                        ret, frame = self.cap.read()
                        f += 1
                        # print(f)
                        if f == self.endframe:
                            break

                        if ret or f == self.endframe:
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            photo = CustomPhotoImage(Image.fromarray(frame))
                            self.window.write_event_value("_UPDATE_IMAGE_", photo)
                            retry_after_delay = (
                                False  # Reset the flag on successful read
                            )
                    except Exception as e:
                        # Handle the exception by setting the flag to retry after a delay
                        print(f"Exception in play_video_thread: {e}")
                        retry_after_delay = True

            self.stop_video_thread.wait(0.03)

            if retry_after_delay:
                # Stop execution for 2 seconds before retrying
                time.sleep(2)
                retry_after_delay = False  # Reset the flag
                continue

    def play_video(self):
        if self.video_thread is None or not self.video_thread.is_alive():
            self.stop_video_thread.clear()
            self.video_thread = threading.Thread(target=self.play_video_thread)
            self.video_thread.start()

    def stop_video(self):
        self.stop_video_thread.set()
        if self.video_thread is not None and self.video_thread.is_alive():
            self.video_thread.join()

    def play_pause_video(self):
        if hasattr(self, "cap") and self.cap.isOpened():
            if self.is_paused:
                self.is_paused = False
                self.play_pause_button.update(text="PAUSE")
                self.play_video()
            else:
                self.is_paused = True
                self.play_pause_button.update(text="PLAY")

    def compute_frames(self):
        # Check if a video is open
        if self.cap is not None:
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"Number of frames in the video: {frame_count}")

            # Set the start and end frames for processing
            start_frame = 1000
            end_frame = 4999

            # Ensure the specified frames are within the valid range
            start_frame = max(0, min(frame_count - 1, start_frame))
            end_frame = max(start_frame, min(frame_count - 1, end_frame))

            # Reset the video capture position to the specified start frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            # Initialize a list to store dictionaries containing frame number and histogram for each frame
            frame_histograms = []

            # Pre-calculate weights for the intensity calculation
            weights = np.array([0.299, 0.587, 0.114])

            # Iterate through frames from start_frame to end_frame and calculate intensity values
            for frame_number in range(start_frame, end_frame + 1):
                # Read a frame from the video
                ret, frame = self.cap.read()

                if ret:
                    # Convert the frame to RGB format
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Calculate intensity values for each pixel
                    intensity_values = np.dot(frame_rgb.reshape(-1, 3), weights)

                    # Calculate the histogram for the intensity values with 25 bins
                    histogram, _ = np.histogram(
                        intensity_values, bins=np.linspace(1, 256, 26)
                    )

                    # Store the frame number and histogram in a dictionary
                    frame_histogram = {
                        "frame_number": frame_number,
                        "histogram": histogram,
                    }

                    # Append the dictionary to the list
                    frame_histograms.append(frame_histogram)

                    # Print the progress
                    # print(f"Processed Frame: {frame_number + 1}/{end_frame + 1}")

            # After processing the specified frames, reset the video capture to the beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Calculate frame-to-frame differences (SD_i) using histogram matrices
            frame_diff_matrix = []
            for i in range(len(frame_histograms) - 1):
                sd_i = np.sum(
                    np.abs(
                        np.array(frame_histograms[i]["histogram"])
                        - np.array(frame_histograms[i + 1]["histogram"])
                    )
                )
                frame_diff_matrix.append(sd_i)

            # # Print the frame-to-frame differences (SD_i) values
            # print("Frame-to-Frame Differences (SD_i) Values:")
            # print(frame_diff_matrix)

            # Calculate the threshold (Tb)
            mean_sd = np.mean(frame_diff_matrix)
            std_sd = np.std(frame_diff_matrix)
            threshold_tb = mean_sd + std_sd * 11
            print(f"Threshold (Tb): {threshold_tb}")

            # Print frame numbers that are equal to or exceed the threshold
            print("Frame Numbers Exceeding Threshold:")
            exceeding_frames = [
                frame_histograms[i]["frame_number"]
                for i in range(len(frame_diff_matrix))
                if frame_diff_matrix[i] >= threshold_tb
            ]
            print(exceeding_frames)

            # Calculate the gradual transition threshold (Ts)
            threshold_ts = mean_sd * 2
            Tor = 2
            print(f"Gradual Threshold (Ts): {threshold_ts}")

            # Iterate through Frame_Diff_matrix and perform tasks
            cut_segments = []  # List to store (Cs, Ce) pairs
            gradual_transitions = []  # List to store (Fs_Candi, Fe_Candi) pairs
            fs_candi_plus_1_values = []  # List to store fs_candi_plus_1 values

            for i in range(len(frame_diff_matrix)):
                if frame_diff_matrix[i] >= threshold_tb:
                    # If Frame_Diff_matrix >= Tb, a cut starts at frame i
                    # and ends at frame i+1
                    cs = frame_histograms[i]["frame_number"]
                    ce = frame_histograms[i + 1]["frame_number"]
                    cut_segments.append((cs, ce))

                elif threshold_ts <= frame_diff_matrix[i] < threshold_tb:
                    # Check for potential start of gradual transition
                    fs_candi = i
                    fe_candi = None

                    # Check following Tor consecutive SD values
                    for j in range(i + 1, min(i + 1 + Tor, len(frame_diff_matrix) - 1)):
                        if (
                            frame_diff_matrix[j] < threshold_ts
                            or frame_diff_matrix[j] >= threshold_tb
                        ):
                            # End the potential gradual transition if SD falls below Ts or reaches a cut boundary
                            fe_candi = j
                            break

                    if (
                        fe_candi is not None
                        and np.sum(frame_diff_matrix[fs_candi:fe_candi]) >= threshold_tb
                    ):
                        # The potential gradual transition is confirmed
                        fs = frame_histograms[fs_candi]["frame_number"]
                        fe = frame_histograms[fe_candi]["frame_number"]
                        gradual_transitions.append((fs, fe))

                        # Calculate Fs_Candi + 1
                        fs_candi_plus_1 = fs + 1
                        fs_candi_plus_1_values.append(fs_candi_plus_1)
                        # print(f"Fs_Candi + 1: {fs_candi_plus_1}")

            # Save fs_candi_plus_1 values to a text file
            fs_candi_plus_1_file_path = "fs_candi_plus_1_values.txt"
            with open(fs_candi_plus_1_file_path, "w") as file:
                for value in fs_candi_plus_1_values:
                    file.write(f"{value}\n")

            # # Print the sets of (Cs, Ce)
            # print("Sets of (Cs, Ce):")
            # for cs, ce in cut_segments:
            #     print(f"Cs: {cs}, Ce: {ce}")

            # # Print the sets of (Fs_Candi, Fe_Candi)
            # print("Sets of (Fs_Candi, Fe_Candi):")
            # for fs_candi, fe_candi in gradual_transitions:
            #     print(f"Fs_Candi: {fs_candi}, Fe_Candi: {fe_candi}")

            # Save cut segments to a text file
            cut_segments_file_path = "cut_segments.txt"
            with open(cut_segments_file_path, "w") as file:
                for cs, ce in cut_segments:
                    file.write(f"Ce: {ce}\n")

    # Method to update buttons with frame numbers and show them
    def execute_function(self):
        frames_file_path = os.path.abspath("merged.txt")
        self.visibility = True
        if os.path.exists(frames_file_path):
            with open(frames_file_path, "r") as file:
                frame_numbers = [int(line.strip()) for line in file]

            # Update the buttons
            self.update_buttons(frame_numbers)

        else:
            sg.popup_error(f"File not found: {frames_file_path}")

    # Method to merge and save cut segments and Fs_Candi + 1 values
    def merge_and_save(self):
        # Read values from cut_segments.txt
        cut_segments_file_path = "cut_segments.txt"
        cut_segments_values = []
        with open(cut_segments_file_path, "r") as file:
            for line in file:
                # Extract Ce values
                match = re.search(r"Ce: (\d+)", line)
                if match:
                    ce = int(match.group(1))
                    cut_segments_values.append((ce, None))
        # Read values from fs_candi_plus_1_values.txt
        fs_candi_plus_1_file_path = "fs_candi_plus_1.txt"
        fs_candi_plus_1_values = []
        with open(fs_candi_plus_1_file_path, "r") as file:
            for line in file:
                # Extract Fs_Candi + 1 values
                fs_candi_plus_1 = int(line.strip())
                fs_candi_plus_1_values.append(fs_candi_plus_1)

        # Merge and sort the values by Ce and Fs_Candi + 1
        merged_values = sorted(
            cut_segments_values
            + [(fs_candi_plus_1, None) for fs_candi_plus_1 in fs_candi_plus_1_values],
            key=lambda x: (x[1] if x[1] is not None else float("inf"), x[0]),
        )

        # Save merged values to a text file
        merged_file_path = "merged.txt"
        with open(merged_file_path, "w") as file:
            for value in merged_values:
                if value[1] is not None:
                    file.write(f"Cs: {value[0]}, Ce: {value[1]}\n")
                else:
                    file.write(f"{value[0]}\n")

        print("Merged values saved to merged.txt")

    # Method to update buttons with frame numbers and display them
    def update_buttons(self, frame_numbers):
        temp_files = []
        for i, frame_number in enumerate(frame_numbers):
            frame = self.get_frame_by_number(frame_number)
            if frame is not None:
                frame = cv2.resize(frame, (90, 80))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                temp_file = os.path.join(self.temp_dir.name, f"temp_{i}.png")
                Image.fromarray(frame).save(temp_file)
                temp_files.append(temp_file)

        # Update the buttons in the layout
        for i in range(self.columns):
            for j in range(self.buttons_per_row):
                index = i * self.buttons_per_row + j
                if index < len(temp_files):
                    frame_number = frame_numbers[index]
                    temp_file = temp_files[index]

                    self.image_buttons[i][j].update(
                        image_filename=temp_file,
                        visible=self.visibility,
                        button_color=("white", sg.theme_text_color()),
                    )
                    self.frame_text[i][j].update(
                        value=f"Frame {frame_number}",
                        font=("Helvetica", 8),
                        visible=self.visibility,
                    )
                    print(f"Button ({i}, {j}) corresponds to Frame {frame_number}")
                else:
                    self.image_buttons[i][j].update(
                        image_filename="", button_color=("white", sg.theme_text_color())
                    )
                    self.frame_text[i][j].update(value="")

    def prev_page(self):
        # Move to the previous page if available
        if self.current_page > 1:
            self.current_page -= 1
            self.execute_function()

    def next_page(self):
        # Move to the next page if available
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.execute_function()

    # Method to get a frame by its frame number
    def get_frame_by_number(self, frame_number):
        if self.cap is not None and self.cap.isOpened():
            with self.cap_lock:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
                ret, frame = self.cap.read()

            if ret:
                return frame

        return None

    # Method to get the timestamp of a frame by its frame number
    def get_frame_timestamp(self, frame_number):
        if self.cap is not None and self.cap.isOpened():
            with self.cap_lock:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
                fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                timestamp_seconds = (frame_number - 1) / fps
                minutes = int(timestamp_seconds // 60)
                seconds = int(timestamp_seconds % 60)
                return f"{minutes:02}:{seconds:02}"

    # Method to get the timestamp of the current video position
    def get_current_video_timestamp(self):
        if self.cap is not None and self.cap.isOpened():
            with self.cap_lock:
                current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                fps = int(self.cap.get(cv2.CAP_PROP_FPS))
                timestamp_seconds = current_frame / fps
                minutes = int(timestamp_seconds // 60)
                seconds = int(timestamp_seconds % 60)
                return f"{minutes:02}:{seconds:02}"

    # Method to stop and close the video player
    def stop_and_close_video_player(self):
        # Stop and close the video player
        if self.cap is not None:
            self.stop_video()
            self.cap.release()
            self.cap = None


if __name__ == "__main__":
    app = VideoPlayerApp()
    app.run()
