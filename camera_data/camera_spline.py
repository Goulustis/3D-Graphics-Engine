import numpy as np
import scipy
import json

cam_spline_path = "/home/jesus/projects/3D-Graphics-Engine/camera_data/camera_spline.npy"
intrinsics_path = "/home/jesus/projects/3D-Graphics-Engine/camera_data/intrinsics.json"
# intrinsics_path = "/home/jesus/projects/3D-Graphics-Engine/camera_data/ori_intrinsics.json"


def read_intrinsics(intrxs_path):
    with open(intrxs_path, "r") as f:
        data = json.load(f)

    cx = data["principal_point_x"]
    cy = data["principal_point_y"]
    fx = fy = data["focal_length"]

    return fx, fy, cx, cy
    # return np.array([[fx, 0, cx],
    #                  [0, fy, cy],
    #                  [0, 0, 1]])

class CameraSpline:
    def __init__(self, filename=cam_spline_path):
        splinerep = np.load(filename, allow_pickle=True).item()
        self.eyerep = splinerep["eye"]
        self.targetrep = splinerep["target"]
        self.uprep = splinerep["up"]

        self.intrinsics = read_intrinsics(intrinsics_path)

    def interpolate(self, times, model = "other"):
        """Interpolate the camera spline at the given times.
        
        Args:
            times: A numpy array of shape (N, ) containing the times in
                microseconds.
        
        Returns:
            positions: A numpy array of shape (N, 3) containing the camera
                positions in world coordinates.
            rotations: A numpy array of shape (N, 3, 3) containing the world to
                camera rotations.
        """
        times = np.array(times, dtype=np.float64) / 1e7
        eye = np.stack(scipy.interpolate.splev(times, self.eyerep), axis=-1)
        target = np.stack(scipy.interpolate.splev(times, self.targetrep),
                          axis=-1)
        up = np.stack(scipy.interpolate.splev(times, self.uprep), axis=-1)

        forward = target - eye
        forward /= np.linalg.norm(forward, axis=-1, keepdims=True)
        right = np.cross(forward, up)
        right /= np.linalg.norm(right, axis=-1, keepdims=True)
        up = np.cross(right, forward)
        up /= np.linalg.norm(up, axis=-1, keepdims=True)

        return right, up, forward, eye
    
    def get_fow(self):
        fx, fy, cx, cy = self.intrinsics
        return 2*np.arctan(cy/fy)



if __name__ == "__main__":
    cs = CameraSpline("synthetic_scene/camera_spline.npy")
    eye, rot = cs.interpolate(np.linspace(0, 1e7, 10))
    print(np.einsum("nij,nj->ni", rot, eye))
