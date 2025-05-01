from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Global variables
fovY = 100
player_pos = [0, 0, 0]
gun_angle = 0
camera_mode = "third"
firstperson_angle = 0
camera_distance = 500
camera_height = 500
camera_angle = 0
cheat_mode = False
auto_camera = False
bullets = []
enemies = []
life = 5
missed_bullets = 0
score = 0
game_over = False
enemy_speed = 0.05
bullet_speed = 5
step_toggle = False
cheat_fire_cooldown = 0.05  # seconds between shots
next_cheat_fire_time = 0   # next time when a shot is allowed
GRID_LENGTH = 500


# Initialize enemies
for _ in range(5):
    enemies.append({
        'pos': [random.randint(-400, 400), 0, random.randint(-400, 400)],
        'scale': 1.0,
        'scale_dir': 0.01
    })

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    global step_toggle
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    
    glPushMatrix()
    glRotatef(gun_angle, 0, 1, 0)

    glPushMatrix()
    glTranslatef(0, 30, 0)
    glColor3f(0, 0.3, 0)
    glScalef(30, 20, 15)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0, 0, 0)
    glTranslatef(0, 55, 0)
    glutSolidSphere(12, 20, 20)
    glPopMatrix()

    glPushMatrix()
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * 10, 40, 5)
        glColor3f(0.9, 0.75, 0.65)
        glutSolidSphere(4, 10, 10)
        gluCylinder(gluNewQuadric(), 3, 3, 35, 10, 10)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 40, 20)
    glColor3f(0.5, 0.5, 0.5)
    gluCylinder(gluNewQuadric(), 2.5, 2.5, 40, 10, 10)
    glPopMatrix()
    glPopMatrix()

    leg_tilt_angle = 0
    leg_length = 20 
    leg_positions = [(-10, 20, 0), (10, 20, 0)]
    glColor3f(0, 0, .5)
    for i, pos in enumerate(leg_positions):
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        tilt_dir = leg_tilt_angle if (i == 0 and step_toggle) or (i == 1 and not step_toggle) else -leg_tilt_angle
        glRotatef(90 + tilt_dir, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3, 3, leg_length, 10, 10)
        glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

def draw_enemy(enemy):
    glPushMatrix()
    glTranslatef(enemy['pos'][0], 30, enemy['pos'][2])
    glScalef(enemy['scale'], enemy['scale'], enemy['scale'])
    glColor3f(1, 0, 0)
    glutSolidSphere(30, 20, 20)
    glTranslatef(0, 40, 0)
    glColor3f(0, 0, 0)
    glutSolidSphere(15, 20, 20)
    glPopMatrix()

def draw_bullet(bullet):
    glPushMatrix()
    glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
    glColor3f(1, 0, 0)
    glutSolidCube(7)
    glPopMatrix()

def draw_grid():
    tile_size = 50
    for x in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
        for z in range(-GRID_LENGTH, GRID_LENGTH, tile_size):
            glColor3f(1, 1, 1) if ((x + z) // tile_size) % 2 == 0 else glColor3f(0.8, 0.6, 0.9)
            glBegin(GL_QUADS)
            glVertex3f(x, 0, z)
            glVertex3f(x + tile_size, 0, z)
            glVertex3f(x + tile_size, 0, z + tile_size)
            glVertex3f(x, 0, z + tile_size)
            glEnd()

def draw_boundaries():
    boundary_height = 50
    def boundary_face(color, verts):
        glColor3f(*color)
        glBegin(GL_QUADS)
        for v in verts:
            glVertex3f(*v)
        glEnd()
    boundary_face((0,0,1), [(-GRID_LENGTH,0,-GRID_LENGTH),(-GRID_LENGTH,boundary_height,-GRID_LENGTH),(-GRID_LENGTH,boundary_height,GRID_LENGTH),(-GRID_LENGTH,0,GRID_LENGTH)])
    boundary_face((1,1,1), [(-GRID_LENGTH,0,GRID_LENGTH),(-GRID_LENGTH,boundary_height,GRID_LENGTH),(GRID_LENGTH,boundary_height,GRID_LENGTH),(GRID_LENGTH,0,GRID_LENGTH)])
    boundary_face((0,1,0), [(GRID_LENGTH,0,GRID_LENGTH),(GRID_LENGTH,boundary_height,GRID_LENGTH),(GRID_LENGTH,boundary_height,-GRID_LENGTH),(GRID_LENGTH,0,-GRID_LENGTH)])
    boundary_face((0,1,1), [(GRID_LENGTH,0,-GRID_LENGTH),(GRID_LENGTH,boundary_height,-GRID_LENGTH),(-GRID_LENGTH,boundary_height,-GRID_LENGTH),(-GRID_LENGTH,0,-GRID_LENGTH)])

def keyboardListener(key, x, y):
    global gun_angle, cheat_mode, auto_camera, game_over, life, missed_bullets, score, step_toggle, player_pos
    key = key.decode('utf-8').lower()
    if game_over and key == 'r':
        game_over = False
        life, missed_bullets, score = 5, 0, 0
        player_pos[:] = [0, 0, 0]
        enemies.clear()
        for _ in range(5):
            enemies.append({'pos': [random.randint(-400, 400), 0, random.randint(-400, 400)], 'scale': 1.0, 'scale_dir': 0.01})
        bullets.clear()
        return

    move = {'w': 10, 's': -10}.get(key, 0)
    if move:
        delta_x = math.sin(math.radians(gun_angle)) * move
        delta_z = math.cos(math.radians(gun_angle)) * move
        player_pos[0] += delta_x
        player_pos[2] += delta_z
        step_toggle = not step_toggle
    elif key == 'a': gun_angle += 5
    elif key == 'd': gun_angle -= 5
    elif key == 'c': 
        cheat_mode = not cheat_mode
    elif key == 'v' and cheat_mode: 
        auto_camera = not auto_camera
        if auto_camera:
            camera_fp_angle = gun_angle 
def specialKeyListener(key, x, y):
    global camera_height, camera_angle
    camera_height += 10 if key == GLUT_KEY_UP else -10 if key == GLUT_KEY_DOWN else 0
    camera_angle += 5 if key == GLUT_KEY_LEFT else -5 if key == GLUT_KEY_RIGHT else 0
    camera_height = max(100, min(camera_height, 1500))
    camera_angle %= 360

def mouseListener(button, state, x, y):
    global camera_mode, camera_fp_angle
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        bullets.append({'pos': player_pos[:], 'dir': [math.sin(math.radians(gun_angle)), 0, math.cos(math.radians(gun_angle))], 'active': True})
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == "third":
            camera_mode = "first"
            camera_fp_angle = gun_angle  # Sync camera to gun when entering first-person
        else:
            camera_mode = "third"



def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode == "third":
        cam_x = player_pos[0] + math.sin(math.radians(camera_angle)) * camera_distance
        cam_z = player_pos[2] + math.cos(math.radians(camera_angle)) * camera_distance
        look_y = max(player_pos[1] + 100, player_pos[1] + camera_height * 0.1)
        gluLookAt(cam_x, camera_height, cam_z, 
                  player_pos[0], look_y, player_pos[2],
                  0, 1, 0)
    else:
        # Use camera_fp_angle, not gun_angle
        cam_x = player_pos[0] + math.sin(math.radians(camera_fp_angle)) * 20
        cam_z = player_pos[2] + math.cos(math.radians(camera_fp_angle)) * 20
        gluLookAt(cam_x, 100, cam_z, 
                  cam_x + math.sin(math.radians(camera_fp_angle)) * 100, 50, cam_z + math.cos(math.radians(camera_fp_angle)) * 100, 
                  0, 1, 0)


def check_collisions():
    global score, life, missed_bullets, game_over
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            bx, by, bz = bullet['pos']
            ex, ey, ez = enemy['pos'][0], 30, enemy['pos'][2]
            if math.dist([bx, by, bz], [ex, ey, ez]) < 50:
                score += 10
                enemy['pos'][0], enemy['pos'][2] = random.randint(-400, 400), random.randint(-400, 400)
                bullets.remove(bullet)
                break
        if abs(bullet['pos'][0]) > GRID_LENGTH or abs(bullet['pos'][2]) > GRID_LENGTH:
            missed_bullets += 1
            bullets.remove(bullet)
            if missed_bullets >= 10:
                game_over = True
    for enemy in enemies:
        if math.dist([player_pos[0], 0, player_pos[2]], [enemy['pos'][0], 30, enemy['pos'][2]]) < 50:
            life -= 1
            enemy['pos'][0], enemy['pos'][2] = random.randint(-400, 400), random.randint(-400, 400)
            if life <= 0:
                game_over = True

def update_enemies():
    for enemy in enemies:
        dx = player_pos[0] - enemy['pos'][0]
        dz = player_pos[2] - enemy['pos'][2]
        dist = math.sqrt(dx**2 + dz**2)
        if dist > 0:
            enemy['pos'][0] += (dx/dist) * enemy_speed
            enemy['pos'][2] += (dz/dist) * enemy_speed
        enemy['scale'] += enemy['scale_dir']
        if enemy['scale'] > 1.2 or enemy['scale'] < 0.8:
            enemy['scale_dir'] *= -1

def update_bullets():
    for bullet in bullets:
        bullet['pos'][0] += bullet['dir'][0] * bullet_speed
        bullet['pos'][2] += bullet['dir'][2] * bullet_speed


def idle():
    global gun_angle, next_cheat_fire_time, cheat_fire_cooldown, camera_fp_angle
    if not game_over:
        if cheat_mode:
            gun_angle = (gun_angle + 2)
            current_time = time.time()
            if enemy_in_line_of_sight() and current_time >= next_cheat_fire_time:
                fire_bullet()
                next_cheat_fire_time = current_time + cheat_fire_cooldown

        # Camera logic for first-person mode
        if camera_mode == "first":
            if cheat_mode and auto_camera:
                camera_fp_angle = gun_angle
            # else: keep camera_fp_angle unchanged (fixed at entry angle)
        
        update_enemies()
        update_bullets()
        check_collisions()
    glutPostRedisplay()




def enemy_in_line_of_sight():
    # Tolerance angle for "in sight"
    tolerance = 5  # degrees
    for enemy in enemies:
        dx = enemy['pos'][0] - player_pos[0]
        dz = enemy['pos'][2] - player_pos[2]
        angle_to_enemy = math.degrees(math.atan2(dx, dz)) % 360
        gun_angle_mod = gun_angle % 360
        if abs((angle_to_enemy - gun_angle_mod + 180) % 360 - 180) < tolerance:
            return True
    return False
 
def fire_bullet():
    bullets.append({
        'pos': player_pos[:],
        'dir': [math.sin(math.radians(gun_angle)), 0, math.cos(math.radians(gun_angle))],
        'active': True
    })
    

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800) 
    setupCamera()
    draw_grid()
    draw_boundaries()
    draw_player()
    for enemy in enemies: draw_enemy(enemy)
    for bullet in bullets: draw_bullet(bullet)
    draw_text(10, 770, f"Player Life Remaining {life} ")
    draw_text(10,745,f"Game Score: {score}")
    draw_text(10,720,f"Player Bullet Missed: {missed_bullets}")
    if game_over:
        draw_text(400, 600, f"GAME is Over. Your score is: {score}") 
        draw_text(460, 575, 'Press "R" to restart')
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0,0)
    wind = glutCreateWindow(b"Bullet Frenzy Game")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
