import pygame
import pygame_gui
import sys

from Graph.graph import Graph
from Database.engine import Engine
engine = Engine()

# Constants for screen dimensions and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLANK_SURFACE = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))

class App:
    def __init__(self, theme_path="./GUI/theme.json"):
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Database Query Analyzer')

        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(pygame.Color(*WHITE))

        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path)

        self.input_box = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((15, 15), (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 15)),
            placeholder_text="Input SQL Query"
        )

        self.submit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((15, SCREEN_HEIGHT // 2), (150, 50)),
            text='Submit Query',
            manager=self.manager
        )

        self.clear_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((180, SCREEN_HEIGHT // 2), (150, 50)),
            text='Reset',
            manager=self.manager
        )

        self.explanation_box = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2, 15), (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 15)),
            html_text="",
            manager=self.manager
        )

        empty = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), flags=pygame.SRCALPHA)
        empty.fill(pygame.Color(0,0,0,0))
        self.plot_box = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 15)),
            image_surface=empty,
            manager=self.manager
        )

    def run(self):
        is_running = True
        clock = pygame.time.Clock()

        while is_running:
            time_delta = clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.submit_button:
                        raw_query = self.input_box.get_text()

                        query_json = engine.get_query_plan(raw_query)
                        graph = Graph(query_json)

                        explanation = graph.create_explanation(graph.root)
                        formatted_explanation = ""
                        for i, e in enumerate(explanation):
                            formatted_explanation += f"{i+1}) {e}\n"
                        
                        self.explanation_box.set_text(formatted_explanation)

                        filename = graph.save_graph_file()
                        plot = pygame.image.load(filename)
                        self.plot_box.set_image(plot)
                        
                    if event.ui_element == self.clear_button:
                        self.input_box.set_text("")
                        self.explanation_box.set_text("")

                        empty = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), flags=pygame.SRCALPHA)
                        empty.fill(pygame.Color(0,0,0,0))
                        self.plot_box.set_image(empty)
                        
                self.manager.process_events(event)

            self.manager.update(time_delta)

            self.screen.blit(self.background, (0,0))
            self.manager.draw_ui(self.screen)

            pygame.display.update()



if __name__ == "__main__":
    gui = App()
    gui.run()