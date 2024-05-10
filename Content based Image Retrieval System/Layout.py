import PySimpleGUI as psg

pagination_font = "Arial 16 bold"
DEFAULT_SIMILARITY_METHOD = "Intensity"
RELEVANCE_COMPATIBLE_METHOD = "Color + Intensity"


class Layout:
    def __init__(self, images) -> None:
        self.curr_page = 1  # State variable for current page number
        self.selected_image = None  # State variable for currently selected image
        self.similarity_method = DEFAULT_SIMILARITY_METHOD  # State variable for currently selected similarity method
        self.images = images  # State variables for current image order list
        self.MAX = len(images)
        self.relevant_images = []
        self.relevance_enabled = False

    def generate_image_gallery(self, size=(152, 152), page_length=18, cols=6):
        """Generates and combines the individual components of the image gallery section

        Args:
            size (tuple, optional): The display size of the images inside the gallery. Defaults to (152, 152).
            page_length (int, optional): Number of images persent on each page. Defaults to 18.
            cols (int, optional): Number of columns that the image gallery should contain. Defaults to 6.

        Returns:
            _type_: None
        """
        start = (self.curr_page - 1) * page_length
        if start >= self.MAX:
            self.curr_page -= 1
        elif self.curr_page <= 0:
            self.curr_page += 1

        cur = start

        # Pagination controls layout
        pagination_element = [
            psg.Button(
                "<",
                font=pagination_font,
                key="-PREVIOUS_PAGE-",
                disabled=True if start == 0 else False,
            ),
            psg.Text(f"{self.curr_page}", font=pagination_font, key="-PAGE_POSITION-"),
            psg.Button(
                ">",
                font=pagination_font,
                key="-NEXT_PAGE-",
                disabled=True if start + page_length >= 100 else False,
            ),
        ]

        # Image gallery layout formation
        cur_max = self.MAX if not self.selected_image else self.MAX - 1
        image_gallery_layout = []
        while cur < min(start + page_length, cur_max):
            temp = []
            subsample = 2 if size[0] == 152 else 3
            for _ in range(cols):
                temp.append(
                    psg.Column(
                        [
                            [
                                psg.Image(
                                    "{path}".format(path=self.images[cur]["path"]),
                                    pad=(16, 4 / 2),
                                    size=size,
                                    subsample = subsample,
                                    key="-IMAGE_{id}-".format(
                                        id=self.images[cur]["name"]
                                    ),
                                    enable_events=True,
                                )
                            ],
                            [
                                psg.Text(
                                    "{name}".format(name=self.images[cur]["name"]),
                                    expand_x=True,
                                    justification="center",
                                ),
                                psg.Checkbox(
                                    text="",
                                    text_color='blue',
                                    default=(
                                        self.images[cur]["name"] in self.relevant_images
                                    ),
                                    visible=self.relevance_enabled,
                                    key="-FEEDBACK_{id}-".format(
                                        id=self.images[cur]["name"]
                                    ),
                                    enable_events=True,
                                ),
                            ],
                        ]
                    )
                )
                cur += 1
                if (self.selected_image and cur == self.MAX - 1) or cur == self.MAX:
                    break
            image_gallery_layout.append(temp)
        image_gallery_layout.append(
            [
                psg.Column(
                    [pagination_element],
                    expand_x=True,
                    element_justification="center",
                )
            ]
        )

        # Integrating all image gallery components
        image_gallery_layout = [
            psg.Column(
                image_gallery_layout,
                expand_x=True,
                expand_y=True,
                pad=(16),
                element_justification="center",
                vertical_alignment="center",
            )
        ]
        return image_gallery_layout

    def createWindow(self, result=False):
        """Determines the layout to be presented and integrates all components of the layout renders it in a window

        Returns:
            _type_: None
        """
        layout = None
        default_text_element = [
            psg.Text(
                "Please select an image",
                font="Arial 20",
                expand_x=True,
                justification="center",
                pad=(16, 8),
            ),
        ]

        # Layout formation when an image is selected
        if self.selected_image:
            image_operations_layout = [
                [
                    psg.Frame(
                        title="",
                        layout=[
                            [
                                psg.Image(
                                    ".\\images\\png\\{id}.png".format(
                                        id=self.selected_image
                                    ),
                                )
                            ]
                        ],
                        pad=(0, 36 / 4),
                    )
                ],
                [
                    psg.Text(
                        "{id}".format(id=self.selected_image),
                        expand_x=True,
                        justification="center",
                    )
                ],
                [
                    psg.Combo(
                        ["Intensity", "Color", "Color + Intensity"],
                        default_value=self.similarity_method,
                        pad=(8, 36),
                        expand_x=True,
                        enable_events=True,
                        readonly=True,
                        key="-METHOD-",
                    )
                ],
                [
                    psg.Column(
                        [
                            [
                                psg.Checkbox(
                                    "Relevance",
                                    default=self.relevance_enabled,
                                    disabled=(
                                        self.similarity_method
                                        != RELEVANCE_COMPATIBLE_METHOD
                                    ),
                                    key="-RF-",
                                    enable_events=True,
                                )
                            ],
                            [
                                psg.Button(
                                    "Retrieve Images",
                                    key="-RETRIEVE-",
                                    expand_x=True,
                                )
                            ],
                            [
                                psg.Button(
                                    "Reset",
                                    key="-RESET-",
                                    expand_x=True,
                                )
                            ],
                        ],
                        key="-OPERATIONS_CONTROL-",
                        pad=((0, 0), (48, 0)),
                        expand_x=True,
                        element_justification="center",
                    )
                ],
            ]

            frame_label = "Other" if not result else "Similar"
            layout = [
                [
                    [
                        psg.Column(
                            [
                                [
                                    psg.Column(
                                        image_operations_layout,
                                        element_justification="center",
                                        pad=(16, 16),
                                    ),
                                    psg.Frame(
                                        f"{frame_label} Images",
                                        [
                                            self.generate_image_gallery(
                                                (108, 108), 20, 5
                                            )
                                        ],
                                        expand_y=True,
                                        expand_x=True,
                                    ),
                                ]
                            ],
                            key="-PARENT-",
                        )
                    ]
                ]
            ]

        else:
            # Layout formation when no image is selected
            layout = [
                [
                    psg.Column(
                        [default_text_element, self.generate_image_gallery()],
                        key="-PARENT-",
                    )
                ]
            ]

        # Render the layout in a window
        return psg.Window(
            "Image Retrieval System", layout, size=(1280, 786), margins=(16, 16)
        )

    def set_relevant_images(self, dictionary):
        for key in dictionary:
            key_parameter = key.split("_")
            if "-FEEDBACK" in key_parameter:
                if dictionary[key]:
                    self.relevant_images.append(key_parameter[1][:-1])

    def to_toggle_Relevance(self, value):
        if (
            value == RELEVANCE_COMPATIBLE_METHOD
            or self.similarity_method == RELEVANCE_COMPATIBLE_METHOD
        ):
            return True
