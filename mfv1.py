from manimlib import *
import numpy as np

class MedianFilter(Scene):
    def construct(self):
        # Image dimensions
        ny, nx = 8, 10
        hy, hx = 2, 2  # Half window size
        
        # Create a sample input image with more grayscale variation
        np.random.seed(42)
        input_image = np.random.uniform(0, 1, (ny, nx))
        
        output_image = np.zeros((ny, nx))
        
        # Create the grid for input image (left side)
        input_grid = self.create_image_grid(input_image, position=LEFT * 8)
        output_grid = self.create_image_grid(output_image, position=RIGHT * 8)
        
        self.add(input_grid, output_grid)
        self.wait(0.5)
        
        # Process each pixel
        for y in range(ny):
            for x in range(nx):
                # Show full window (including out of bounds)
                window_all_positions = []
                window_values = []
                window_valid = []
                
                for i in range(y - hy, y + hy + 1):
                    for j in range(x - hx, x + hx + 1):
                        window_all_positions.append((i, j))
                        if 0 <= i < ny and 0 <= j < nx:
                            window_values.append(input_image[i, j])
                            window_valid.append(True)
                        else:
                            window_valid.append(False)
                
                # Show full window overlay
                window_overlay = self.create_window_overlay(
                    window_all_positions, window_valid, y, x, input_image, input_grid
                )
                self.play(FadeIn(window_overlay), run_time=0.3)
                
                # Create label for unsorted buffer
                # unsorted_label = Text("Unsorted", font_size=24)
                # unsorted_label.move_to(UP * 3.5)
                # self.play(FadeIn(unsorted_label), run_time=0.2)
                
                # Copy cells from window to unsorted buffer with animation
                moving_cells = VGroup()
                unsorted_buffer_cells = VGroup()
                cell_size = 0.6
                buffer_y = 10
                
                idx = 0
                for (i, j), is_valid in zip(window_all_positions, window_valid):
                    if is_valid:
                        # Create a copy of the cell that will move
                        cell_index = i * nx + j
                        moving_cell = input_grid[cell_index].copy()
                        moving_cell.set_stroke(WHITE, width=2)
                        moving_cells.add(moving_cell)
                        
                        # Create target position in unsorted buffer
                        target_x = (idx - len(window_values) / 2) * (cell_size + 0.05)
                        target_pos = UP * buffer_y + RIGHT * target_x
                        
                        # Scale it down to buffer size
                        moving_cell.generate_target()
                        moving_cell.target.scale(cell_size / 1.0)
                        moving_cell.target.move_to(target_pos)
                        
                        unsorted_buffer_cells.add(moving_cell.target.copy())
                        idx += 1
                
                self.play(
                    *[MoveToTarget(cell) for cell in moving_cells],
                    run_time=0.6
                )
                
                # Create sorted buffer label
                sorted_label = Text("Sort buffer", font_size=30)
                sorted_label.move_to(UP * 9.0 + RIGHT * 1.0)
                
                # Create arrow between buffers
                arrow = Arrow(
                    UP * (buffer_y - 0.5),
                    UP * 8.5,
                    buff=0.1,
                    stroke_width=4,
                    color=BLUE
                )
                
                self.play(
                    FadeIn(sorted_label),
                    ShowCreation(arrow),
                    run_time=0.3
                )
                
                # Sort animation - move cells to sorted positions
                sorted_values = sorted(window_values)
                sorted_buffer_y = 8
                
                # Create mapping: for each unsorted cell, find its sorted position
                # We'll use indices with values to handle duplicates
                unsorted_with_idx = [(val, idx) for idx, val in enumerate(window_values)]
                sorted_with_idx = sorted(unsorted_with_idx, key=lambda x: x[0])
                
                # Create mapping from original index to sorted index
                idx_to_sorted_pos = {}
                for sorted_pos, (val, orig_idx) in enumerate(sorted_with_idx):
                    idx_to_sorted_pos[orig_idx] = sorted_pos
                
                # Animate cells moving to sorted positions
                for idx, cell in enumerate(moving_cells):
                    sorted_pos = idx_to_sorted_pos[idx]
                    target_x = (sorted_pos - len(window_values) / 2) * (cell_size + 0.05)
                    target_pos = UP * sorted_buffer_y + RIGHT * target_x
                    
                    cell.generate_target()
                    cell.target.move_to(target_pos)
                
                self.play(
                    *[MoveToTarget(cell) for cell in moving_cells],
                    run_time=0.7
                )
                
                # Create sorted cells array for easier median access
                sorted_cells = [None] * len(moving_cells)
                for idx, cell in enumerate(moving_cells):
                    sorted_pos = idx_to_sorted_pos[idx]
                    sorted_cells[sorted_pos] = cell
                
                # Get median and highlight
                mid = len(window_values) // 2
                median_value = 0
                median_highlight = VGroup()
                median_cells_to_move = VGroup()
                
                if len(window_values) % 2 == 1:
                    # Odd number - single median
                    median_value = sorted_values[mid]
                    median_box = sorted_cells[mid].copy()
                    median_box.set_stroke(GREEN, width=6)
                    median_highlight.add(median_box)
                    median_cells_to_move.add(sorted_cells[mid])
                else:
                    # Even number - mean of two middle values
                    median_value = 0.5 * (sorted_values[mid] + sorted_values[mid - 1])
                    median_box1 = sorted_cells[mid - 1].copy()
                    median_box1.set_stroke(GREEN, width=6)
                    median_box2 = sorted_cells[mid].copy()
                    median_box2.set_stroke(GREEN, width=6)
                    median_highlight.add(median_box1, median_box2)
                    
                    # Show mean calculation with line
                    mean_line = Line(
                        sorted_cells[mid - 1].get_center(),
                        sorted_cells[mid].get_center(),
                        color=GREEN,
                        stroke_width=4
                    ).shift(DOWN * 0.5)
                    median_highlight.add(mean_line)
                    median_cells_to_move.add(sorted_cells[mid - 1], sorted_cells[mid])
                
                self.play(FadeIn(median_highlight), run_time=0.3)
                self.wait(0.2)
                
                output_image[y, x] = median_value
                
                # Animate median cell(s) moving to output
                output_cell_index = y * nx + x
                output_pos = output_grid[output_cell_index].get_center()
                
                # Create final output cell
                final_cell = self.create_cell(median_value, output_pos)
                
                if len(median_cells_to_move) == 1:
                    # Single median cell - move it and transform to output
                    med_cell = median_cells_to_move[0]
                    med_cell.generate_target()
                    med_cell.target.scale(1.0 / cell_size)
                    med_cell.target.move_to(output_pos)
                    med_cell.target.set_fill(
                        rgb_to_color([median_value, median_value, median_value]),
                        opacity=1
                    )
                    med_cell.target.set_stroke(WHITE, width=2)
                    
                    self.play(
                        MoveToTarget(med_cell),
                        Transform(output_grid[output_cell_index], final_cell),
                        run_time=0.6
                    )
                else:
                    # Two median cells - move both and merge
                    for med_cell in median_cells_to_move:
                        med_cell.generate_target()
                        med_cell.target.scale(1.0 / cell_size)
                        med_cell.target.move_to(output_pos)
                        med_cell.target.set_fill(
                            rgb_to_color([median_value, median_value, median_value]),
                            opacity=1
                        )
                        med_cell.target.set_stroke(WHITE, width=2)
                    
                    self.play(
                        *[MoveToTarget(cell) for cell in median_cells_to_move],
                        run_time=0.6
                    )
                    
                    # Merge into final cell
                    self.play(
                        Transform(output_grid[output_cell_index], final_cell),
                        *[FadeOut(cell) for cell in median_cells_to_move],
                        run_time=0.3
                    )
                
                # Clean up
                cleanup_anims = [
                    FadeOut(window_overlay),
                    FadeOut(median_highlight),
                    FadeOut(arrow),
                    # FadeOut(unsorted_label),
                    FadeOut(sorted_label),
                ]
                
                # Fade out all buffer cells except the median ones (they're already handled)
                for cell in moving_cells:
                    if cell not in median_cells_to_move:
                        cleanup_anims.append(FadeOut(cell))
                
                # For single median case, need to fade that out too
                if len(median_cells_to_move) == 1:
                    cleanup_anims.append(FadeOut(median_cells_to_move[0]))
                
                self.play(*cleanup_anims, run_time=0.2)
        
        self.wait(2)
    
    def create_image_grid(self, image, position):
        ny, nx = image.shape
        grid = VGroup()
        cell_size = 1.0  # Larger cell size
        
        for i in range(ny):
            for j in range(nx):
                cell = self.create_cell(image[i, j], ORIGIN)
                cell.move_to(position + RIGHT * j * cell_size + DOWN * i * cell_size)
                grid.add(cell)
        
        # Center the grid
        grid.move_to(position)
        return grid
    
    def create_cell(self, value, position):
        cell_size = 1.0  # Larger cell size
        # Create square
        square = Square(side_length=cell_size)
        
        # Color based on value (grayscale)
        gray_value = value
        color = rgb_to_color([gray_value, gray_value, gray_value])
        square.set_fill(color, opacity=1)
        square.set_stroke(WHITE, width=2)
        
        square.move_to(position)
        return square
    
    def create_window_overlay(self, positions, valid, center_y, center_x, input_image, input_grid):
        overlay = VGroup()
        cell_size = 1.0
        ny, nx = input_image.shape
        
        for idx, ((i, j), is_valid) in enumerate(zip(positions, valid)):
            if is_valid:
                # Highlight existing cell
                cell_index = i * nx + j
                highlight = input_grid[cell_index].copy()
                
                # Yellow for center pixel, blue for window
                if i == center_y and j == center_x:
                    highlight.set_stroke(YELLOW, width=6)
                else:
                    highlight.set_stroke(BLUE, width=5)
                overlay.add(highlight)
            else:
                # Show grayed out cell for out of bounds
                relative_i = i - center_y
                relative_j = j - center_x
                center_pos = input_grid[center_y * nx + center_x].get_center()
                out_cell = Square(side_length=cell_size)
                out_cell.set_fill(BLACK, opacity=0.3)
                out_cell.set_stroke(RED, width=3, opacity=0.5)
                out_cell.move_to(center_pos + RIGHT * relative_j * cell_size + DOWN * relative_i * cell_size)
                overlay.add(out_cell)

        overlay.add(input_grid[center_y * nx + center_x].copy().set_stroke(YELLOW, width=6))
        
        return overlay
    
    def create_buffer_display(self, values, position, label):
        buffer_group = VGroup()
        cell_size = 0.6
        
        cells = VGroup()
        for idx, val in enumerate(values):
            cell = Square(side_length=cell_size)
            gray_value = val
            color = rgb_to_color([gray_value, gray_value, gray_value])
            cell.set_fill(color, opacity=1)
            cell.set_stroke(WHITE, width=2)
            cell.move_to(position + RIGHT * (idx - len(values) / 2) * (cell_size + 0.05))
            cells.add(cell)
        
        # Add label text
        label_text = Text(label, font_size=24)
        label_text.next_to(cells, UP, buff=0.2)
        
        buffer_group.add(cells, label_text)
        return buffer_group