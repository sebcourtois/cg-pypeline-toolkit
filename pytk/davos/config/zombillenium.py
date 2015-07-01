
class project:

    dir_name = "zombillenium"
    maya_version = 2016

    public_path = '//Diskstation/z2k/05_3D/{}/'.format(dir_name)
    private_path = '${{USERPROFILE}}/cg_projects/{}/'.format(dir_name)

    template_path = '//Diskstation/z2k/05_3D/{}/tool/template/'.format(dir_name)

    libraries = (
        "asset_lib",
        "shot_lib",
        "output_lib",
        )


class asset_lib:

    dir_name = "asset"

    public_path = project.public_path + dir_name
    private_path = project.private_path + dir_name

    asset_tree = {
        "{assetType}":
            {
            "{asset} -> root_dir":
                {
                "texture -> texture_dir":{},
                "ref -> ref_dir":{},
                "image -> image_dir":{},
                },
            },
        }


class shot_lib:

    dir_name = "shot"

    public_path = project.public_path + dir_name
    private_path = project.private_path + dir_name

    shot_tree = {
        "{sequence}":
            {
            "{shot} -> root_dir":
                {
                },
            },
        }

class output_lib:

    dir_name = "output"

    public_path = project.public_path + dir_name
    private_path = project.private_path + dir_name




