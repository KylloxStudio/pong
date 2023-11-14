from ursina import *

app = Ursina()

window.color = color.black
window.fps_counter.enabled = False
window.exit_button.visible = False
camera.orthographic = True
camera.fov = 1

left_paddle = Entity(scale=(1/32,6/32), x=-.75, model='quad', origin_x=.5, collider='box', speed=1)
right_paddle = duplicate(left_paddle, x=left_paddle.x*-1, rotation_z=left_paddle.rotation_z+180, speed=1)

floor = Entity(model='quad', y=-.5, origin_y=.5, collider='box', scale=(2,10), visible=False)
ceiling = duplicate(floor, y=.5, rotation_z=180, visible=False)
left_wall = duplicate(floor, x=-.5*window.aspect_ratio, rotation_z=90, visible=True)
right_wall = duplicate(floor, x=.5*window.aspect_ratio, rotation_z=-90, visible=True)

collision_cooldown = .15
ball = Entity(model='circle', scale=.05, collider='box', speed=0, velocity=0, collision_cooldown=collision_cooldown)

isGameOver = True
right_isUsingSkill = False
left_isUsingSkill = False
right_skillCool = 5.0
left_skillCool = 5.0
info_text = Text("press space to play", origin=(-.25,15))

def update():
  global isGameOver, right_isUsingSkill, left_isUsingSkill, right_skillCool, left_skillCool, info_text
  if isGameOver:
    return

  # 플레이어 B가 스킬 사용 시
  if right_isUsingSkill:
    right_paddle.speed = 2
    # 쿨타임 연산
    if right_skillCool <= 0:
      right_skillCool = 5.0
  else:
    right_skillCool -= time.dt

  # 플레이어 A가 스킬 사용 시
  if left_isUsingSkill:
    left_paddle.speed = 2
    # 쿨타임 연산
    if left_skillCool <= 0:
      left_skillCool = 5.0
  else:
    left_skillCool -= time.dt

  # 승패 결정
  if ball.x >= 1:
    info_text = Text("player A win. press space to restart", origin=(-.25,15))
    isGameOver = True
  elif ball.x <= -1:
    info_text = Text("player B win. press space to restart", origin=(-.25,15))
    isGameOver = True

  # 공 탈출 방지
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

  left_paddle.y += (held_keys['w'] - held_keys['s']) * time.dt * left_paddle.speed
  right_paddle.y += (held_keys['up arrow'] - held_keys['down arrow']) * time.dt * right_paddle.speed

  
  if ball.collision_cooldown > 0:
    return

  hit_info = ball.intersects()
  if hit_info.hit:
    if hit_info.entity in (left_paddle, right_paddle, left_wall, right_wall):
      ball.collision_cooldown = collision_cooldown
      invoke(setattr, hit_info.entity, 'collision', True, delay=.1)
      if hit_info.entity == left_paddle:
        if ball.color == color.red:
          ball.color = color.white
        if left_isUsingSkill: # 스킬 사용 시
          ball.speed += 10
          ball.color = color.red
          left_paddle.color = color.white
          left_paddle.speed = 1
          left_isUsingSkill = False
        ball.velocity = 1
        direction_multiplier = -1
      elif hit_info.entity == right_paddle:
        if ball.color == color.red:
          ball.color = color.white
        if right_isUsingSkill: # 스킬 사용 시
          ball.speed += 10
          ball.color = color.red
          right_paddle.color = color.white
          right_paddle.speed = 1
          right_isUsingSkill = False
        ball.velocity = -1
        direction_multiplier = 1
      # 승패 결정
      elif hit_info.entity == right_wall:
        info_text = Text("player A win. press space to restart", origin=(-.25,15))
        isGameOver = True
      elif hit_info.entity == left_wall:
        info_text = Text("player B win. press space to restart", origin=(-.25,15))
        isGameOver = True

      if hit_info.entity != right_wall and hit_info.entity != left_wall:
        ball.rotation_z += 180 * direction_multiplier
        ball.rotation_z -= (hit_info.entity.world_y - ball.y) * 20 * 32 * direction_multiplier
        ball.speed *= 1.1
    else: # 벽 충돌 시 각도 계산
      ball.speed *= 1.1
      if hit_info.world_normal.normalized()[1] == 0:
        ball.rotation_z *= -abs(ball.velocity)
      else:
        ball.rotation_z *= -abs(hit_info.world_normal.normalized()[1])

    particle = Entity(model='quad', position=hit_info.world_point, scale=0, texture='circle', add_to_scene_entities=False)
    particle.animate_scale(.2, .5, curve=curve.out_expo)
    particle.animate_color(color.clear, duration=.5, curve=curve.out_expo)
    destroy(particle, delay=.5)

# 초기화 (다시 시작)
def reset():
  global isGameOver, right_isUsingSkill, left_isUsingSkill, left_skillCool, right_skillCool, skill_text, info_text
  info_text.enabled = False
  ball.position = (0,0,0)
  ball.rotation = (0,0,0)
  ball.speed = 10
  ball.velocity = -1
  ball.color = color.white
  for paddle in (left_paddle, right_paddle):
    paddle.color = color.white
    paddle.speed = 1
    paddle.collision = True
    paddle.y = 0
  for wall in (left_wall, right_wall):
    wall.collision = True
  left_skillCool = 5.0
  right_skillCool = 5.0
  left_isUsingSkill = False
  right_isUsingSkill = False
  isGameOver = False

# 키 입력
def input(key):
  global isGameOver, left_skillCool, right_skillCool, left_isUsingSkill, right_isUsingSkill

  if isGameOver:
    if key == 'space': # 게임 시작
      reset()
  else:
    # 스킬 사용 (쉬프트)
    if key == 'left shift' and left_skillCool <= 0:
      left_isUsingSkill = True
      left_paddle.color = color.red

    if key == 'right shift' and right_skillCool <= 0:
      right_isUsingSkill = True
      right_paddle.color = color.red

app.run()
