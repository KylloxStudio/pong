from ursina import *

app = Ursina()

window.color = color.black
window.fps_counter.enabled = False
window.exit_button.visible = False
camera.orthographic = True
camera.fov = 1

left_paddle = Entity(scale=(1/32,6/32), x=-.75, model='quad', origin_x=.5, collider='box')
right_paddle = duplicate(left_paddle, x=left_paddle.x*-1, rotation_z=left_paddle.rotation_z+180)

floor = Entity(model='quad', y=-.5, origin_y=.5, collider='box', scale=(2,10), visible=False)
ceiling = duplicate(floor, y=.5, rotation_z=180, visible=False)
left_wall = duplicate(floor, x=-.5*window.aspect_ratio, rotation_z=90, visible=True)
right_wall = duplicate(floor, x=.5*window.aspect_ratio, rotation_z=-90, visible=True)

collision_cooldown = .15
ball = Entity(model='circle', scale=.05, collider='box', speed=0, velocity=0, collision_cooldown=collision_cooldown)

isGameOver = True
info_text = Text("press space to play", origin=(-.25,15))

def update():
  global isGameOver, info_text
  if isGameOver:
    return

  if ball.x >= 1:
    info_text = Text("player A win. press space to restart", origin=(-.25,15))
    isGameOver = True
  elif ball.x <= -1:
    info_text = Text("player B win. press space to restart", origin=(-.25,15))
    isGameOver = True

  if ball.y > 0.49:
    ball.y -= 0.05
  elif ball.y < -0.49:
    ball.y += 0.05
  
  ball.collision_cooldown -= time.dt
  ball.position += ball.right * time.dt * ball.speed

  if left_paddle.y > 0.5:
    left_paddle.y = 0.5
  elif left_paddle.y < -0.5:
    left_paddle.y = -0.5
  
  if right_paddle.y > 0.5:
    right_paddle.y = 0.5
  elif right_paddle.y < -0.5:
    right_paddle.y = -0.5

  left_paddle.y += (held_keys['w'] - held_keys['s']) * time.dt * 1
  right_paddle.y += (held_keys['up arrow'] - held_keys['down arrow']) * time.dt * 1
  
  if ball.collision_cooldown > 0:
    return

  hit_info = ball.intersects()
  if hit_info.hit:
    if hit_info.entity in (left_paddle, right_paddle, left_wall, right_wall):
      ball.collision_cooldown = collision_cooldown
      # hit_info.entity.collision = False
      invoke(setattr, hit_info.entity, 'collision', True, delay=.1)
      if hit_info.entity == left_paddle:
        ball.velocity = 1
        direction_multiplier = -1
        # left_paddle.collision = True
        # right_paddle.collision = True
      elif hit_info.entity == right_paddle:
        ball.velocity = -1
        direction_multiplier = 1
        # right_paddle.collision = True
        # left_paddle.collision = True
      elif hit_info.entity == right_wall:
        info_text = Text("player A win. press space to restart", origin=(-.25,15))
        isGameOver = True
      elif hit_info.entity == left_wall:
        info_text = Text("player B win. press space to restart", origin=(-.25,15))
        isGameOver = True

      if hit_info.entity != right_wall and hit_info.entity != left_wall:
        ball.rotation_z += 180 * direction_multiplier
        ball.rotation_z -= (hit_info.entity.world_y - ball.y) * 20 * 32 * direction_multiplier
        if ball.speed < 30:
          ball.speed *= 1.2
    else:
      if ball.speed < 30:
        ball.speed *= 1.1

      if hit_info.world_normal.normalized()[1] == 0:
        ball.rotation_z *= -abs(ball.velocity)
      else:
        ball.rotation_z *= -abs(hit_info.world_normal.normalized()[1])

    particle = Entity(model='quad', position=hit_info.world_point, scale=0, texture='circle', add_to_scene_entities=False)
    particle.animate_scale(.2, .5, curve=curve.out_expo)
    particle.animate_color(color.clear, duration=.5, curve=curve.out_expo)
    destroy(particle, delay=.5)


def reset():
  global isGameOver
  info_text.enabled = False
  info_text.enabled = False
  info_text.enabled = False
  ball.position = (0,0,0)
  ball.rotation = (0,0,0)
  ball.speed = 10
  ball.velocity = -1
  for paddle in (left_paddle, right_paddle):
    paddle.collision = True
    paddle.y = 0
  for wall in (left_wall, right_wall):
    wall.collision = True
  isGameOver = False

def input(key):
  global isGameOver
  if key == 'space' and isGameOver:
    reset()

  if key == 't':
    ball.speed += 5

app.run()
