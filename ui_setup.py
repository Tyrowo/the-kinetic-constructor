import os
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsItem, QLabel, QFrame, QWidget, QGridLayout, QPushButton
from PyQt5.QtGui import QFont, QTransform, QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt, QPointF, QEvent, QSize
from PyQt5.QtSvg import QSvgRenderer
from objects.arrow import Arrow
from objects.staff import Staff
from objects.grid import Grid
from managers.arrow_manager import Arrow_Manager
from managers.staff_manager import Staff_Manager
from managers.svg_manager import Svg_Manager
from managers.json_manager import Json_Manager
from generator import Pictograph_Generator
from managers.sequence_manager import Sequence_Manager
from info_tracker import Info_Tracker
from views.graphboard_view import Graphboard_View
from views.arrowbox_view import ArrowBox_View
from views.propbox_view import PropBox_View
from exporter import Exporter
from pictograph_selector import Pictograph_Selector
from settings import *

class UiSetup(QWidget):

    def __init__(self, main_window):
        super().__init__(main_window)
        self.setFocusPolicy(Qt.StrongFocus)
        self.main_window = main_window
        self.main_window.installEventFilter(self)
        self.main_window.setMinimumSize(int(2000), int(1600))
        self.main_window.show()
        self.main_window.setWindowTitle("Sequence Generator")
        self.svg_manager = Svg_Manager()
        self.arrows = []
        self.graphboard_scene = QGraphicsScene()
        self.graphboard_scene.setSceneRect(0, 0, GRID_WIDTH, GRID_WIDTH)
        self.ARROW_DIR = 'images\\arrows'
        self.exporter = None
        self.sequence_manager = None
        self.graphboard_view = None


        self.init_staff_manager()
        self.initLayouts()
        self.arrow_manager = Arrow_Manager(None, self.graphboard_view, self.staff_manager)
        self.json_manager = Json_Manager(self.graphboard_scene)
        self.initInfoTracker()
        
        self.grid = Grid('images\\grid\\grid.svg')
        self.grid.setScale(GRAPHBOARD_SCALE)
        self.exporter = Exporter(self.graphboard_view, self.graphboard_scene, self.staff_manager, self.grid)
        
        self.initGraphboardView() 
        self.init_generator() 
        self.connectGraphboard()
        self.initArrowBox()
        self.initPropBoxView()
        
        self.staff_manager.connect_grid(self.grid)
        self.staff_manager.connect_graphboard_view(self.graphboard_view)
        self.staff_manager.connect_propbox_view(self.propbox_view)
        self.staff_manager.init_graphboard_staffs(self.graphboard_view)
        self.staff_manager.init_propbox_staffs(self.propbox_scene)
        
        self.initButtons()
        self.connectInfoTracker()
        self.initWordLabel()
        self.initSequenceScene()
        self.initLetterButtons()
        self.setFocus()

        self.arrow_manager.connect_info_tracker(self.info_tracker)
        self.graphboard_view.connect_generator(self.generator)

    def initLayouts(self):
        self.main_layout = QHBoxLayout()
        self.right_layout = QVBoxLayout()  # Change this to QHBoxLayout
        self.upper_layout = QHBoxLayout()  # This will contain graphboard and buttons
        self.lower_layout = QVBoxLayout()  # Sequence
        self.top_of_lower_layout = QHBoxLayout()
        self.objectbox_layout = QVBoxLayout()
        self.graphboard_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()  # Change this to QHBoxLayout
        self.info_layout = QVBoxLayout()
        self.word_label_layout = QHBoxLayout()
        self.upper_graphboard_with_panel_layout = QVBoxLayout()
        
        self.upper_graphboard_with_panel_layout.addLayout(self.graphboard_layout)
        self.upper_graphboard_with_panel_layout.addLayout(self.button_layout)  # Add button_layout after graphboard_layout
        self.upper_layout.addLayout(self.objectbox_layout)
        self.upper_layout.addLayout(self.upper_graphboard_with_panel_layout)
        self.top_of_lower_layout.addLayout(self.word_label_layout)
        self.lower_layout.addLayout(self.top_of_lower_layout)
        self.right_layout.addLayout(self.upper_layout)
        self.upper_layout.addLayout(self.info_layout)
        self.right_layout.addLayout(self.lower_layout)  # Add info_layout to right_layout
        self.main_layout.addLayout(self.right_layout)

        self.upper_layout.addStretch()
        self.objectbox_layout.addStretch()
        self.objectbox_layout.addStretch()

        self.main_window.setLayout(self.main_layout)

    def initGraphboardView(self):
        self.graphboard_view = Graphboard_View(self.graphboard_scene, self.grid, self.info_tracker, self.staff_manager, self.svg_manager, self.arrow_manager, self, None, self.sequence_manager, self.exporter, self.json_manager)
        self.arrow_manager.connect_to_graphboard(self.graphboard_view)

         
    def initLetterButtons(self):
        letter_buttons_layout = QVBoxLayout()
        letter_buttons_layout.setSpacing(10)  # Set the spacing between rows of buttons
        letter_buttons_layout.setAlignment(Qt.AlignTop)  # Align the layout to the top
        letter_rows = [
            ['A', 'B', 'C'],
            ['D', 'E', 'F'],
            ['G', 'H', 'I'],
            ['J', 'K', 'L'],
            ['M', 'N', 'O'],
            ['P', 'Q', 'R'],
            ['S', 'T', 'U', 'V'],
            ['W', 'X', 'Y', 'Z'],
            ['Σ', 'Δ', 'θ', 'Ω'],
            # ['Φ', 'Ψ', 'Λ'],
            # ['W-', 'X-', 'Y-', 'Z-'],
            # ['Σ-', 'Δ-', 'θ-', 'Ω-'],
            # ['Φ-', 'Ψ-', 'Λ-'],
            ['α', 'β', 'Γ']
        ]

        for row in letter_rows:
            row_layout = QHBoxLayout()
            for letter in row:
                icon_path = f"images/letters/{letter}.svg"
                renderer = QSvgRenderer(icon_path)
                pixmap = QPixmap(renderer.defaultSize())
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                button = QPushButton(QIcon(pixmap), "", self.main_window)
                font = QFont()
                font.setPointSize(20)
                button.setFont(font)
                button.setFixedSize(65, 65)
                button.clicked.connect(lambda _, l=letter: self.show_pictograph_selector(l))
                row_layout.addWidget(button)
            letter_buttons_layout.addLayout(row_layout)

        generate_all_button = QPushButton("Generate All", self.main_window)
        font = QFont()
        font.setPointSize(20)
        generate_all_button.setFont(font)
        generate_all_button.setFixedSize(300, 80)
        generate_all_button.clicked.connect(lambda: self.generator.generate_all_pictographs(self.staff_manager))
        letter_buttons_layout.addWidget(generate_all_button)
        self.upper_layout.addLayout(letter_buttons_layout)

    def initButtons(self):
        button_font = QFont('Helvetica', 14)
        button_width = 60
        button_height = 60
        icon_size = QSize(40, 40)
        masterbtnlayout = QVBoxLayout()
        buttonlayout = QHBoxLayout()
        buttonstack = QHBoxLayout()
        buttonstack.setAlignment(Qt.AlignTop)
        masterbtnlayout.setAlignment(Qt.AlignTop)
        buttonlayout.addLayout(buttonstack)
        masterbtnlayout.addLayout(buttonlayout)

        def createButton(icon_path, tooltip, on_click, is_lambda=False):
            button = QPushButton(QIcon(icon_path), "")
            button.setToolTip(tooltip)
            button.setFont(button_font)
            button.setFixedWidth(button_width)
            button.setFixedHeight(button_height)
            button.setIconSize(icon_size)
            if is_lambda:
                button.clicked.connect(lambda: on_click())
            else:
                button.clicked.connect(on_click)
            return button

        self.updatePositionButton = createButton("images/icons/update_locations.png", "Update Position", 
            lambda: self.json_manager.update_optimal_locations_in_json(*self.graphboard_view.get_current_arrow_positions()), is_lambda=True)
        self.deleteButton = createButton("images/icons/delete.png", "Delete",
            lambda: self.arrow_manager.delete_arrow(self.graphboard_scene.selectedItems()), is_lambda=True)
        self.rotateRightButton = createButton("images/icons/rotate_right.png", "Rotate Right",
            lambda: self.arrow_manager.rotate_arrow('right', self.graphboard_scene.selectedItems()), is_lambda=True)        
        self.rotateLeftButton = createButton("images/icons/rotate_left.png", "Rotate Left",
            lambda: self.arrow_manager.rotate_arrow('left', self.graphboard_scene.selectedItems()), is_lambda=True)
        self.mirrorButton = createButton("images/icons/mirror.png", "Mirror",
            lambda: self.arrow_manager.mirror_arrow(self.graphboard_scene.selectedItems()), is_lambda=True)
        self.swapColors = createButton("images/icons/swap.png", "Swap Colors",
            lambda: self.arrow_manager.swap_colors(self.graphboard_scene.selectedItems()), is_lambda=True)
        self.selectAllButton = createButton("images/icons/select_all.png", "Select All",
            lambda: self.graphboard_view.select_all_items(), is_lambda=True)
        self.add_to_sequence_button = createButton("images/icons/add_to_sequence.png", "Add to Sequence",
            lambda: self.sequence_manager.add_to_sequence(self.graphboard_view), is_lambda=True)
        
        buttons = [
            self.deleteButton, 
            self.rotateRightButton,
            self.rotateLeftButton,
            self.mirrorButton,
            self.swapColors,
            self.updatePositionButton,
            self.selectAllButton,
            self.add_to_sequence_button
        ]

        for button in buttons:
            buttonstack.addWidget(button)

        self.button_layout.addLayout(masterbtnlayout)

    def initArrowBox(self):
        arrowbox_frame = QFrame(self.main_window)
        objectbox_layout = QGridLayout()
        arrowbox_frame.setLayout(objectbox_layout) 
        arrowbox_scene = QGraphicsScene()

        svgs_full_paths = []
        default_arrows = ['red_pro_r_ne_0.svg', 'red_anti_r_ne_0.svg', 'blue_pro_r_sw_0.svg', 'blue_anti_r_sw_0.svg']
        svg_item_count = 0

        for dirpath, dirnames, filenames in os.walk(self.ARROW_DIR):
            svgs_full_paths.extend([os.path.join(dirpath, filename) for filename in filenames if filename.endswith('.svg')])

        svg_item_count_red_pro = 0
        svg_item_count_red_anti = 0
        svg_item_count_blue_pro = 0
        svg_item_count_blue_anti = 0
        spacing = 200
        y_pos_red = 0
        y_pos_blue = 200

        for i, svg_file in enumerate(svgs_full_paths):
            file_name = os.path.basename(svg_file)
            if file_name in default_arrows:
                motion_type = file_name.split('_')[1]
                arrow_item = Arrow(svg_file, self.graphboard_view, self.info_tracker, self.svg_manager, self.arrow_manager, motion_type, self.staff_manager, None)
                arrow_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                arrow_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                arrow_item.setScale(0.75)

                if 'red' in file_name:
                    if 'pro' in file_name:
                        arrow_item.setPos(svg_item_count_red_pro * spacing, y_pos_red) # Red pro
                        svg_item_count_red_pro += 1
                    elif 'anti' in file_name:
                        arrow_item.setPos((svg_item_count_red_anti + 1) * spacing, y_pos_red) # Red Anti
                        svg_item_count_red_anti += 1
                elif 'blue' in file_name:
                    if 'pro' in file_name:
                        arrow_item.setPos(svg_item_count_blue_pro * spacing, y_pos_blue) # Blue pro
                        svg_item_count_blue_pro += 1
                    elif 'anti' in file_name:
                        arrow_item.setPos((svg_item_count_blue_anti + 1) * spacing, y_pos_blue) # Blue Anti
                        svg_item_count_blue_anti += 1
                arrowbox_scene.addItem(arrow_item) 


                self.arrows.append(arrow_item)
        arrowbox = ArrowBox_View(arrowbox_scene, self.graphboard_view, self.info_tracker, self.svg_manager)
        objectbox_layout.addWidget(arrowbox) 
        arrowbox_frame.setFixedSize(int(500), int(500))
        self.objectbox_layout.addWidget(arrowbox_frame)

    def initPropBoxView(self):
        self.propbox_view = PropBox_View(self.main_window, self.staff_manager, self)
        propbox_layout = QVBoxLayout()
        propbox_frame = QFrame() 
        propbox_layout.addWidget(self.propbox_view.propbox_frame)
        propbox_frame.setLayout(propbox_layout)
        self.objectbox_layout.addWidget(propbox_frame)
        self.propbox_scene = QGraphicsScene()
        self.propbox_view.setScene(self.propbox_scene)

    def initInfoTracker(self):
        self.info_label = QLabel(self.main_window)
        self.info_tracker = Info_Tracker(None, self.info_label, self.staff_manager, self.json_manager)

    def initWordLabel(self):
        self.word_label = QLabel(self.main_window)
        self.lower_layout.addWidget(self.word_label)
        self.word_label.setFont(QFont('Helvetica', 20))
        self.word_label.setText("My word: ")



    def initSequenceScene(self):

        self.sequence_scene = QGraphicsScene()
        self.sequence_scene.setSceneRect(0, 0, 4 * 375, 375)
        self.sequence_manager = Sequence_Manager(self.sequence_scene, self.generator, self, self.info_tracker)
        self.sequence_scene.manager = self.sequence_manager
        self.sequence_container = QGraphicsView(self.sequence_scene)
        self.sequence_container.setFixedSize(1960, 500)
        self.sequence_container.show()
        self.lower_layout.addWidget(self.sequence_container)
        clear_sequence_button = self.sequence_manager.get_clear_sequence_button()
        self.lower_layout.addWidget(clear_sequence_button)

    def init_generator(self):
        self.generator = Pictograph_Generator(self.staff_manager, self.graphboard_view, self.graphboard_scene, self.info_tracker, self.main_window, self, self.exporter, self.json_manager, self.grid)

    def init_staff_manager(self):
        self.staff_manager = Staff_Manager(self.graphboard_scene)


### CONNECTORS ###

    def connectInfoTracker(self):
        self.info_layout.addWidget(self.info_label)

    def connectGraphboard(self):
        self.info_tracker.connect_graphboard_view(self.graphboard_view)
        self.graphboard_layout.addWidget(self.graphboard_view)


### GETTERS ###

    def get_sequence_manager(self):
        if not hasattr(self, 'sequence_manager'):
            self.sequence_scene.set_manager(self.sequence_manager)
        return self.sequence_manager


### EVENTS ###

    def show_pictograph_selector(self, letter):
        # Fetch all possible combinations for the clicked letter
        # Assuming self.generator.letters is the dictionary containing all combinations
        combinations = self.generator.letters.get(letter, [])
        
        if not combinations:
            print(f"No combinations found for letter {letter}")
            return
        
        # Create and show the Pictograph_Selector dialog
        dialog = Pictograph_Selector(combinations, letter, self.graphboard_view, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # TODO: Handle the selected pictograph
            pass

    def keyPressEvent(self, event):
        self.selected_items = self.graphboard_view.get_selected_items()
        
        try:
            self.selected_item = self.selected_items[0]
        except IndexError:
            self.selected_item = None

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Delete:
            for item in self.selected_items:
                if isinstance(item, Arrow):
                    self.arrow_manager.delete_arrow(item)
                elif isinstance(item, Staff):
                    self.arrow_manager.delete_staff(item)

        elif event.key() == Qt.Key_Delete:
            for item in self.selected_items:
                if isinstance(item, Arrow):
                    self.arrow_manager.delete_arrow(item)
                    self.arrow_manager.delete_staff(item.staff)
                elif isinstance(item, Staff):
                    self.arrow_manager.delete_staff(item)

        elif self.selected_item and isinstance(self.selected_item, Arrow):
            if event.key() == Qt.Key_W:
                self.arrow_manager.move_arrow_quadrant_wasd('up', self.selected_item)
            elif event.key() == Qt.Key_A:
                self.arrow_manager.move_arrow_quadrant_wasd('left', self.selected_item)
            elif event.key() == Qt.Key_S:
                self.arrow_manager.move_arrow_quadrant_wasd('down', self.selected_item)
            elif event.key() == Qt.Key_D:
                self.arrow_manager.move_arrow_quadrant_wasd('right', self.selected_item)
            elif event.key() == Qt.Key_E:
                self.arrow_manager.mirror_arrow(self.selected_items)
            elif event.key() == Qt.Key_Q:
                self.arrow_manager.swap_motion_type(self.selected_items)
            elif event.key() == Qt.Key_F:
                self.sequence_manager.add_to_sequence(self.graphboard_view)
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)
            return True
        return super().eventFilter(source, event)
    
