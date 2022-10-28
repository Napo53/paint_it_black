import pygame


class PaintItBlack:
    def __init__(self):
        pygame.init()

        self.highscore = 0
        self.load_images()
        self.new_game()

        self.height = len(self.map)
        self.width = len(self.map[0])
        self.scale = self.images[0].get_width()

        window_height = self.scale * self.height
        window_width = self.scale * self.width
        self.window = pygame.display.set_mode(
            (window_width, window_height + self.scale))

        self.game_font = pygame.font.SysFont("Arial", 24)

        pygame.display.set_caption("Paint it Black")

        self.main_loop()

    def load_images(self):
        self.images = []
        for name in ["floor", "wall", "target", "box", "robotsmall", "done", "target_robot"]:
            self.images.append(pygame.image.load(name + ".png"))

    def new_game(self):
        self.map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 5, 1, 2, 0, 0, 2, 0, 1, 2, 2, 0, 2, 0, 0, 2, 0, 0, 0, 1],
                    [1, 2, 0, 0, 0, 0, 2, 0, 1, 2, 2, 0, 0, 1, 2, 0, 1, 0, 0, 1],
                    [1, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 2, 0, 0, 1],
                    [1, 4, 0, 2, 1, 0, 2, 2, 1, 0, 0, 0, 2, 0, 1, 2, 1, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        self.start_black_squares = self.count_black_squares()

    def main_loop(self):
        while True:
            self.check_events()
            self.draw_window()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    self.new_game()
                if event.key == pygame.K_ESCAPE:
                    exit()
                if event.key == pygame.K_LEFT:
                    self.move(0, -1)
                if event.key == pygame.K_RIGHT:
                    self.move(0, 1)
                if event.key == pygame.K_UP:
                    self.move(-1, 0)
                if event.key == pygame.K_DOWN:
                    self.move(1, 0)

            if event.type == pygame.QUIT:
                exit()

    def draw_window(self):
        self.window.fill((0, 0, 0))

        for y in range(self.height):
            for x in range(self.width):
                square = self.map[y][x]
                self.window.blit(
                    self.images[square], (x * self.scale, y * self.scale))

        painted_squares = self.count_black_squares() - self.start_black_squares
        game_text = self.game_font.render(
            f"Painted black: {painted_squares}", True, (255, 0, 0))
        self.window.blit(game_text, (25, self.height * self.scale + 10))

        game_text = self.game_font.render("F2 = new game", True, (255, 0, 0))
        self.window.blit(game_text, (225, self.height * self.scale + 10))

        game_text = self.game_font.render("Esc = exit game", True, (255, 0, 0))
        self.window.blit(game_text, (450, self.height * self.scale + 10))

        game_text = self.game_font.render(
            f"Higshscore = {self.highscore}", True, (255, 0, 0))
        self.window.blit(game_text, (675, self.height * self.scale + 10))

        if self.game_solved():
            # setting the highscore
            if painted_squares > self.highscore:
                self.highscore = painted_squares

            game_text = self.game_font.render(
                f"You painted {painted_squares} squares black!", True, (0, 255, 0))
            game_text_x = self.scale * self.width / 2 - game_text.get_width() / 2
            game_text_y = self.scale * self.height / 2 - game_text.get_height() / 2
            pygame.draw.rect(self.window, (0, 0, 0), (game_text_x,
                             game_text_y, game_text.get_width(), game_text.get_height()))
            self.window.blit(game_text, (game_text_x, game_text_y))

            skilljudgement = self.judgement()
            judgement_text = self.game_font.render(
                f"{skilljudgement}", True, (255, 255, 255))
            judgement_text_x = self.scale * self.width / 2 - judgement_text.get_width() / 2
            judgement_text_y = self.scale * self.height / \
                2 - judgement_text.get_height() / 2 + 30
            pygame.draw.rect(self.window, (0, 0, 0), (judgement_text_x, judgement_text_y,
                             judgement_text.get_width(), judgement_text.get_height()))
            self.window.blit(
                judgement_text, (judgement_text_x, judgement_text_y))

        if self.game_failed():
            fail_text = self.game_font.render(
                "Sorry, you failed the game. Press F2 to try again!", True, (255, 0, 0))
            fail_text_x = self.scale * self.width / 2 - fail_text.get_width() / 2
            fail_text_y = self.scale * self.height / 2 - fail_text.get_height() / 2
            pygame.draw.rect(self.window, (0, 0, 0), (fail_text_x,
                             fail_text_y, fail_text.get_width(), fail_text.get_height()))
            self.window.blit(fail_text, (fail_text_x, fail_text_y))

        pygame.display.flip()

    def find_robot(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] in [4, 6]:
                    return (y, x)

    def game_solved(self):
        # The game ends when the robot eliminate the Done-box
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] == 5:
                    return False
        return True

    def game_failed(self):
        # Game ends, if robot is boxed in
        if self.game_solved():
            return False

        robot_y, robot_x = self.find_robot()
        if (self.map[robot_y+1][robot_x] == 1 and
            self.map[robot_y-1][robot_x] == 1 and
            self.map[robot_y][robot_x+1] == 1 and
                self.map[robot_y][robot_x-1] == 1):
            return True
        return False

    def judgement(self):
        points = self.count_black_squares() - self.start_black_squares

        if points > 50:
            return "Okay I admit it - I'm not even sure if it's possible to paint it all black"
        if points > 45:
            return "You're a wizard. Keep pushing yourself"
        if points > 40:
            return "You are getting there!"
        if points > 35:
            return "That's quite impressive - not perfect though"
        if points > 30:
            return "You have some skills - was that your best try though?"
        if points > 25:
            return "Okay - but improvements could have been made"
        return "Surely you could have done better"

    def count_black_squares(self):
        black_tiles = 0
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x] == 1:
                    black_tiles += 1
        return black_tiles

    def move(self, move_y, move_x):
        if self.game_solved() or self.game_failed():
            return

        robot_old_y, robot_old_x = self.find_robot()
        robot_new_y = robot_old_y + move_y
        robot_new_x = robot_old_x + move_x

        if self.map[robot_new_y][robot_new_x] == 1:
            return

        if self.map[robot_old_y][robot_old_x] == 4:
            self.map[robot_old_y][robot_old_x] = 2

        if self.map[robot_old_y][robot_old_x] == 6:
            self.map[robot_old_y][robot_old_x] = 1

        if self.map[robot_new_y][robot_new_x] == 5:
            self.game_solved()
            self.map[robot_new_y][robot_new_x] = 4
            return

        self.map[robot_new_y][robot_new_x] += 4


if __name__ == "__main__":
    PaintItBlack()
