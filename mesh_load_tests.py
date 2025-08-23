from timeit import Timer
import open3d as o3d
import numpy as np
import gzip
import io
import os
import shutil

from pointcloud_utils import load_df_pointcloud


def load_file_through_disk_open3d(filename):
    """ Loading with open3d, requires saving the decompressed ply file on disk

    """
    with gzip.open(filename, 'rb') as f_in:
        out_path = filename.rsplit('.', 1)[0]
        with open(out_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    pcd = o3d.io.read_point_cloud(out_path)

    # Remove file
    os.remove(out_path)
    # points = np.asarray(pcd.points)
    # print(f"loaded mesh through disk: {points.shape}")


def load_file_through_disk_plyfile(filename):
    """ Loading with open3d, requires saving the decompressed ply file on disk

    """
    with gzip.open(filename, 'rb') as f_in:
        out_path = filename.rsplit('.', 1)[0]
        with open(out_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    df, pcd = load_df_pointcloud(out_path, return_pointcloud=True)
    # Remove file
    os.remove(out_path)
    # points = np.asarray(pcd.points)
    # print(f"loaded mesh through disk: {points.shape} and {df.shape} fields in dataframe")


def load_file_through_memory_plyfile(filename):
    """ Loading with open3d, requires saving the decompressed ply file on disk

    """
    with open(filename, "rb") as f:
        compressed_bytes = f.read(-1)
    data = gzip.decompress(compressed_bytes)
    df, pcd = load_df_pointcloud(io.BytesIO(data), return_pointcloud=True)

    # points = np.asarray(pcd.points)
    # print(f"loaded pcd through memory: {points.shape} and {df.shape} fields in dataframe")


if __name__ == '__main__':
    # Time each function 10 times and print the results
    n = 10
    t1 = Timer(lambda: load_file_through_disk_open3d("example_data/example_pointcloud.ply.gz"))
    times1 = t1.repeat(repeat=n, number=1)
    print(f"open3D disk: avg={np.mean(times1):.3f}s, std={np.std(times1):.3f}s over {n} runs")

    t2 = Timer(lambda: load_file_through_disk_plyfile("example_data/example_pointcloud.ply.gz"))
    times2 = t2.repeat(repeat=n, number=1)
    print(f"plyfile disk: avg={np.mean(times2):.3f}s, std={np.std(times2):.3f}s over {n} runs")

    t3 = Timer(lambda: load_file_through_memory_plyfile("example_data/example_pointcloud.ply.gz"))
    times3 = t3.repeat(repeat=n, number=1)
    print(f"plyfile memory: avg={np.mean(times3):.3f}s, std={np.std(times3):.3f}s over {n} runs")

    print("finished test")
