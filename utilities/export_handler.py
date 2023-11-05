import re
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import QPointF
from objects.arrow.arrow import Arrow
from objects.staff.staff import Staff
from objects.grid import Grid
from lxml import etree
from copy import deepcopy


class ExportHandler:
    def __init__(self, staff_handler, grid, graphboard):
        self.graphboard = graphboard
        self.staff_handler = staff_handler
        self.grid = grid

    def export_to_svg(self, output_file_path):
        try:
            print("Exporting")
            svg = etree.Element("svg", nsmap={None: "http://www.w3.org/2000/svg"})
            svg.set("width", "750")
            svg.set("height", "900")
            svg.set("viewBox", "0 0 750 900")

            # Create groups for staffs, arrows, and the grid
            staffs_group = etree.Element("g", id="staffs")
            arrows_group = etree.Element("g", id="arrows")
            grid_group = etree.Element("g", id="grid")

            for item in self.graphboard.items():
                if isinstance(item, Grid):
                    grid_svg = etree.parse(item.svg_file)
                    circle_elements = grid_svg.getroot().findall(
                        ".//{http://www.w3.org/2000/svg}circle"
                    )

                    for circle_element in circle_elements:
                        cx = float(circle_element.get("cx")) + 50
                        cy = float(circle_element.get("cy")) + 50
                        circle_element.set("cx", str(cx))
                        circle_element.set("cy", str(cy))

                        # Append the circle to the grid group
                        grid_group.append(circle_element)

                    print("Finished exporting grid: " + item.svg_file)

                elif isinstance(item, Arrow):
                    arrow_svg = etree.parse(item.svg_file)
                    path_elements = arrow_svg.getroot().findall(
                        ".//{http://www.w3.org/2000/svg}path"
                    )
                    fill_color = self.get_fill_color(item.svg_file)
                    transform = item.transform()

                    for path_element in path_elements:
                        path_element.set(
                            "transform",
                            f"matrix({transform.m11()}, {transform.m12()}, {transform.m21()}, {transform.m22()}, {item.x()}, {item.y()})",
                        )
                        if fill_color is not None:
                            path_element.set("fill", fill_color)

                        # Append the path to the arrows group
                        arrows_group.append(path_element)

                    print("Finished exporting arrow: " + item.svg_file)

                elif isinstance(item, Staff):
                    staff_svg = etree.parse(item.svg_file)
                    rect_elements = staff_svg.getroot().findall(
                        ".//{http://www.w3.org/2000/svg}rect"
                    )
                    fill_color = self.get_fill_color(item.svg_file)
                    position = item.pos()
                    print(f"Staff position: {position}")

                    for rect_element in rect_elements:
                        rect_element_copy = deepcopy(
                            rect_element
                        )  # Create a deep copy of the element
                        rect_element_copy.set(
                            "x", str(position.x())
                        )  # Set the 'x' attribute
                        rect_element_copy.set(
                            "y", str(position.y())
                        )  # Set the 'y' attribute
                        rect_element_copy.set(
                            "transform", f"matrix(1.0, 0.0, 0.0, 1.0, 0, 0)"
                        )  # Remove the translation from the transformation matrix
                        if fill_color is not None:
                            rect_element_copy.set("fill", fill_color)

                        # Append the rect to the staffs group
                        staffs_group.append(rect_element_copy)
                    print("Finished exporting staff: " + item.svg_file)

            # Add comments and append the groups to the SVG root element
            svg.append(etree.Comment(" staffs "))
            svg.append(staffs_group)
            svg.append(etree.Comment(" ARROWS "))
            svg.append(arrows_group)
            svg.append(etree.Comment(" GRID "))
            svg.append(grid_group)

            # Convert the SVG element to a string
            svg_string = etree.tostring(svg, pretty_print=True).decode()

            # Add blank lines between elements
            svg_string = svg_string.replace(">\n<", ">\n\n<")
            with open(output_file_path, "w") as file:
                file.write(svg_string)
            print(f"SVG file written at {output_file_path}")
        except Exception as e:
            print(f"An error occurred while exporting the SVG: {e}")

    def export_to_png(self):
        selectedItems = self.graphboard.selectedItems()
        image = QImage(self.graphboard.size(), QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        for item in selectedItems:
            item.setSelected(False)

        self.graphboard.render(painter)
        painter.end()
        image.save("export.png")

        for item in selectedItems:
            item.setSelected(True)

    def get_staff_position(self, staff):
        staff_svg = etree.parse(staff.svg_file)
        rect_elements = staff_svg.getroot().findall(
            ".//{http://www.w3.org/2000/svg}rect"
        )
        position = None

        for rect_element in rect_elements:
            if "x" in rect_element.attrib and "y" in rect_element.attrib:
                position = QPointF(
                    float(rect_element.attrib["x"]), float(rect_element.attrib["y"])
                )
                break

        return position

    def get_fill_color(self, svg_file):
        svg = etree.parse(svg_file)
        fill_color = None

        # Try to get fill color from style element
        style_element = svg.getroot().find(".//{http://www.w3.org/2000/svg}style")
        if style_element is not None:
            style_text = style_element.text
            color_match = re.search(r"fill:\s*(#[0-9a-fA-F]+)", style_text)
            if color_match:
                fill_color = color_match.group(1)

        # If fill color was not found in style element, try to get it from path or rect elements
        if fill_color is None:
            for element in svg.getroot().iterfind(".//{http://www.w3.org/2000/svg}*"):
                if "fill" in element.attrib:
                    fill_color = element.attrib["fill"]
                    break

        return fill_color
