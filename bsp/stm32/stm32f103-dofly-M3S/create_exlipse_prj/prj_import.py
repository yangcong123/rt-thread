import os
import textwrap
import json
import shutil
import xmltodict


def do_copy_file(src, dst):
    # check source file
    if not os.path.exists(src):
        return

    path = os.path.dirname(dst)
    # mkdir if path not exist
    if not os.path.exists(path):
        os.makedirs(path)

    shutil.copy2(src, dst)


def do_copy_folder(src_dir, dst_dir, ignore=None):
    import shutil
    # check source directory
    if not os.path.exists(src_dir):
        return

    try:
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
    except:
        print('Deletes folder: %s failed.' % dst_dir)
        return

    shutil.copytree(src_dir, dst_dir, ignore=ignore)


def get_mdk_prj_info(path):
    with open(path, "r") as f:
        s = f.read()
    data = json.dumps(xmltodict.parse(s), indent=4)
    data_get = json.loads(data)["Project"]

    with open("mdk_info_from_project.json", "w") as f:
        f.write(data)

    info_mdk = dict()
    info_mdk["prj_name"] = data_get["Targets"]["Target"]["TargetName"]
    info_mdk["mcu_type"] = data_get["Targets"]["Target"]["TargetOption"]["TargetCommonOption"]["Device"]
    info_mdk["groups"] = data_get["Targets"]["Target"]["Groups"]["Group"]
    info_mdk["include_path"] = data_get["Targets"]["Target"]["TargetOption"]["TargetArmAds"]["Cads"]["VariousControls"][
        "IncludePath"]

    # print(data_get["SchemaVersion"])
    # print(data_get["Targets"]["Target"]["TargetOption"]["TargetCommonOption"]["Device"])
    # print(data_get["Targets"]["Target"]["TargetOption"]["TargetCommonOption"]["AfterMake"])
    # print(data_get["Targets"]["Target"]["TargetOption"]["TargetArmAds"]["Cads"]["VariousControls"]["Define"])
    # print(data_get["Targets"]["Target"]["TargetOption"]["TargetArmAds"]["LDads"]["ScatterFile"])
    # print()
    return info_mdk


def studio_prj_update(stdio_prj_path, mdk_info):
    with open(stdio_prj_path, "r") as f:
        s = f.read()
    data = json.dumps(xmltodict.parse(s), indent=4)
    data_get = json.loads(data)

    # with open("read_info_from_eclipse_project.json", "w") as f:
    #     f.write(data)

    data_get["projectDescription"]["linkedResources"]["link"].clear()
    # print(data_get["linkedResources"]["link"])

    for group in mdk_info["groups"]:
        creat_group_dict = dict()
        creat_group_dict["name"] = group["GroupName"]
        creat_group_dict["type"] = "2"
        creat_group_dict["locationURI"] = "virtual:/virtual"
        data_get["projectDescription"]["linkedResources"]["link"].append(creat_group_dict)

        # add group dir to new project
        for file in group["Files"]:
            group_file_name = group["GroupName"] + "\\" + file["File"]["FileName"]
            file_path = os.path.join(os.path.dirname(stdio_prj_path), "..\\" + file["File"]["FilePath"])

            # add files to group
            creat_group_file_dict = dict()
            creat_group_file_dict["name"] = group_file_name
            creat_group_file_dict["type"] = "1"
            creat_group_file_dict["location"] = file_path.replace("\\", "/")
            data_get["projectDescription"]["linkedResources"]["link"].append(creat_group_file_dict)

    new_xml_str = xmltodict.unparse(data_get, pretty=True)  # 这里直接放dict对象，不要放json字符串
    print(new_xml_str)

    with open(".project", "w") as f:
        f.write(new_xml_str)

def studio_prj_config_update(configuration_path, mdk_info):
    with open(configuration_path, "r") as f:
        s = f.read()
    data = json.dumps(xmltodict.parse(s), indent=4)
    data_get = json.loads(data)

    with open("read_info_from_eclipse_config_project.json", "w") as f:
        f.write(data)

 storageModule cproject configuration folderInfo  toolChain tool option   listOptionValue

def main():
    mdk_info = get_mdk_prj_info(os.path.join(os.getcwd(), "../project.uvprojx"))
    studio_prj_update(os.path.join(os.getcwd(), ".project"), mdk_info)
    studio_prj_config_update(os.path.join(os.getcwd(), ".cproject"), mdk_info)


if __name__ == "__main__":
    main()
