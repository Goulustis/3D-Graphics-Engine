import glm
import pygame as pg
from camera_data.camera_spline import CameraSpline
import numpy as np

FOV = 50  # deg
NEAR = 0.1
FAR = 100
SPEED = 0.005
SENSITIVITY = 0.04

class Camera:
    def __init__(self, app, position=(0, 0, 4), yaw=-90, pitch=0):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(position)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.yaw = yaw
        self.pitch = pitch
        # view matrix
        self.m_view = self.get_view_matrix()
        # projection matrix
        self.m_proj = self.get_projection_matrix()

    def rotate(self):
        rel_x, rel_y = pg.mouse.get_rel()
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self):
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self):
        velocity = SPEED * self.app.delta_time
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.position += self.forward * velocity
        if keys[pg.K_s]:
            self.position -= self.forward * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_q]:
            self.position += self.up * velocity
        if keys[pg.K_e]:
            self.position -= self.up * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)


class PlayCamera(Camera):
    def __init__(self, app, position=(0, 0, 4), yaw=-90, pitch=0):
        self.camera_spline = CameraSpline()
        self.triggers = np.loadtxt("camera_data/triggers.txt")
        self.trig_idx = 0
        self.near, self.far = 1e-3, 50

        self.fow = self.camera_spline.get_fow()
        right, up, forward, pos = self.camera_spline.interpolate(self.triggers[self.trig_idx])
        super().__init__(app, pos, yaw, pitch)

        self.up = glm.vec3(*up)
        self.right = glm.vec3(*right)
        self.forward = glm.vec3(*forward)

        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()

        self.trig_idx += 1

        self.done = False   # if the thing is done playing
    
    def rotate(self):
        pass

    def update_camera_vectors(self):
        if self.trig_idx >= len(self.triggers):
            self.app.attr["done"] = True
            return
        time = self.triggers[self.trig_idx]
        right, up, forward, pos = self.camera_spline.interpolate(time)
        self.right = glm.vec3(*right)
        self.up = glm.vec3(*up)
        self.forward = glm.vec3(*forward)
        self.position = glm.vec3(*pos)
        
        self.trig_idx += 1
    
    def update(self):
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()
    
    def move(self):
        pass
    
    
    def get_projection_matrix(self):
        return glm.perspective(self.fow, self.aspect_ratio, self.near, self.far)