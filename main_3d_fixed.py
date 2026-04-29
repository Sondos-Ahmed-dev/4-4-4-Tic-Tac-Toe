# main_3d_gui.py
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from board import Board
from ai_agent import find_best_move
import time

# ---------- Utility: Ray-AABB intersection (slab method) ----------
def ray_intersect_aabb(ray_origin, ray_dir, aabb_min, aabb_max):
    tmin = (aabb_min[0] - ray_origin[0]) / (ray_dir[0] if ray_dir[0] != 0 else 1e-8)
    tmax = (aabb_max[0] - ray_origin[0]) / (ray_dir[0] if ray_dir[0] != 0 else 1e-8)
    if tmin > tmax: tmin, tmax = tmax, tmin
    tymin = (aabb_min[1] - ray_origin[1]) / (ray_dir[1] if ray_dir[1] != 0 else 1e-8)
    tymax = (aabb_max[1] - ray_origin[1]) / (ray_dir[1] if ray_dir[1] != 0 else 1e-8)
    if tymin > tymax: tymin, tymax = tymax, tymin
    if (tmin > tymax) or (tymin > tmax):
        return False, None
    if tymin > tmin:
        tmin = tymin
    if tymax < tmax:
        tmax = tymax
    tzmin = (aabb_min[2] - ray_origin[2]) / (ray_dir[2] if ray_dir[2] != 0 else 1e-8)
    tzmax = (aabb_max[2] - ray_origin[2]) / (ray_dir[2] if ray_dir[2] != 0 else 1e-8)
    if tzmin > tzmax: tzmin, tzmax = tzmax, tzmin
    if (tmin > tzmax) or (tzmin > tmax):
        return False, None
    if tzmin > tmin:
        tmin = tzmin
    return True, tmin

# ---------- Draw cube ----------
def draw_cube(size=0.5):
    vertices = [
        [-size,-size,-size],[size,-size,-size],[size,size,-size],[-size,size,-size],
        [-size,-size,size],[size,-size,size],[size,size,size],[-size,size,size]
    ]
    faces = [
        (0,1,2,3),(4,5,6,7),
        (0,1,5,4),(2,3,7,6),
        (0,3,7,4),(1,2,6,5)
    ]
    glBegin(GL_QUADS)
    for face in faces:
        for v in face:
            glVertex3fv(vertices[v])
    glEnd()
    # edges
    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]
    glColor3f(0,0,0)
    glBegin(GL_LINES)
    for e in edges:
        glVertex3fv(vertices[e[0]])
        glVertex3fv(vertices[e[1]])
    glEnd()

# ---------- Main Game ----------
class Main3D:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("4x4x4 Qubic - Menu")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 64)
        self.font_med = pygame.font.SysFont(None, 36)
        self.state = "menu"
        self.mode = None
        self.board = None
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.winning_line = None
        self.win_time = None
        self.celebration_duration = 3.0  
        # camera
        self.rot_x = -30.0
        self.rot_y = 45.0
        self.zoom = -15.0
        self.dragging = False
        self.last_pos = (0,0)
        # board layout params
        self.cube_size = 0.35
        self.gap = 1.5
        self.offset = 1.5 * self.gap
        # hover tracking
        self.hovered_cube = None

    def reset_game(self):
        self.board = Board()
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.winning_line = None
        self.win_time = None

    # ---------- 2D Menu ----------
    def menu_loop(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    return False
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    mx,my = ev.pos
                    b1 = pygame.Rect(250,250,200,100)
                    b2 = pygame.Rect(550,250,200,100)
                    if b1.collidepoint(mx,my):
                        self.mode = 1
                        self.start_game_gl()
                        return True
                    if b2.collidepoint(mx,my):
                        self.mode = 2
                        self.start_game_gl()
                        return True
            self.screen.fill((20,20,50))
            b1 = pygame.Rect(250,250,200,100)
            b2 = pygame.Rect(550,250,210,100)
            pygame.draw.rect(self.screen,(255, 100, 100),b1,border_radius=15)
            pygame.draw.rect(self.screen,(100, 255, 150),b2,border_radius=15)
            self.screen.blit(self.font_big.render("1 Player", True, (255,255,255)), (260,270))
            self.screen.blit(self.font_big.render("2 Players", True, (255,255,255)), (560,270))
            instr = [
                "Left-Drag = rotate board",
                "Right-Click = place move",
                "Mouse Wheel = Zoom In/Out",
                "R = Reset | M = Menu"
            ]
            for i,t in enumerate(instr):
                self.screen.blit(self.font_med.render(t, True, (200,200,200)), (20, 20 + i*28))
            pygame.display.flip()
            self.clock.tick(60)

    # ---------- Initialize OpenGL ----------
    def start_game_gl(self):
        pygame.display.set_mode(    (800, 600),
                                pygame.RESIZABLE |  DOUBLEBUF | OPENGL)
        pygame.display.set_caption("4x4x4 Qubic - Play")
        glViewport(0,0,self.width,self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.width/self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (5,5,5,1))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5,0.5,0.5,1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1,1,1,1))
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        self.board = Board()
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.winning_line = None
        self.win_time = None
        self.state = "playing"
        self.rot_x = -30.0
        self.rot_y = 45.0
        self.zoom = -15.0
        self.dragging = False

    # ---------- Mouse ray ----------
    def mouse_ray(self, mouse_x, mouse_y):
        model = glGetDoublev(GL_MODELVIEW_MATRIX)
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        view = glGetIntegerv(GL_VIEWPORT)
        win_x = float(mouse_x)
        win_y = float(view[3]) - float(mouse_y)
        near = gluUnProject(win_x, win_y, 0.0, model, proj, view)
        far = gluUnProject(win_x, win_y, 1.0, model, proj, view)
        ray_origin = (near[0], near[1], near[2])
        ray_dir = (far[0]-near[0], far[1]-near[1], far[2]-near[2])
        length = max((ray_dir[0]**2 + ray_dir[1]**2 + ray_dir[2]**2)**0.5, 1e-8)
        ray_dir = (ray_dir[0]/length, ray_dir[1]/length, ray_dir[2]/length)
        return ray_origin, ray_dir

    # ---------- Get cube at mouse ----------
    def get_cube_at_mouse(self, mouse_pos):
        mx,my = mouse_pos
        ray_o, ray_d = self.mouse_ray(mx,my)
        best_t = float('inf')
        best_cube = None 
        size = self.cube_size
        gap = self.gap
        offset = self.offset
        import math
        import numpy as np
        rx = math.radians(self.rot_x)
        ry = math.radians(self.rot_y)
        Rx = np.array([[1,0,0,0],
                       [0, math.cos(rx), -math.sin(rx), 0],
                       [0, math.sin(rx), math.cos(rx), 0],
                       [0,0,0,1]])
        Ry = np.array([[math.cos(ry),0,math.sin(ry),0],
                       [0,1,0,0],
                       [-math.sin(ry),0,math.cos(ry),0],
                       [0,0,0,1]])
        T = np.array([[1,0,0,0],
                      [0,1,0,0],
                      [0,0,1,self.zoom],
                      [0,0,0,1]])
        M = T.dot(Rx).dot(Ry)
        for z in range(4):
            for y in range(4):
                for x in range(4):
                    cx = x*gap - offset
                    cy = y*gap - offset
                    cz = z*gap - offset
                    local_min = np.array([cx - size, cy - size, cz - size, 1.0])
                    local_max = np.array([cx + size, cy + size, cz + size, 1.0])
                    world_min = M.dot(local_min)[:3]
                    world_max = M.dot(local_max)[:3]
                    aabb_min = tuple(np.minimum(world_min, world_max))
                    aabb_max = tuple(np.maximum(world_min, world_max))
                    hit, t = ray_intersect_aabb(ray_o, ray_d, aabb_min, aabb_max)
                    if hit and t is not None and t < best_t:
                        best_t = t
                        best_cube = (z,y,x)
        return best_cube

    # ---------- Draw 3D board ----------
    def draw_board(self):
        glPushMatrix()
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.rot_x, 1.0, 0.0, 0.0)
        glRotatef(self.rot_y, 0.0, 1.0, 0.0)
        size = self.cube_size
        gap = self.gap
        offset = self.offset
        

        if self.mode == 1:
            current_player_color = (1.0, 0.2, 0.2)
        else:
            current_player_color = (1.0, 0.2, 0.2) if self.player_turn else (0.2, 0.5, 1.0)
        

        pulse = 1.0
        draw_glow = False
        if self.winning_line and self.win_time:
            elapsed = time.time() - self.win_time

            pulse = 1.0 + 0.15 * abs(pygame.math.Vector2(1, 0).rotate(elapsed * 360).x)
        elif self.winner == "Draw" and self.win_time:
            draw_glow = True
            elapsed = time.time() - self.win_time
            pulse = 1.0 + 0.08 * abs(pygame.math.Vector2(1, 0).rotate(elapsed * 180).x)
        
        for z in range(4):
            for y in range(4):
                for x in range(4):
                    glPushMatrix()
                    glTranslatef(x*gap - offset, y*gap - offset, z*gap - offset)
                    p = self.board.board[z][y][x]
                    
                    is_winning = self.winning_line and (z,y,x) in self.winning_line
                    is_hovered = self.hovered_cube == (z,y,x) and p == 0 and not self.game_over
                    is_draw_cube = draw_glow and p != 0  
                    
                    
                    if is_winning:
                        cube_size = size * pulse  
                    elif is_draw_cube:
                        cube_size = size * pulse  
                    elif is_hovered:
                        cube_size = size * 1.2
                    else:
                        cube_size = size
                    
                    
                    if is_winning:
                        
                        golden_intensity = 0.7 + 0.3 * abs(pygame.math.Vector2(1, 0).rotate(time.time() * 180).x)
                        glColor3f(1.0, golden_intensity, 0.0)
                    elif is_draw_cube:
                        
                        if p == 1:
                            glColor3f(1.0, 0.4, 0.4) 
                        else:
                            glColor3f(0.4, 0.7, 1.0)  
                    elif is_hovered:
                        glColor3f(*current_player_color)
                    elif p == 1:
                        glColor3f(1.0, 0.2, 0.2)
                    elif p == -1:
                        glColor3f(0.2, 0.5, 1.0)
                    else:
                        glColor3f(0.3, 0.3, 0.3)
                    
                
                    if is_winning:
                        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.8, 0.6, 0.0, 1.0))
                    elif is_draw_cube:
                        if p == 1:
                            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.3, 0.1, 0.1, 1.0))
                        else:
                            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.1, 0.2, 0.3, 1.0))
                    elif is_hovered:
                        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (*current_player_color, 1.0))
                    
                    draw_cube(cube_size)
                    
                    if is_winning or is_hovered or is_draw_cube:
                        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0,0,0,1))
                    
                    glPopMatrix()
        glPopMatrix()

    # ---------- Game Over Screen ----------
    def show_game_over_screen(self):
        pygame.display.set_mode((self.width, self.height))
        self.screen = pygame.display.get_surface()
        while True:
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    return "quit"
                if ev.type == KEYDOWN:
                    if ev.key == K_m:
                        return "menu"
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    mx,my = ev.pos
                    btn_play = pygame.Rect(self.width//2-120, self.height//2+100, 240, 50)
                    btn_menu = pygame.Rect(self.width//2-120, self.height//2+170, 240, 50)
                    if btn_play.collidepoint(mx,my):
                        self.start_game_gl()
                        return "play_again"
                    if btn_menu.collidepoint(mx,my):
                        return "menu"
            
            self.screen.fill((20,20,20))
            

            if self.winner == "Draw":
                txt = "IT'S A DRAW!"
                color = (200, 200, 200)  
                msg = "No winner - Board is full!"
                msg_surf = self.font_med.render(msg, True, (150,150,150))
                self.screen.blit(msg_surf, (self.width//2 - msg_surf.get_width()//2, self.height//2 - 30))
            else:
                txt = f"{self.winner} WINS!"
                color = (255,215,0)  # لون ذهبي للفائز
                # عرض الخط الفايز
                if self.winning_line:
                    win_txt = "Winning Line: " + " → ".join([f"({z},{y},{x})" for z,y,x in self.winning_line])
                    win_surf = self.font_med.render(win_txt, True, (100,255,100))
                    self.screen.blit(win_surf, (self.width//2 - win_surf.get_width()//2, self.height//2 - 30))
            
            surf = self.font_big.render(txt, True, color)
            self.screen.blit(surf, (self.width//2 - surf.get_width()//2, self.height//2 - 100))
            
            btn_play = pygame.Rect(self.width//2-120, self.height//2+100, 240, 50)
            btn_menu = pygame.Rect(self.width//2-120, self.height//2+170, 240, 50)
            pygame.draw.rect(self.screen, (50,200,50), btn_play)
            pygame.draw.rect(self.screen, (200,50,50), btn_menu)
            self.screen.blit(self.font_med.render("Play Again", True, (0,0,0)), (self.width//2-60, self.height//2+110))
            self.screen.blit(self.font_med.render("Main Menu", True, (0,0,0)), (self.width//2-55, self.height//2+180))
            pygame.display.flip()
            self.clock.tick(60)

    # ---------- Main loop ----------
    def run(self):
        while True:
            if self.state == "menu":
                ok = self.menu_loop()
                if not ok:
                    return
            elif self.state == "playing":
                running = True
                while running and self.state == "playing":
                    for ev in pygame.event.get():
                        if ev.type == QUIT:
                            pygame.quit()
                            return
                        if ev.type == KEYDOWN:
                            if ev.key == K_r:
                                self.reset_game()
                            elif ev.key == K_m:
                                self.state = "menu"
                                pygame.display.set_mode((self.width, self.height))
                                self.screen = pygame.display.get_surface()
                                pygame.display.set_caption("4x4x4 Qubic - Menu")
                                
                                running = False
                                break

                    if ev.type == MOUSEWHEEL:
                        self.zoom += ev.y
        
                       
                    if ev.type == MOUSEBUTTONDOWN:
                        if ev.button == 4 :
                            self.zoom += 1.0
                        elif ev.button == 5:  # scroll down
                            self.zoom -= 1.0
                        elif ev.button == 1:
                            self.dragging = True
                            self.last_pos = ev.pos
                        elif ev.button == 3 and not self.game_over:
                            cube = self.get_cube_at_mouse(ev.pos)
                            if cube:
                                z,y,x = cube
                                if self.board.is_valid_move(z,y,x):
                                    if self.mode == 1:
                                        self.board.make_move(z,y,x,1)
                                        win_line = self.board.get_winning_line(1)
                                        if win_line:
                                            self.game_over = True
                                            self.winner = "Player 1"
                                            self.winning_line = win_line
                                            self.win_time = time.time()  
                                        else:
                                            ai_move = find_best_move(self.board)
                                            if ai_move and ai_move[0] is not None:
                                                self.board.make_move(*ai_move, -1)
                                                win_line = self.board.get_winning_line(-1)
                                                if win_line:
                                                    self.game_over = True
                                                    self.winner = "AI"
                                                    self.winning_line = win_line
                                                    self.win_time = time.time()
                                    else:
                                        player_val = 1 if self.player_turn else -1
                                        self.board.make_move(z,y,x,player_val)
                                        win_line = self.board.get_winning_line(player_val)
                                        if win_line:
                                            self.game_over = True
                                            self.winner = "Player 1" if player_val == 1 else "Player 2"
                                            self.winning_line = win_line
                                            self.win_time = time.time()
                                        self.player_turn = not self.player_turn
                                    if not self.game_over and self.board.is_game_over():
                                        self.game_over = True
                                        self.winner = "Draw"
                                        self.win_time = time.time()  
                    if ev.type == MOUSEBUTTONUP:
                        if ev.button == 1:
                            self.dragging = False
                    if ev.type == MOUSEMOTION:
                        if self.dragging:
                            dx = ev.pos[0] - self.last_pos[0]
                            dy = ev.pos[1] - self.last_pos[1]
                            self.rot_y += dx * 0.5
                            self.rot_x += dy * 0.5
                            self.last_pos = ev.pos
                        else:
                            self.hovered_cube = self.get_cube_at_mouse(ev.pos)

                    
                    if self.state != "playing":
                        break
                        
                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                    glClearColor(0.05,0.05,0.15,1.0)
                    self.draw_board()
                    pygame.display.flip()
                    self.clock.tick(60)

                    
                    if self.game_over and self.win_time:
                        elapsed = time.time() - self.win_time
                        if elapsed >= self.celebration_duration:
                            
                            res = self.show_game_over_screen()
                            if res == "quit":
                                return
                            if res == "menu":
                                self.state = "menu"
                                running = False
                                break
                            if res == "play_again":
                                continue

if __name__ == "__main__":
    Main3D().run()