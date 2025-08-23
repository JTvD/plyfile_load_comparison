# Pointcloud loading test
Addresses loading pointclouds from memory & scalar fields from zipped pointcloud files.


Pointclouds are big files to store and move around, to help with this some systems compress the files into GNU Zips (.gz). While smaller in size and safe to move, they have the downside that they have to be unpacked before open3D can read them.
At the time of writing Open3D also lacks a way to load pointclouds with aditional scalarfields. This repository offers a solution to this challange and compares it to Open3D timewise.

## Data format
Pointclouds come in many file types and formats. In this example the Polygon File Format (.ply) type is used. This is a public standard that is well described and implemented in various libraries. For more information, see the [PLY file format on Wikipedia](https://en.wikipedia.org/wiki/PLY_(file_format)).
Instead of implementing it ourselves, we modified the python-plyfile (ply_reader.py) by Darsh Ranjan, source [plyfile repositoy](https://github.com/dranjan/python-plyfile) To support empty lines which we discovered in some of the header files. A pull request is made to the plyfile repository to add support. Untill this is merged the fork can be used.


## Speed Test Results
The following table summarizes the average and standard deviation of loading times for different point cloud reading methods, measured over 10 runs:

| Method           | Average Time (s) | Std Dev (s) | Runs |
|------------------|------------------|-------------|------|
| open3D disk      | 0.024            | 0.006       | 10   |
| plyfile disk     | 0.037            | 0.008       | 10   |
| plyfile memory   | 0.691            | 0.005       | 10   |

These results show that reading with Open3D from disk is the fastest, which is to be expected as it ignored the scalar fields. plyfile from disk returns a dataframe with the scalarfields and an open3D pointcloud object. 

The test clearly shows that unzipping on disk and removing the file is faster than unzipping in memory and streaming the data to plyfile.