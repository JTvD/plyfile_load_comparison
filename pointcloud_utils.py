import numpy as np
import pandas as pd
import open3d as o3d
from plyfile import PlyData, PlyElement


def save_df_pointcloud(filename: str, df: pd.DataFrame,
                       pcd_object: o3d.geometry.PointCloud = None):
    """***Open3D cannot save/load pointclouds with 3D scalars fields, therefore we use plyfile ***"""
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
    """Load pointcloud from disk, optional returns pointcloud in the dataframe or as pointcloud"""
    plydata = PlyData.read(filename)
    df = pd.DataFrame(np.array(plydata["vertex"].data))

    if return_pointcloud is True:
        # Using a view to convert an array to a recarray:
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


def df_to_mesh(df: pd.DataFrame, df_drop: list) -> o3d.geometry.TriangleMesh:
    """Converts a dataframe to a triangle mesh.
       Requires columns: x, y, z, red, green, blue, triangle1, triangle2, triangle3
       """
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(np.array(df[["x", "y", "z"]].values.tolist()))
    mesh.vertex_colors = o3d.utility.Vector3dVector(np.array(df[["red", "green", "blue"]].values.tolist()) / 255)
    # Triangles: expects columns named triangle1, triangle2, triangle3 (indices)
    if all(col in df.columns for col in ["triangle1", "triangle2", "triangle3"]):
        triangles = np.array(df[["triangle1", "triangle2", "triangle3"]].values.tolist(), dtype=np.int32)
        mesh.triangles = o3d.utility.Vector3iVector(triangles)
    return mesh


def df_to_pointcloud(df: pd.DataFrame) -> o3d.geometry.PointCloud:
    """Converts a dataframe to a pointcloud
       Requires columns: x, y, z, red, green, blue
       """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.array(df[["x", "y", "z"]].values.tolist()))
    pcd.colors = o3d.utility.Vector3dVector(np.array(df[["red", "green", "blue"]].values.tolist()) / 255)
    return pcd
