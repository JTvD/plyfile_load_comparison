from pathlib import Path
from shutil import copyfileobj
from plyfile import PlyData, PlyElement
import numpy as np
import pandas as pd
import open3d as o3d
import gzip


def unzip_ply(filename: Path) -> Path:
    """ Unzip ply file and save a copy of the unzipped file.
        Args:
            filename (Path): The path to the gzipped ply file.
        Returns:
            Path: The path to the unzipped ply file.
    """
    with gzip.open(filename, 'rb') as f_in:
        out_path = filename.with_suffix('')
        with open(out_path, 'wb') as f_out:
            copyfileobj(f_in, f_out)
    return out_path


def save_df_pointcloud(filename: str, df: pd.DataFrame,
                       pcd_object: o3d.geometry.PointCloud = None):
    """ Open3D cannot save/load pointclouds with 3D scalars fields, therefore we use plyfile.
        Args:
            filename (str): The path to save the ply file.
            df (pd.DataFrame): The dataframe containing scalarfield values for each point.
            pcd_object (o3d.geometry.PointCloud): The Open3D point cloud object to save.
    """
    if pcd_object is not None:
        # pcd object contains the points with colors, the dataframe the other scalar fields
        xyz = np.asarray(pcd_object.points)
        rgb = np.round(np.abs(np.asarray(pcd_object.colors)) * 255 * 255)
        rgb = rgb.astype(int)
        df_tuple = df.apply(tuple, axis=1).tolist()
        vertices = list(tuple(sub) + tuple(rgb[idx]) + df_tuple[idx] for idx, sub in enumerate(xyz.tolist()))

        # Create dictionary with datatypes
        dtype_list = [("x", "f4"), ("y", "f4"), ("z", "f4"), ("red", "u1"), ("green", "u1"), ("blue", "u1")]
        for colname in df.columns:
            dtype_list.append((colname, "f4"))
        vertices = np.array(vertices, dtype=dtype_list)
    else:
        # The dataframe contains the points, colors and scalar fields.
        dtype_dict = {"x": "f4", "y": "f4", "z": "f4", "red": "u1", "green": "u1", "blue": "u1"}
        for colname in df.columns:
            if colname not in dtype_dict:
                dtype_dict[colname] = "f4"
        vertices = df.to_records(index=False, column_dtypes=dtype_dict)
    ply = PlyData([PlyElement.describe(vertices, "vertex")], text=False)
    ply.write(filename)


def load_df_pointcloud(filename: str, return_pointcloud: bool = True,
                       df_drop: bool = True) -> tuple:
    """ Load pointcloud and scalarfields.
        Args:
            filename (str): The path to the ply file.
            return_pointcloud (bool): Whether to return the pointcloud object.
            df_drop (bool): Whether to drop the pointcloud columns from the dataframe.
        Returns:
            tuple: A tuple containing the dataframe and the pointcloud object (if requested).
    """

    plydata = PlyData.read(filename)
    df = pd.DataFrame(np.array(plydata["vertex"].data))

    # Check if 'face' element exists and is not empty, then add as new column
    if 'face' in plydata and len(plydata['face'].data) > 0:
        triangles = np.array(plydata['face'].data)
        tri_arr = np.stack(triangles['vertex_index'])
        df[['triangle1', 'triangle2', 'triangle3']] = pd.DataFrame(tri_arr, index=df.index[:len(tri_arr)]).astype('Int64')
    if return_pointcloud is True:
        if all(col in df.columns for col in ["triangle1", "triangle2", "triangle3", "red", "green", "blue"]):
            pcd = df_to_mesh(df)
            if df_drop:
                df.drop(["triangle1", "triangle2", "triangle3", "red", "green", "blue"], axis=1, inplace=True)
        elif all(col in df.columns for col in ["x", "y", "z", "red", "green", "blue"]):
            pcd = df_to_pointcloud(df)
            if df_drop:
                df.drop(["x", "y", "z", "red", "green", "blue"], axis=1, inplace=True)
        else:
            pcd = None
    else:
        pcd = None
    return (df, pcd)


def df_to_mesh(df: pd.DataFrame) -> o3d.geometry.TriangleMesh:
    """ Converts a dataframe to a triangle mesh.
        Requires columns: x, y, z, red, green, blue, triangle1, triangle2, triangle3
        Args:
            df (pd.DataFrame): The input dataframe.
        Returns:
            o3d.geometry.TriangleMesh: The resulting triangle mesh.
    """
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(np.array(df[["x", "y", "z"]].values.tolist()))
    mesh.vertex_colors = o3d.utility.Vector3dVector(np.array(df[["red", "green", "blue"]].values.tolist()) / 255)
    # Triangles: expects columns named triangle1, triangle2, triangle3 (indices)
    if all(col in df.columns for col in ["triangle1", "triangle2", "triangle3"]):
        sub_df = df.dropna(subset=['triangle1', 'triangle2', 'triangle3'])
        triangles = np.array(sub_df[["triangle1", "triangle2", "triangle3"]].values.tolist(), dtype=np.int32)
        mesh.triangles = o3d.utility.Vector3iVector(triangles)
    return mesh


def df_to_pointcloud(df: pd.DataFrame) -> o3d.geometry.PointCloud:
    """ Converts a dataframe to a pointcloud
        Requires columns: x, y, z, red, green, blue
        Args:
            df (pd.DataFrame): The input dataframe.
        Returns:
            o3d.geometry.PointCloud: The resulting point cloud.
       """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.array(df[["x", "y", "z"]].values.tolist()))
    pcd.colors = o3d.utility.Vector3dVector(np.array(df[["red", "green", "blue"]].values.tolist()) / 255)
    return pcd
