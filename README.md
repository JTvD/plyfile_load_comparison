# Point Cloud Loading Test
This project addresses loading point clouds from memory and scalar fields from zipped point cloud files.

Point clouds are large files to store and move around. To help with this, some systems compress the files into GNU Zips (.gz). While smaller in size and safe to move, they have the downside that they must be unpacked before Open3D can read them.
At the time of writing, Open3D also lacks a way to load point clouds with additional scalar fields. This repository offers a solution to this challenge and compares it to Open3D in terms of speed.

## Data Format
Point clouds come in many file types and formats. In this example, the Polygon File Format (.ply) is used. This is a public standard that is well described and implemented in various libraries. For more information, see the [PLY file format on Wikipedia](https://en.wikipedia.org/wiki/PLY_(file_format)).
Instead of implementing it ourselves, we modified the python-plyfile (ply_reader.py) by Darsh Ranjan, source [plyfile repository](https://github.com/dranjan/python-plyfile), to support empty lines which we discovered in some of the header files. A pull request has been made to the plyfile repository to add support. Until this is merged, the fork can be used.


## Speed Test Results
The following table summarizes the average and standard deviation of loading times for different point cloud reading methods, measured over 10 runs:

| Method           | Average Time (s) | Std Dev (s) | Runs |
|------------------|------------------|-------------|------|
| Open3D disk      | 0.024            | 0.006       | 10   |
| plyfile disk     | 0.037            | 0.008       | 10   |
| plyfile memory   | 0.691            | 0.005       | 10   |

These results show that reading with Open3D from disk is the fastest, which is to be expected as it ignores the scalar fields. plyfile from disk returns a DataFrame with the scalar fields and an Open3D point cloud object.

The test clearly shows that unzipping on disk and removing the file is faster than unzipping in memory and streaming the data to plyfile.